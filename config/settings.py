import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "finam_predictor")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    
    @property
    def url(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass(frozen=True)
class FinamConfig:
    token: str = os.getenv("FINAM_TOKEN", "")
    account_id: str = os.getenv("FINAM_ACCOUNT_ID", "")
    base_url: str = os.getenv("API_BASE_URL", "https://api.finam.ru")
    timeout: int = int(os.getenv("API_TIMEOUT", "30"))
    rate_limit: int = int(os.getenv("API_RATE_LIMIT", "200"))


@dataclass(frozen=True)
class DataConfig:
    default_timeframe: str = os.getenv("DEFAULT_TIMEFRAME", "1m")
    history_days: int = int(os.getenv("HISTORY_DAYS", "365"))
    
    TIMEFRAMES = {
        "1m": "M1", "5m": "M5", "15m": "M15", "30m": "M30",
        "1h": "H1", "4h": "H4", "1d": "D1", "1w": "W1", "1M": "MN",
    }


DB_CONFIG = DatabaseConfig()
FINAM_CONFIG = FinamConfig()
DATA_CONFIG = DataConfig()