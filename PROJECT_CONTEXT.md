# PROJECT CONTEXT - Finam Stock Predictor
> Auto: 2026-07-07 21:20
> Commit: 1482c9c feat: add SPRINTS.md and auto-update script for PROJECT_CONTEXT | Branch: main

## Project
| Param | Value |
|-------|-------|
| Name | Finam Stock Predictor |
| Lang | Python 3.11+ |
| IDE | VS Code + WSL |
| DB | PostgreSQL 16 |
| API | Finam Trade API |

## API Status
- JWT: OK
- Account: 2045914
- CABA candles (7d): 1314 OK
- Options: 138 OK
- Option candles: OK

## DB Models: Ticker, Candle, Option, OptionCandle, Prediction

## Done
- [x] Project structure
- [x] API client
- [x] Data fetcher
- [x] CABA 7 days saved
- [x] Options discovered
- [x] WSL setup
- [x] Auto context

## Next
- [ ] DB for options
- [ ] Fetch option quotes (strikes 2-7)
- [ ] Save options to DB
- [ ] Feature engineering
- [ ] ML model
- [ ] Trading

## 🔗 WSL → Windows PostgreSQL Connection
| Параметр | Значение |
|----------|----------|
| **WSL IP Gateway** | `172.26.48.1` (из `ip route \| grep default`) |
| **PostgreSQL Host** | `172.26.48.1` |
| **Port Proxy** | `netsh interface portproxy add v4tov4 listenport=5432 listenaddress=0.0.0.0 connectport=5432 connectaddress=127.0.0.1` |
| **pg_hba.conf** | `C:\Program Files\PostgreSQL\17\data\pg_hba.conf` |
| **Firewall Rule** | `PostgreSQL-WSL` (Allow) |
| **PostgreSQL Version** | 17 (слушает порт 5432) |
| **WSL PostgreSQL** | Остановлен (`sudo service postgresql stop`) |

### Настройка (один раз):
1. `pg_hba.conf` → добавить `host all all 0.0.0.0/0 scram-sha-256`
2. `postgresql.conf` → `listen_addresses = '*'`
3. PowerShell admin: `Restart-Service postgresql-x64-17`
4. PowerShell admin: `netsh interface portproxy add v4tov4 listenport=5432 listenaddress=0.0.0.0 connectport=5432 connectaddress=127.0.0.1`
5. PowerShell admin: `New-NetFirewallRule -DisplayName "PostgreSQL-WSL" -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow`
6. WSL: `sudo service postgresql stop` (остановить WSL PostgreSQL)
7. `.env` → `DB_HOST=172.26.48.1`

*Version: 0.3.0