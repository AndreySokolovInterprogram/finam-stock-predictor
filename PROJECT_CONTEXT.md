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
| **API** | Finam Trade API (JWT) |
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
| **JWT** | ✅ Получается через POST /v1/sessions |
| **Account ID** | `2045914` |
| **Base URL** | `https://api.finam.ru` |

### Endpoints:

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/v1/sessions` | POST | Получение JWT |
| `/v1/instruments/{symbol}@{mic}/bars` | GET | Свечи акций (timeframe=1 для M1) |
| `/v1/assets/{symbol}@{mic}/options` | GET | Цепочка опционов (нужна дата экспирации) |

### ⚠️ Известные проблемы:
- **Rate limit:** API не выдерживает &gt;1 запроса/сек, нужен `time.sleep(2)`
- **Таймфрейм:** только M1 (1), дневки не поддерживаются
- **Опционы:** требуется точная дата экспирации (year/month/day)

---

## ✅ Сделано

- [x] Структура проекта
- [x] Модели БД (5 таблиц: tickers, candles, options, option_candles, predictions)
- [x] API клиент с JWT (FinamClient)
- [x] Загрузчик данных (HistoricalDataFetcher)
- [x] Логирование (loguru)
- [x] GitHub репозиторий
- [x] `.gitignore`
- [x] PostgreSQL + DBeaver
- [x] Токен Finam получен, JWT работает
- [x] **Получены свечи CABA@XNGS за 7 дней: 1314 минутных свечей**
- [x] **Сохранены в PostgreSQL**
- [x] **Найден endpoint опционов: `/v1/assets/{symbol}@mic/options`**
- [x] **Получены 138 опционов CABA (7 экспираций, страйки 0.5-7.5)**
- [x] **Получены исторические свечи для отдельных опционов**
- [x] Исправлен парсинг candle_time (Timestamp → datetime)
- [x] Исправлен парсинг volume (dict → float → int)
- [x] fetch_data.py работает с `--mic` параметром

---

## ⬜ Следующие шаги

- [ ] Получить котировки опционов CABA (страйки 2-7, Call+Put, 7 дней истории)
- [ ] Доработать БД для хранения опционов (таблица option_candles)
- [ ] Автоматическое определение дат экспирации опционов
- [ ] Data pipeline: регулярная загрузка акций + опционов
- [ ] Технические индикаторы (фичи для нейросети)
- [ ] Нейросеть (LSTM/Transformer)
- [ ] Backtesting
- [ ] Автоторговля

---

## 📁 Структура проекта
finam-stock-predictor/
├── .env                          # Токены (НЕ в git!)
├── config/settings.py            # Конфигурация
├── src/
│   ├── api/
│   │   ├── init.py
│   │   └── finam_client.py       # FinamClient + FinamClientSync
│   ├── data_fetcher/
│   │   ├── init.py
│   │   └── historical_data.py    # HistoricalDataFetcher
│   ├── database/
│   │   ├── init.py
│   │   └── models.py             # SQLAlchemy модели
│   └── utils/
│       └── logger.py
├── scripts/
│   ├── fetch_data.py             # Загрузка свечей (--symbol --mic --days --timeframe)
│   ├── init_db.py
│   └── test_connection.py
└── PROJECT_CONTEXT.md            # Этот файл

---

## 🔧 Известные баги

| Баг | Где | Решение |
|-----|-----|---------|
| API timeout при массовых запросах | Finam API | `time.sleep(2)` между запросами |
| Таймфрейм 1d не работает | Finam Trade API | Использовать только M1 (1) |
| psycopg2 InvalidSchemaName | historical_data.py | `pd.to_datetime(str(idx)).to_pydatetime().replace(tzinfo=None)` |

---

## 🚀 Быстрый старт

```bash
# Активировать venv
venv\Scripts\activate

# Проверить JWT
python scripts/test_connection.py

# Загрузить свечи акций
python scripts/fetch_data.py --symbol CABA --mic XNGS --days 7 --timeframe 1m