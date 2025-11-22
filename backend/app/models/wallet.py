from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_balance = Column(Float, default=0.0)
    reserved_balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class LedgerType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    HOLD = "hold"
    RELEASE = "release"
    TRADE = "trade"
    FEE = "fee"
    TAX = "tax"

class Ledger(Base):
    __tablename__ = "ledger"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    type = Column(Enum(LedgerType), nullable=False)
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    meta_data = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
