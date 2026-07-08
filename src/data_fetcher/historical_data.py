"""Загрузчик исторических данных."""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
from loguru import logger

from src.api import FinamClient
from src.database import get_db_session, Ticker, Candle


class HistoricalDataFetcher:
    """Загрузчик исторических данных с сохранением в БД."""

    def __init__(self):
        self.client = FinamClient()

    async def __aenter__(self):
        await self.client.connect()
        return self

    async def __aexit__(self, *args):
        await self.client.disconnect()

    async def fetch_stock_candles(
        self,
        symbol: str,
        mic: str = "XNGS",
        timeframe: str = "1m",
        days: int = 30,
        save_to_db: bool = True,
    ) -> pd.DataFrame:
        """Загружает исторические свечи через Trade API."""
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)

        logger.info(f"Загрузка {symbol}@{mic} ({timeframe}) за {days} дней...")

        try:
            df = await self.client.get_candles(
                symbol=symbol,
                mic=mic,
                timeframe=timeframe,
                from_date=from_date,
                to_date=to_date,
            )
        except Exception as e:
            logger.error(f"Ошибка загрузки {symbol}: {e}")
            return pd.DataFrame()

        if save_to_db and not df.empty:
            self._save_to_db(symbol, mic, timeframe, df)

        return df

    async def fetch_multiple_stocks(
        self,
        symbols: List[str],
        mic: str = "XNGS",
        timeframe: str = "1m",
        days: int = 30,
    ) -> dict[str, pd.DataFrame]:
        """Загружает данные для нескольких тикеров."""
        tasks = [self.fetch_stock_candles(sym, mic, timeframe, days) for sym in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Ошибка загрузки {symbol}: {result}")
            elif not result.empty:
                data[symbol] = result

        return data
    
    async def fetch_option_chain(self, symbol: str, mic: str = None) -> pd.DataFrame:
        """Получить опционный чейн через FinamClient"""
        return await self.client.fetch_option_chain(symbol, mic)

    def _save_to_db(self, symbol, mic, timeframe, df):
        """Сохраняет свечи в БД по одной с обработкой ошибок."""
        session = get_db_session()
        saved = 0
        try:
            ticker = session.query(Ticker).filter_by(symbol=symbol, exchange=mic).first()
            if not ticker:
                ticker = Ticker(symbol=symbol, name=symbol, exchange=mic)
                session.add(ticker)
                session.commit()

            for idx, row in df.iterrows():
                try:
                    candle_time = pd.to_datetime(str(idx)).to_pydatetime().replace(tzinfo=None)
                    candle = Candle(
                        ticker_id=ticker.id,
                        timeframe=timeframe,
                        open_price=float(row["open"]),
                        high_price=float(row["high"]),
                        low_price=float(row["low"]),
                        close_price=float(row["close"]),
                        volume=int(float(row["volume"])),
                        candle_time=candle_time,
                    )
                    session.add(candle)
                    session.commit()
                    saved += 1
                except Exception as e:
                    session.rollback()
                    logger.warning(f"Skip candle {idx}: {e}")
                    continue

            logger.info(f"Saved {saved}/{len(df)} candles for {symbol}")
        except Exception as e:
            session.rollback()
            logger.error(f"DB error: {e}")
        finally:
            session.close()


if __name__ == "__main__":
    async def test():
        async with HistoricalDataFetcher() as f:
            df = await f.fetch_stock_candles("CABA", mic="XNGS", timeframe="1m", days=7)
            print(f"Загружено: {len(df)}")
            print(df.head())

    asyncio.run(test())