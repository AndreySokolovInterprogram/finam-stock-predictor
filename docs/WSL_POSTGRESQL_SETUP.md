# 🔗 WSL → Windows PostgreSQL Connection Guide

&gt; 📌 Автоматически сгенерирован: 2026-07-07
&gt; 📌 Проект: Finam Stock Predictor

## ⚡ Быстрый старт (каждый день)

```bash
# 1. Проверить что WSL PostgreSQL остановлен
sudo service postgresql status  # должен быть inactive

# 2. Проверить подключение
python3 -c "import psycopg2; conn = psycopg2.connect(host='172.26.48.1', port=5432, dbname='finam_predictor', user='postgres', password='1289'); print('OK'); conn.close()"

🛠️ Автоматическое исправление
Если подключение перестало работать (например, после перезагрузки):
bash
python3 scripts/fix_wsl_postgres.py
Этот скрипт автоматически:
Проверит подключение
Остановит WSL PostgreSQL если он запустился
Отключит Hyper-V firewall
Настроит port proxy
Обновит .env
⚠️ Важно: Hyper-V Firewall
Ключевая проблема: Windows 11 имеет Hyper-V firewall, который блокирует трафик WSL2 → Windows по умолчанию.
Решение (выполнить один раз в PowerShell админ):
powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Enabled False
Проверить статус:
powershell
Get-NetFirewallHyperVVMSetting -PolicyStore ActiveStore
🔧 Полная настройка (один раз)
1. Найти правильную версию PostgreSQL
В PowerShell (админ):
powershell
Get-NetTCPConnection -LocalPort 5432 | Select-Object LocalAddress, OwningProcess, @{Name="Path";Expression={(Get-Process -Id $_.OwningProcess).Path}}
2. Настроить pg_hba.conf
Открыть конфиг для правильной версии (например 17):
powershell
code "C:\Program Files\PostgreSQL\17\data\pg_hba.conf"
Добавить в конец:
plain
host    all             all             0.0.0.0/0               scram-sha-256
3. Настроить postgresql.conf
powershell
code "C:\Program Files\PostgreSQL\17\data\postgresql.conf"
Найти listen_addresses и изменить на:
plain
listen_addresses = '*'
4. Перезапустить PostgreSQL
powershell
Restart-Service postgresql-x64-17
5. Создать Port Proxy
powershell
netsh interface portproxy add v4tov4 listenport=5432 listenaddress=0.0.0.0 connectport=5432 connectaddress=127.0.0.1
6. Создать Firewall Rule
powershell
New-NetFirewallRule -DisplayName "PostgreSQL-WSL" -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow -RemoteAddress Any
7. Остановить WSL PostgreSQL
bash
sudo service postgresql stop
sudo systemctl disable postgresql
8. Обновить .env
bash
# .env
DB_HOST=172.26.48.1
DB_PORT=5432
🩺 Диагностика
Table
Проблема	Решение
Connection refused на localhost	WSL PostgreSQL запущен → sudo service postgresql stop
timeout на 172.26.48.1	Hyper-V firewall или port proxy → python3 scripts/fix_wsl_postgres.py
password authentication failed	pg_hba.conf не настроен → добавить host all all 0.0.0.0/0 scram-sha-256
database does not exist	База в другой версии PostgreSQL → проверить версию
📊 Текущие параметры
Table
Параметр	Значение
WSL IP Gateway	172.26.48.1
PostgreSQL Host	172.26.48.1
PostgreSQL Port	5432
PostgreSQL Version	17
Database	finam_predictor
User	postgres
Password	1289
🔗 Связанные файлы
.env — конфиг подключения
scripts/fix_wsl_postgres.py — автоматическое исправление
config/settings.py — загрузка конфига
src/database/models.py — модели SQLAlchemy
