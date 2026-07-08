#!/usr/bin/env python3
"""
Скрипт для загрузки исторических данных.
Пример:
    python scripts/fetch_data.py --symbol AAPL --days 30 --timeframe 1m
    python scripts/fetch_data.py --symbols AAPL,MSFT,TSLA --days 365
"""

import sys
import os
import asyncio
import argparse
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import HistoricalDataFetcher
from src.utils import setup_logger

logger = setup_logger()


async def main():
    parser = argparse.ArgumentParser(description="Загрузка исторических данных с Finam")
    parser.add_argument("--symbol", type=str, help="Тикер акции")
    parser.add_argument("--symbols", type=str, help="Список тикеров через запятую")
    parser.add_argument("--mic", type=str, default="XNGS", help="MIC код биржи")
    parser.add_argument("--timeframe", type=str, default="1m")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--options", action="store_true", help="Загрузить опционный чейн")
    parser.add_argument("--min-strike", type=float, default=0, help="Минимальный страйк")
    parser.add_argument("--max-strike", type=float, default=float('inf'), help="Максимальный страйк")
    parser.add_argument("--option-types", type=str, default="ALL", choices=["CALL", "PUT", "ALL"], help="Типы опционов")
    
    args = parser.parse_args()
    
    async with HistoricalDataFetcher() as fetcher:
        if args.symbols:
            symbols = [s.strip().upper() for s in args.symbols.split(",")]
            logger.info(f"Загрузка данных для: {symbols}")
            data = await fetcher.fetch_multiple_stocks(symbols=symbols, board=args.board,
                                                        timeframe=args.timeframe, days=args.days)
            for sym, df in data.items():
                logger.info(f"{sym}: {len(df)} записей")
        
        elif args.symbol:
            symbol = args.symbol.upper()
            logger.info(f"Загрузка данных для {symbol}")
            df = await fetcher.fetch_stock_candles(symbol=symbol, mic=args.mic,
                                                    timeframe=args.timeframe, days=args.days)
            logger.info(f"Загружено {len(df)} записей для {symbol}")
            print(df.head())
            
            if args.options:
                logger.info(f"Загрузка опционного чейна для {symbol}")
                opt_df = await fetcher.fetch_option_chain(symbol, args.mic)

                # Фильтрация
                if args.min_strike > 0 or args.max_strike < float('inf'):
                    opt_df = opt_df[(opt_df['strike'] >= args.min_strike) & (opt_df['strike'] <= args.max_strike)]
                    logger.info(f"После фильтрации страйков {args.min_strike}-{args.max_strike}: {len(opt_df)} опционов")
                if args.option_types != "ALL":
                    opt_df = opt_df[opt_df['type'] == args.option_types]
                    logger.info(f"После фильтрации типа {args.option_types}: {len(opt_df)} опционов")
                logger.info(f"Загружено {len(opt_df)} опционов")
                print(opt_df[['symbol', 'type', 'strike', 'expiration_date']].to_string())
                # Сохранить в БД
                await save_options_to_db(opt_df, symbol)
        else:
            logger.error("Укажите --symbol или --symbols")
            parser.print_help()

async def save_options_to_db(opt_df: pd.DataFrame, underlying_symbol: str):
    """Сохранить опционы в базу данных"""
    from src.database.models import Option, Ticker, get_db_session
    from sqlalchemy import select
    
    session = get_db_session()
    try:
        # Найти underlying ticker
        result = session.execute(select(Ticker).where(Ticker.symbol == underlying_symbol))
        ticker = result.scalar_one_or_none()
        
        if not ticker:
            logger.error(f"Тикер {underlying_symbol} не найден в БД")
            return
        
        saved_count = 0
        for _, row in opt_df.iterrows():
            # Проверить существование
            result = session.execute(select(Option).where(Option.symbol == row['symbol']))
            existing = result.scalar_one_or_none()
            
            if existing:
                # Обновить
                existing.strike = row['strike']
                existing.expiration_date = row['expiration_date']
                existing.is_active = True
            else:
                # Создать новый
                option = Option(
                    underlying_ticker_id=ticker.id,
                    symbol=row['symbol'],
                    option_type=row['type'],
                    strike=row['strike'],
                    expiration_date=row['expiration_date'],
                )
                session.add(option)
                saved_count += 1
        
        session.commit()
        logger.info(f"Сохранено/обновлено {saved_count} опционов в БД")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка сохранения опционов: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    asyncio.run(main())