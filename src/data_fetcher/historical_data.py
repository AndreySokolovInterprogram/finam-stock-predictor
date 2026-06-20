"""
Модуль для загрузки и сохранения исторических данных.
Обёртка над API клиентом с сохранением в БД.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
from loguru import logger

from src.api import FinamClient, FinamExportClient
from src.database import get_db_session, Ticker, Candle, Option, OptionCandle
from config import DATA_CONFIG


class HistoricalDataFetcher:
    """Загрузчик исторических данных с сохранением в БД."""
    
    def __init__(self):
        self.client = FinamClient()
        self.export_client = FinamExportClient()
    
    async def __aenter__(self):
        await self.client.connect()
        self.export_session = await self.export_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()
        await self.export_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def fetch_stock_candles(self, symbol: str, board: str = "US",
                                  timeframe: str = "1m", days: int = 30,
                                  save_to_db: bool = True) -> pd.DataFrame:
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=days)
        
        logger.info(f"Загрузка {symbol} ({timeframe}) за {days} дней...")
        
        try:
            df = await self.export_client.download_history(
                symbol=symbol, market=board, period=timeframe,
                from_date=from_date, to_date=to_date)
        except Exception as e:
            logger.warning(f"Export API не сработал: {e}. Пробуем Trade API...")
            df = await self.client.get_candles_to_dataframe(
                board=board, symbol=symbol, timeframe=timeframe,
                from_date=from_date, to_date=to_date)
        
        if save_to_db and not df.empty:
            self._save_candles_to_db(symbol, board, timeframe, df)
        return df
    
    async def fetch_multiple_stocks(self, symbols: List[str], board: str = "US",
                                    timeframe: str = "1m", days: int = 30) -> dict[str, pd.DataFrame]:
        tasks = [self.fetch_stock_candles(sym, board, timeframe, days) for sym in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Ошибка загрузки {symbol}: {result}")
            elif not result.empty:
                data[symbol] = result
        return data
    
    async def fetch_option_chain(self, underlying_symbol: str, board: str = "US",
                                 save_to_db: bool = True) -> pd.DataFrame:
        options = await self.client.get_option_chain(board, underlying_symbol)
        if not options:
            logger.warning(f"Опционы для {underlying_symbol} не найдены")
            return pd.DataFrame()
        
        df = pd.DataFrame([{
            "symbol": opt.symbol, "type": opt.option_type, "strike": opt.strike,
            "expiration": opt.expiration, "bid": opt.bid, "ask": opt.ask,
            "last_price": opt.last_price, "volume": opt.volume,
            "open_interest": opt.open_interest, "iv": opt.implied_volatility,
            "delta": opt.delta, "gamma": opt.gamma, "theta": opt.theta, "vega": opt.vega,
        } for opt in options])
        
        if save_to_db:
            self._save_options_to_db(underlying_symbol, board, df)
        return df
    
    def _save_candles_to_db(self, symbol: str, board: str, timeframe: str, df: pd.DataFrame):
        session = get_db_session()
        try:
            ticker = session.query(Ticker).filter_by(symbol=symbol, exchange=board).first()
            if not ticker:
                ticker = Ticker(symbol=symbol, name=symbol, exchange=board)
                session.add(ticker)
                session.commit()
            
            for idx, row in df.iterrows():
                candle = Candle(
                    ticker_id=ticker.id, timeframe=timeframe,
                    open_price=row["open"], high_price=row["high"],
                    low_price=row["low"], close_price=row["close"],
                    volume=int(row["volume"]),
                    candle_time=idx.to_pydatetime() if hasattr(idx, 'to_pydatetime') else idx,
                )
                session.merge(candle)
            session.commit()
            logger.info(f"Сохранено {len(df)} свечей для {symbol} в БД")
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка сохранения в БД: {e}")
        finally:
            session.close()
    
    def _save_options_to_db(self, underlying_symbol: str, board: str, df: pd.DataFrame):
        session = get_db_session()
        try:
            underlying = session.query(Ticker).filter_by(symbol=underlying_symbol, exchange=board).first()
            if not underlying:
                underlying = Ticker(symbol=underlying_symbol, name=underlying_symbol, exchange=board)
                session.add(underlying)
                session.commit()
            
            for _, row in df.iterrows():
                option = Option(
                    underlying_ticker_id=underlying.id, symbol=row["symbol"],
                    option_type=row["type"], strike=row["strike"],
                    expiration_date=row["expiration"], bid=row.get("bid"),
                    ask=row.get("ask"), last_price=row.get("last_price"),
                    volume=row.get("volume"), open_interest=row.get("open_interest"),
                    implied_volatility=row.get("iv"), delta=row.get("delta"),
                    gamma=row.get("gamma"), theta=row.get("theta"), vega=row.get("vega"),
                )
                session.merge(option)
            session.commit()
            logger.info(f"Сохранено {len(df)} опционов для {underlying_symbol} в БД")
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка сохранения опционов в БД: {e}")
        finally:
            session.close()


if __name__ == "__main__":
    async def test_fetcher():
        async with HistoricalDataFetcher() as fetcher:
            df = await fetcher.fetch_stock_candles("AAPL", board="US", timeframe="1d", days=30)
            print(f"Загружено {len(df)} свечей AAPL")
            print(df.head())
    asyncio.run(test_fetcher())