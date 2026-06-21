"""
Клиент для работы с Finam Trade API.
Использует официальную библиотеку finam-trade-api.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import pandas as pd
from loguru import logger

# Официальная библиотека Finam
from finam_trade_api import Client
from finam_trade_api import TokenManager

from config import FINAM_CONFIG, DATA_CONFIG


@dataclass
class CandleData:
    """Структура данных свечи."""
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    time: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "open": self.open_price,
            "high": self.high_price,
            "low": self.low_price,
            "close": self.close_price,
            "volume": self.volume,
            "time": self.time,
        }


class FinamClient:
    """
    Клиент для Finam Trade API.
    Обёртка над официальной библиотекой finam-trade-api.
    """
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or FINAM_CONFIG.token
        self._client: Optional[Client] = None
        
        if not self.token:
            raise ValueError("FINAM_TOKEN не задан! Проверь .env файл.")
        
        logger.info("FinamClient инициализирован")
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self):
        """Устанавливает соединение и получает JWT."""
        try:
            token_manager = TokenManager(self.token)
            self._client = Client(token_manager)
            
            # Получаем JWT токен
            await self._client.access_tokens.set_jwt_token()
            
            # Проверяем что JWT получен
            jwt_details = await self._client.access_tokens.get_jwt_token_details()
            logger.info(f"JWT получен: {jwt_details}")
            
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            raise
    
    async def disconnect(self):
        """Закрывает соединение."""
        if self._client:
            logger.info("Соединение с Finam API закрыто")
    
    # ============================================================
    # AUTH & ACCOUNT
    # ============================================================
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Получает информацию об аккаунте."""
        account_id = FINAM_CONFIG.account_id or ""
        if not account_id:
            logger.warning("FINAM_ACCOUNT_ID не задан!")
            return {}
        try:
            return await self._client.account.get_account_info(account_id)
        except Exception as e:
            logger.error(f"Ошибка получения аккаунта: {e}")
            return {}
    
    # ============================================================
    # MARKET DATA - Через Export API (более надёжно)
    # ============================================================
    
    async def get_candles_to_dataframe(
        self,
        board: str,
        symbol: str,
        timeframe: str = "1m",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        count: int = 500,
    ) -> pd.DataFrame:
        """
        Получает исторические свечи через Finam Export API.
        Более надёжно чем Trade API для исторических данных.
        """
        async with FinamExportClient() as export:
            df = await export.download_history(
                symbol=symbol,
                market=board,
                period=timeframe,
                from_date=from_date,
                to_date=to_date,
            )
            logger.info(f"Получено {len(df)} свечей для {symbol} ({timeframe})")
            return df


# ============================================================
# Finam Export API (для исторических данных)
# ============================================================

class FinamExportClient:
    """Клиент для Finam Export API."""
    
    EXPORT_URL = "https://export.finam.ru"
    
    MARKETS = {"NYSE": 1, "NASDAQ": 2, "AMEX": 3, "US": 25, "MOEX": 1, "FORTS": 14, "SPBEX": 517}
    PERIODS = {"ticks": 1, "1m": 2, "5m": 3, "10m": 4, "15m": 5, "30m": 6, "1h": 7, "1d": 8, "1w": 9, "1M": 10}
    
    def __init__(self):
        import aiohttp
        self._session = None
        self.aiohttp = aiohttp
    
    async def __aenter__(self):
        self._session = self.aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def download_history(self, symbol: str, market: str = "US",
                               period: str = "1m",
                               from_date: Optional[datetime] = None,
                               to_date: Optional[datetime] = None) -> pd.DataFrame:
        """Скачивает исторические данные с Finam Export."""
        import io
        
        market_code = self.MARKETS.get(market, 25)
        period_code = self.PERIODS.get(period, 2)
        
        params = {
            "market": market_code, "em": 0, "code": symbol, "apply": 0,
            "df": from_date.day if from_date else 1,
            "mf": from_date.month - 1 if from_date else 0,
            "yf": from_date.year if from_date else 2020,
            "dt": to_date.day if to_date else 31,
            "mt": to_date.month - 1 if to_date else 11,
            "yt": to_date.year if to_date else 2025,
            "p": period_code, "f": symbol, "e": ".csv", "cn": symbol,
            "dtf": 1, "tmf": 1, "MSOR": 0, "mstime": "on", "mstimever": 1,
            "sep": 1, "sep2": 1, "datf": 5, "at": 0,
        }
        
        url = f"{self.EXPORT_URL}/{symbol}.csv"
        async with self._session.get(url, params=params) as response:
            if response.status == 200:
                content = await response.text()
                df = pd.read_csv(io.StringIO(content), header=None,
                                 names=["ticker", "period", "date", "time", "open", "high", "low", "close", "volume"])
                df["datetime"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str).str.zfill(6),
                                                  format="%Y%m%d %H%M%S")
                df.set_index("datetime", inplace=True)
                df.drop(columns=["ticker", "period", "date", "time"], inplace=True)
                logger.info(f"Скачано {len(df)} строк для {symbol} ({period})")
                return df
            else:
                text = await response.text()
                logger.error(f"Export API failed: {response.status} - {text}")
                raise Exception(f"Failed to download data: {response.status}")


# ============================================================
# SYNC WRAPPER
# ============================================================

import asyncio

class FinamClientSync:
    """Синхронная обёртка над асинхронным клиентом."""
    
    def __init__(self, token: Optional[str] = None):
        self._client = FinamClient(token)
        self