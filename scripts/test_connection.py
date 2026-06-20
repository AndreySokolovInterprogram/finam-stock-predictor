#!/usr/bin/env python3
"""
Скрипт для проверки подключения к Finam API.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api import FinamClient
from src.utils import setup_logger

logger = setup_logger()


async def test_connection():
    print("🔌 Тестирование подключения к Finam Trade API...")
    
    async with FinamClient() as client:
        print("\n📋 1. Проверка аккаунта...")
        try:
            account = await client.get_account_info()
            print(f"   ✅ Аккаунт доступен")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print("\n📈 2. Получение списка инструментов (US)...")
        try:
            securities = await client.get_securities(board="US")
            print(f"   ✅ Найдено {len(securities)} инструментов")
            if securities:
                print(f"   Первые 5: {[s.get('symbol') for s in securities[:5]]}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print("\n🕯️ 3. Получение свечей AAPL (1d, последние 5)...")
        try:
            candles = await client.get_candles(board="US", symbol="AAPL", timeframe="1d", count=5)
            print(f"   ✅ Получено {len(candles)} свечей")
            for c in candles:
                print(f"   {c.time.date()}: O={c.open_price:.2f} H={c.high_price:.2f} L={c.low_price:.2f} C={c.close_price:.2f} V={c.volume}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print("\n📊 4. Получение опционного чейна AAPL...")
        try:
            options = await client.get_option_chain("US", "AAPL")
            print(f"   ✅ Получено {len(options)} опционов")
            if options:
                opt = options[0]
                print(f"   Пример: {opt.symbol} | {opt.option_type} | Strike={opt.strike} | Exp={opt.expiration.date()}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    print("\n🎉 Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(test_connection())