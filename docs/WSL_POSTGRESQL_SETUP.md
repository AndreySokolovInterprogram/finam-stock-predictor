# 🔗 WSL → Windows PostgreSQL Connection Guide

&gt; 📌 Автоматически сгенерирован: 2026-07-07
&gt; 📌 Проект: Finam Stock Predictor

## ⚡ Быстрый старт (каждый день)

```bash
# 1. Проверить что WSL PostgreSQL остановлен
sudo service postgresql status  # должен быть inactive

# 2. Проверить подключение
python3 -c "import psycopg2; conn = psycopg2.connect(host='172.26.48.1', port=5432, dbname='finam_predictor', user='postgres', password='1289'); print('OK'); conn.close()"