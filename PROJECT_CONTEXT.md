# PROJECT CONTEXT - Finam Stock Predictor
> Auto: 2026-07-05 22:33
> Commit: d95220f docs: update PROJECT_CONTEXT with options API, CABA data, fixes | Branch: main

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

*Version: 0.3.0