"""
Клиент для работы с Finam Trade API.
Поддерживает REST и gRPC протоколы.
Для исторических данных использует Finam Export API.
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import aiohttp
import pandas as pd
from loguru import logger

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


@dataclass
class OptionChainData:
    """Данные опционного чейна."""
    symbol: str
    option_type: str
    strike: float
    expiration: datetime
    bid: Optional[float]
    ask: Optional[float]
    last_price: Optional[float]
    volume: Optional[int]
    open_interest: Optional[int]
    implied_volatility: Optional[float]
    delta: Optional[float]
    gamma: Optional[float]
    theta: Optional[float]
    vega: Optional[float]


class FinamClient:
    """
    Асинхронный клиент для Finam Trade API.
    """
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or FINAM_CONFIG.token
        self.base_url = FINAM_CONFIG.base_url
        self.timeout = aiohttp.ClientTimeout(total=FINAM_CONFIG.timeout)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        self._session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"FinamClient инициализирован. Base URL: {self.base_url}")
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=self.timeout,
            )
            logger.info("Соединение с Finam API установлено")
    
    async def disconnect(self):
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("Соединение с Finam API закрыто")
    
    async def get_account_info(self) -> Dict[str, Any]:
        return await self._get("/api/v1/accounts")
    
    async def get_securities(self, board: Optional[str] = None, 
                            symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {}
        if board:
            params["board"] = board
        if symbol:
            params["symbol"] = symbol
        return await self._get("/api/v1/securities", params=params)
    
    async def get_candles(self, board: str, symbol: str, timeframe: str = "1m",
                          from_date: Optional[datetime] = None,
                          to_date: Optional[datetime] = None,
                          count: int = 500) -> List[CandleData]:
        tf_code = DATA_CONFIG.TIMEFRAMES.get(timeframe, "M1")
        params = {"timeFrame": tf_code, "count": count}
        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%dT%H:%M:%S")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%dT%H:%M:%S")
        
        response = await self._get(f"/api/v1/securities/{board}/{symbol}/candles", params=params)
        
        candles = []
        for item in response.get("data", []):
            candles.append(CandleData(
                open_price=float(item["open"]),
                high_price=float(item["high"]),
                low_price=float(item["low"]),
                close_price=float(item["close"]),
                volume=int(item["volume"]),
                time=datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00")),
            ))
        logger.info(f"Получено {len(candles)} свечей для {symbol} ({timeframe})")
        return candles
    
    async def get_candles_to_dataframe(self, board: str, symbol: str, 
                                       timeframe: str = "1m",
                                       from_date: Optional[datetime] = None,
                                       to_date: Optional[datetime] = None,
                                       count: int = 500) -> pd.DataFrame:
        candles = await self.get_candles(board, symbol, timeframe, from_date, to_date, count)
        if not candles:
            return pd.DataFrame()
        df = pd.DataFrame([c.to_dict() for c in candles])
        df.set_index("time", inplace=True)
        df.sort_index(inplace=True)
        return df
    
    async def get_option_chain(self, board: str, underlying_symbol: str,
                               expiration_date: Optional[datetime] = None) -> List[OptionChainData]:
        params = {"underlying": underlying_symbol}
        if expiration_date:
            params["expiration"] = expiration_date.strftime("%Y-%m-%d")
        
        response = await self._get(f"/api/v1/securities/{board}/{underlying_symbol}/options", params=params)
        
        options = []
        for item in response.get("data", []):
            options.append(OptionChainData(
                symbol=item["symbol"],
                option_type=item["type"],
                strike=float(item["strike"]),
                expiration=datetime.strptime(item["expiration"], "%Y-%m-%d"),
                bid=float(item["bid"]) if item.get("bid") else None,
                ask=float(item["ask"]) if item.get("ask") else None,
                last_price=float(item["lastPrice"]) if item.get("lastPrice") else None,
                volume=int(item["volume"]) if item.get("volume") else None,
                open_interest=int(item["openInterest"]) if item.get("openInterest") else None,
                implied_volatility=float(item["iv"]) if item.get("iv") else None,
                delta=float(item["delta"]) if item.get("delta") else None,
                gamma=float(item["gamma"]) if item.get("gamma") else None,
                theta=float(item["theta"]) if item.get("theta") else None,
                vega=float(item["vega"]) if item.get("vega") else None,
            ))
        logger.info(f"Получено {len(options)} опционов для {underlying_symbol}")
        return options
    
    async def place_order(self, account_id: str, board: str, symbol: str,
                          side: str, quantity: int, order_type: str = "MARKET",
                          price: Optional[float] = None) -> Dict[str, Any]:
        payload = {
            "accountId": account_id, "board": board, "symbol": symbol,
            "side": side, "quantity": quantity, "type": order_type,
        }
        if price and order_type == "LIMIT":
            payload["price"] = price
        return await self._post("/api/v1/orders", payload)
    
    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        async with self._session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                text = await response.text()
                logger.error(f"GET {url} failed: {response.status} - {text}")
                response.raise_for_status()
    
    async def _post(self, endpoint: str, payload: Dict) -> Any:
        url = f"{self.base_url}{endpoint}"
        async with self._session.post(url, json=payload) as response:
            if response.status in (200, 201):
                return await response.json()
            else:
                text = await response.text()
                logger.error(f"POST {url} failed: {response.status} - {text}")
                response.raise_for_status()
    
    async def _delete(self, endpoint: str) -> Any:
        url = f"{self.base_url}{endpoint}"
        async with self._session.delete(url) as response:
            if response.status in (200, 204):
                return await response.json() if response.status == 200 else {}
            else:
                text = await response.text()
                logger.error(f"DELETE {url} failed: {response.status} - {text}")
                response.raise_for_status()


class FinamExportClient:
    """Клиент для Finam Export API (исторические данные в CSV)."""
    
    EXPORT_URL = "https://export.finam.ru"
    
    MARKETS = {"NYSE": 1, "NASDAQ": 2, "AMEX": 3, "US": 25, "MOEX": 1, "FORTS": 14, "SPBEX": 517}
    PERIODS = {"ticks": 1, "1m": 2, "5m": 3, "10m": 4, "15m": 5, "30m": 6, "1h": 7, "1d": 8, "1w": 9, "1M": 10}
    
    def __init__(self):
        self._session = None
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def download_history(self, symbol: str, market: str = "US", period: str = "1m",
                               from_date: Optional[datetime] = None,
                               to_date: Optional[datetime] = None) -> pd.DataFrame:
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
                from io import StringIO
                df = pd.read_csv(StringIO(content), header=None,
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


class FinamClientSync:
    """Синхронная обёртка над асинхронным клиентом."""
    
    def __init__(self, token: Optional[str] = None):
        self._client = FinamClient(token)
        self._loop = asyncio.new_event_loop()
    
    def __enter__(self):
        self._loop.run_until_complete(self._client.connect())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._loop.run_until_complete(self._client.disconnect())
        self._loop.close()
    
    def _run(self, coro):
        return self._loop.run_until_complete(coro)
    
    def get_securities(self, **kwargs):
        return self._run(self._client.get_securities(**kwargs))
    
    def get_candles_df(self, **kwargs):
        return self._run(self._client.get_candles_to_dataframe(**kwargs))
    
    def get_option_chain(self, **kwargs):
        return self._run(self._client.get_option_chain(**kwargs))


if __name__ == "__main__":
    async def test():
        async with FinamClient() as client:
            securities = await client.get_securities(board="US")
            print(f"Найдено {len(securities)} инструментов")
            candles = await client.get_candles(board="US", symbol="AAPL", timeframe="1d", count=5)
            for c in candles:
                print(f"{c.time.date()}: O={c.open_price} H={c.high_price} L={c.low_price} C={c.close_price}")
    asyncio.run(test())