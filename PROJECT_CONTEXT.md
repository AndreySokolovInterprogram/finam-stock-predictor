# 🧠 PROJECT CONTEXT — Finam Stock Predictor

> 📌 Для AI-ассистента: Если чат закончился, скопируй этот файл в новый чат.

---

## 📋 Информация о проекте

| Параметр | Значение |
|----------|----------|
| **Название** | Finam Stock Predictor |
| **Язык** | Python 3.11+ |
| **IDE** | VS Code |
| **База данных** | PostgreSQL 15+ |
| **GUI БД** | DBeaver |
| **API** | Finam Trade API + Export API |
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

## ✅ Сделано

- [x] Структура проекта
- [x] Модели БД (5 таблиц: tickers, candles, options, option_candles, predictions)
- [x] API клиент (Finam Trade + Export)
- [x] Загрузчик данных
- [x] Логирование
- [x] GitHub репозиторий
- [x] .gitignore
- [x] PostgreSQL установлена
- [x] DBeaver подключён
- [x] База finam_predictor создана
- [x] Таблицы инициализированы

---

## ⬜ Следующие шаги

- [ ] Получить токен Finam
- [ ] Тест API (`python scripts/test_connection.py`)
- [ ] Загрузить первые данные
- [ ] Data pipeline
- [ ] Технические индикаторы
- [ ] Нейросеть
- [ ] Backtesting
- [ ] Автоторговля

---

## 🔐 Безопасность

- .env в .gitignore (токены не утекают)
- Пароль PostgreSQL: 1289 (локально)

---

*Версия: 0.1.0 | Дата: 2026-06-21*