#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных.
Создаёт все таблицы.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_database


if __name__ == "__main__":
    print("🚀 Инициализация базы данных...")
    init_database()
    print("✅ Готово! Теперь можно подключаться из DBeaver.")