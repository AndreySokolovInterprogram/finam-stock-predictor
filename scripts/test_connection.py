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
        print("\n📋 1. Проверка JWT...")
        try:
            jwt = await client._client.access_tokens.get_jwt_token_details()
            print(f"   ✅ JWT получен: {jwt}")
        except Exception as e:
            print(f"   ❌ Ошибка JWT: {e}")
        
        print("\n📋 2. Проверка аккаунта...")
        try:
            account = await client.get_account_info()
            print(f"   ✅ Аккаунт: {account}")
        except Exception as e:
            print(f"   ❌ Ошибка аккаунта: {e}")
    
    print("\n🎉 Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(test_connection())