#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path

def generate():
    try:
        b = subprocess.check_output(["git","rev-parse","--abbrev-ref","HEAD"]).decode().strip()
        l = subprocess.check_output(["git","log","-1","--pretty=format:%h %s"]).decode().strip()
    except:
        b,l = "unknown","unknown"
    m = Path("src/database/models.py")
    db = "not found"
    if m.exists():
        r = [x.strip().replace("class ","").replace("(Base):","") for x in m.read_text().split("\n") if "class " in x and "(Base)" in x]
        db = ", ".join(r) if r else "none"
    c = f"""# PROJECT CONTEXT - Finam Stock Predictor
> Auto: {datetime.now().strftime("%Y-%m-%d %H:%M")}
> Commit: {l} | Branch: {b}

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

## DB Models: {db}

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

*Version: 0.3.0"""
    Path("PROJECT_CONTEXT.md").write_text(c, encoding="utf-8")
    print("PROJECT_CONTEXT.md updated")

if __name__ == "__main__":
    generate()