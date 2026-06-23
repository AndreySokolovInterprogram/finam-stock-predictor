"""Клиент для Finam Trade API. Исторические свечи через /v1/instruments/{symbol}/bars"""

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import aiohttp
import pandas as pd
from loguru import logger

from config import FINAM_CONFIG


@dataclass
class CandleData:
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    time: datetime


class FinamClient:
    """Клиент для Finam Trade API v1."""
    
    BASE_URL = "https://api.finam.ru"
    
    # MIC коды бирж
    MIC_CODES = {
        "MISX": "MISX",   # Мосбиржа
        "XNGS": "XNGS",   # NASDAQ
        "XNYS": "XNYS",   # NYSE
        "XASE": "XASE",   # AMEX / NYSE American
        "XNAS": "XNAS",   # NASDAQ (альтернатива)
    }
    
    # Таймфреймы
    TIMEFRAMES = {
        "1m": 1,
        "5m": 2,
        "15m": 3,
        "30m": 4,
        "1h": 5,
        "4h": 6,
        "1d": 7,
    }
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or FINAM_CONFIG.token
        self._jwt_token: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None
        
        if not self.token:
            raise ValueError("FINAM_TOKEN не задан!")
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self):
        """Получает JWT и создаёт сессию."""
        # Получаем JWT через POST /v1/sessions
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/v1/sessions",
                headers={"Content-Type": "application/json"},
                json={"secret": self.token}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._jwt_token = data["token"]
                    logger.info("JWT получен")
                else:
                    text = await resp.text()
                    raise Exception(f"Auth failed: {resp.status} - {text}")
        
        # Создаём сессию с JWT
        self._session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self._jwt_token}"}
        )
    
    async def disconnect(self):
        if self._session:
            await self._session.close()
    
    async def get_candles(
        self,
        symbol: str,
        mic: str = "MISX",
        timeframe: str = "1d",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        count: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Получает свечи через /v1/instruments/{symbol}@mic/bars
        
        Args:
            symbol: Тикер (CABA, SBER и т.д.)
            mic: MIC код биржи (XNGS, XNYS, MISX)
            timeframe: 1m, 5m, 15m, 30m, 1h, 1d, 1w
            from_date: Начальная дата
            to_date: Конечная дата
            count: Количество свечей (если не указаны даты)
        """
        tf_code = self.TIMEFRAMES.get(timeframe, "TIME_FRAME_D1")
        
        params = {"timeframe": tf_code}
        
        if from_date:
            params["interval.start_time"] = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        if to_date:
            params["interval.end_time"] = to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        url = f"{self.BASE_URL}/v1/instruments/{symbol}@{mic}/bars"
        
        logger.info(f"Запрос: {symbol}@{mic}, {timeframe}")
        
        async with self._session.get(url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                bars = data.get("bars", [])
                
                if not bars:
                    logger.warning(f"Нет данных для {symbol}")
                    return pd.DataFrame()
                
                candles = []
                for bar in bars:
                    candles.append({
                        "open": float(bar["open"]["value"]),
                        "high": float(bar["high"]["value"]),
                        "low": float(bar["low"]["value"]),
                        "close": float(bar["close"]["value"]),
                        "volume": int(float(bar.get("volume", {}).get("value", 0))) if isinstance(bar.get("volume"), dict) else int(float(bar.get("volume", 0))),
                        "time": datetime.fromisoformat(bar["timestamp"].replace("Z", "+00:00")),
                    })
                
                df = pd.DataFrame(candles)
                if not df.empty:
                    df.set_index("time", inplace=True)
                    df.sort_index(inplace=True)
                
                logger.info(f"Получено {len(df)} свечей")
                return df
                
            elif resp.status == 400:
                text = await resp.text()
                logger.error(f"400 Bad Request: {text}")
                raise Exception(f"Неверный символ или интервал. Проверьте формат {symbol}@{mic}")
            else:
                text = await resp.text()
                raise Exception(f"HTTP {resp.status}: {text}")


# ============================================================
# SYNC WRAPPER
# ============================================================

import asyncio

class FinamClientSync:
    def __init__(self, token=None):
        self._client = FinamClient(token)
        self._loop = asyncio.new_event_loop()
    
    def __enter__(self):
        self._loop.run_until_complete(self._client.connect())
        return self
    
    def __exit__(self, *args):
        self._loop.run_until_complete(self._client.disconnect())
        self._loop.close()
    
    def get_candles(self, **kwargs):
        return self._loop.run_until_complete(self._client.get_candles(**kwargs))


if __name__ == "__main__":
    async def test():
        async with FinamClient() as client:
            print("=== CABA (NASDAQ) ===")
            df = await client.get_candles(
                symbol="CABA",
                mic="XNGS",
                timeframe="1d",
                from_date=datetime.now() - timedelta(days=7),
                to_date=datetime.now(),
            )
            print(f"Получено: {len(df)}")
            print(df)
    
    asyncio.run(test())