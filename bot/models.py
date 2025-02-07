from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class TradingSignal(Base):
    __tablename__ = 'trading_signals'
    
    id = Column(Integer, primary_key=True)
    pair = Column(String, nullable=False)
    signal_type = Column(String, nullable=False)  # BUY or SELL
    entry_price = Column(Float, nullable=False)
    target_1 = Column(Float)
    target_2 = Column(Float)
    target_3 = Column(Float)
    stop_loss = Column(Float)
    rsi_value = Column(Float)
    macd_value = Column(Float)
    news_sentiment = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pair': self.pair,
            'signal_type': self.signal_type,
            'entry_price': self.entry_price,
            'targets': [self.target_1, self.target_2, self.target_3],
            'stop_loss': self.stop_loss,
            'rsi_value': self.rsi_value,
            'macd_value': self.macd_value,
            'news_sentiment': self.news_sentiment,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class BotSettings(Base):
    __tablename__ = 'bot_settings'
    
    id = Column(Integer, primary_key=True)
    exchange = Column(String, nullable=False)
    trading_pairs = Column(String, nullable=False)  # comma-separated list
    rsi_period = Column(Integer, default=14)
    macd_fast = Column(Integer, default=12)
    macd_slow = Column(Integer, default=26)
    macd_signal = Column(Integer, default=9)
    enable_news = Column(Boolean, default=False)
    telegram_token = Column(String)
    telegram_chat_id = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'exchange': self.exchange,
            'trading_pairs': self.trading_pairs,
            'rsi_period': self.rsi_period,
            'macd_fast': self.macd_fast,
            'macd_slow': self.macd_slow,
            'macd_signal': self.macd_signal,
            'enable_news': self.enable_news,
            'telegram_token': self.telegram_token,
            'telegram_chat_id': self.telegram_chat_id,
            'updated_at': self.updated_at.isoformat()
        }
