# 🧠 PROJECT CONTEXT — Finam Stock Predictor

&gt; 📌 Для AI-ассистента: Если чат закончился, скопируй этот файл в новый чат.

---

## 📋 Информация о проекте

| Параметр | Значение |
|----------|----------|
| **Название** | Finam Stock Predictor |
| **Язык** | Python 3.11+ |
| **IDE** | VS Code |
| **База данных** | PostgreSQL 16 |
| **GUI БД** | DBeaver |
| **API** | Finam Trade API (JWT) + Finam Export API (CSV) |
| **ОС** | Windows 10/11 |
| **Репозиторий** | https://github.com/AndreySokolovInterprogram/finam-stock-predictor |

---

## 🎯 Цель

1. Получать котировки акций и опционов через Finam API
2. Хранить в PostgreSQL
3. Анализировать нейросетью
4. Предсказывать движение акций
5. Торговать автоматически

---

## 📊 Данные

- **Рынки:** NYSE, NASDAQ, CBOE
- **Инструменты:** Акции + Опционы (страйки, греки, IV)
- **Таймфрейм:** Минутные (1m)
- **Горизонт предсказания:** Задаваемый

---

## 🔐 API Finam — Статус

| Параметр | Значение |
|----------|----------|
| **Токен** | ✅ Получен и работает |
| **JWT** | ✅ Получается автоматически через `finam-trade-api` |
| **Account ID** | `2045914` (без "К№-" префикса) |
| **Base URL** | `https://api.finam.ru` |

### ⚠️ Известные проблемы с API:
- **Библиотека `finam-trade-api`** имеет баг: `positions` требует поле `quantity`, которого нет в ответе сервера. Это не критично — JWT и account работают.
- **Trade API** не предоставляет исторические данные (только real-time).
- **Export API** (`https://export.finam.ru`) используется для исторических OHLCV данных.

---

## ✅ Сделано

- [x] Структура проекта
- [x] Модели БД (5 таблиц: tickers, candles, options, option_candles, predictions)
- [x] API клиент с JWT-аутентификацией (через `finam-trade-api`)
- [x] Finam Export API клиент (CSV загрузка)
- [x] Загрузчик данных (HistoricalDataFetcher)
- [x] Логирование (loguru)
- [x] GitHub репозиторий
- [x] `.gitignore` (защита секретов)
- [x] PostgreSQL установлена
- [x] DBeaver подключён
- [x] База `finam_predictor` создана
- [x] Таблицы инициализированы
- [x] Токен Finam получен
- [x] JWT работает
- [x] Account ID найден (2045914)

---

## ⬜ Следующие шаги

- [ ] Исправить `src/data_fetcher/__init__.py` (добавить экспорт HistoricalDataFetcher)
- [ ] Исправить `src/api/finam_client.py` (убрать несуществующие методы .securities, .market_data)
- [ ] Протестировать загрузку данных через Export API
- [ ] Data pipeline (регулярная загрузка)
- [ ] Технические индикаторы (фичи для нейросети)
- [ ] Нейросеть (LSTM/Transformer)
- [ ] Backtesting
- [ ] Автоторговля

---

## 📁 Структура проекта (ключевые файлы)
finam-stock-predictor/
├── .env                          # Токены и пароли (НЕ в git!)
├── config/settings.py            # Конфигурация
├── src/
│   ├── api/finam_client.py      # API клиент (JWT + Export)
│   ├── database/models.py        # SQLAlchemy модели
│   ├── data_fetcher/             # ⚠️ init.py пустой — нужен экспорт
│   └── utils/logger.py           # Логирование
├── scripts/
│   ├── init_db.py                # Инициализация БД
│   ├── test_connection.py        # Тест API (JWT + аккаунт)
│   └── fetch_data.py             # Загрузка данных
└── PROJECT_CONTEXT.md            # Этот файл


---

## 🔧 Известные баги

| Баг | Где | Решение |
|-----|-----|---------|
| `__init__.py` пустой | `src/data_fetcher/__init__.py` | Добавить `from .historical_data import HistoricalDataFetcher` |
| Несуществующие методы | `src/api/finam_client.py` | Убрать `.securities`, `.market_data`, `.get_option_chain`. Использовать только Export API для данных |
| Pydantic validation error | `finam-trade-api` library | Баг в библиотеке, игнорировать или обновить |

---

## 🚀 Быстрый старт (если чат новый)

```bash
# 1. Активировать venv
venv\Scripts\activate

# 2. Проверить JWT
python scripts/test_connection.py

# 3. Загрузить данные (после исправления багов)
python scripts/fetch_data.py --symbol AAPL --days 7 --timeframe 1d

🔐 Безопасность
.env в .gitignore (токены не утекают)
Пароль PostgreSQL: 1289 (локально)
Account ID: 2045914


---

## 🔧 Исправления кода (сразу сделай)

### 1. `src/data_fetcher/__init__.py`

Открой файл и вставь:

```python
from src.data_fetcher.historical_data import HistoricalDataFetcher

__all__ = ["HistoricalDataFetcher"]

