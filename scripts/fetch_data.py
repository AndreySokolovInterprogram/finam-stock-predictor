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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import HistoricalDataFetcher
from src.utils import setup_logger

logger = setup_logger()


async def main():
    parser = argparse.ArgumentParser(description="Загрузка исторических данных с Finam")
    parser.add_argument("--symbol", type=str, help="Тикер акции")
    parser.add_argument("--symbols", type=str, help="Список тикеров через запятую")
    parser.add_argument("--board", type=str, default="US")
    parser.add_argument("--timeframe", type=str, default="1m")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--options", action="store_true", help="Загрузить опционный чейн")
    
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
            df = await fetcher.fetch_stock_candles(symbol=symbol, board=args.board,
                                                    timeframe=args.timeframe, days=args.days)
            logger.info(f"Загружено {len(df)} записей для {symbol}")
            print(df.head())
            
            if args.options:
                logger.info(f"Загрузка опционного чейна для {symbol}")
                opt_df = await fetcher.fetch_option_chain(symbol, args.board)
                logger.info(f"Загружено {len(opt_df)} опционов")
                print(opt_df.head())
        else:
            logger.error("Укажите --symbol или --symbols")
            parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())