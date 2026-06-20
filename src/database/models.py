from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, BigInteger, Numeric, Index, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from config import DB_CONFIG

Base = declarative_base()
engine = create_engine(DB_CONFIG.url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Ticker(Base):
    __tablename__ = "tickers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    exchange = Column(String(20), nullable=False)
    currency = Column(String(3), default="USD")
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    lot_size = Column(Integer, default=1)
    price_step = Column(Numeric(10, 4), default=0.01)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    candles = relationship("Candle", back_populates="ticker", cascade="all, delete-orphan")
    options = relationship("Option", back_populates="underlying_ticker", cascade="all, delete-orphan")
    
    __table_args__ = (Index("idx_tickers_symbol_exchange", "symbol", "exchange"),)


class Candle(Base):
    __tablename__ = "candles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker_id = Column(UUID(as_uuid=True), ForeignKey("tickers.id", ondelete="CASCADE"), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    
    open_price = Column(Numeric(18, 8), nullable=False)
    high_price = Column(Numeric(18, 8), nullable=False)
    low_price = Column(Numeric(18, 8), nullable=False)
    close_price = Column(Numeric(18, 8), nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    candle_time = Column(DateTime, nullable=False, index=True)
    vwap = Column(Numeric(18, 8), nullable=True)
    trades_count = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ticker = relationship("Ticker", back_populates="candles")
    
    __table_args__ = (
        UniqueConstraint("ticker_id", "timeframe", "candle_time", name="uix_candle_unique"),
        Index("idx_candles_timeframe_time", "timeframe", "candle_time"),
        Index("idx_candles_ticker_time", "ticker_id", "candle_time"),
    )


class Option(Base):
    __tablename__ = "options"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    underlying_ticker_id = Column(UUID(as_uuid=True), ForeignKey("tickers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    symbol = Column(String(30), nullable=False, unique=True, index=True)
    option_type = Column(String(4), nullable=False)
    strike = Column(Numeric(18, 4), nullable=False, index=True)
    expiration_date = Column(DateTime, nullable=False, index=True)
    
    delta = Column(Numeric(10, 6), nullable=True)
    gamma = Column(Numeric(10, 6), nullable=True)
    theta = Column(Numeric(10, 6), nullable=True)
    vega = Column(Numeric(10, 6), nullable=True)
    rho = Column(Numeric(10, 6), nullable=True)
    implied_volatility = Column(Numeric(10, 6), nullable=True)
    
    open_interest = Column(BigInteger, nullable=True)
    volume = Column(BigInteger, nullable=True)
    bid = Column(Numeric(18, 4), nullable=True)
    ask = Column(Numeric(18, 4), nullable=True)
    last_price = Column(Numeric(18, 4), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    underlying_ticker = relationship("Ticker", back_populates="options")
    option_candles = relationship("OptionCandle", back_populates="option", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_options_underlying_strike", "underlying_ticker_id", "strike"),
        Index("idx_options_expiration", "expiration_date"),
        Index("idx_options_type_strike", "option_type", "strike"),
    )


class OptionCandle(Base):
    __tablename__ = "option_candles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    option_id = Column(UUID(as_uuid=True), ForeignKey("options.id", ondelete="CASCADE"), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    
    open_price = Column(Numeric(18, 8), nullable=False)
    high_price = Column(Numeric(18, 8), nullable=False)
    low_price = Column(Numeric(18, 8), nullable=False)
    close_price = Column(Numeric(18, 8), nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    candle_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    option = relationship("Option", back_populates="option_candles")
    
    __table_args__ = (
        UniqueConstraint("option_id", "timeframe", "candle_time", name="uix_option_candle_unique"),
        Index("idx_option_candles_time", "option_id", "candle_time"),
    )


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker_id = Column(UUID(as_uuid=True), ForeignKey("tickers.id", ondelete="CASCADE"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    
    predicted_direction = Column(String(10), nullable=False)
    predicted_price = Column(Numeric(18, 8), nullable=True)
    confidence = Column(Numeric(5, 4), nullable=False)
    
    prediction_horizon = Column(String(20), nullable=False)
    prediction_time = Column(DateTime, nullable=False)
    target_time = Column(DateTime, nullable=False)
    
    actual_direction = Column(String(10), nullable=True)
    actual_price = Column(Numeric(18, 8), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    
    model_version = Column(String(50), nullable=True)
    features_used = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_predictions_ticker_time", "ticker_id", "prediction_time"),
        Index("idx_predictions_model", "model_name", "model_version"),
    )


def init_database():
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована!")


def get_db_session():
    return SessionLocal()