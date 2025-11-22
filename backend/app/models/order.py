from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class OrderSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, enum.Enum):
    MARKET = "market"
    LIMIT = "limit"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    ext_id = Column(String, unique=True, index=True)  # Broker order ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    symbol = Column(String, nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    type = Column(Enum(OrderType), nullable=False)
    qty = Column(Integer, nullable=False)
    price = Column(Float)
    filled_qty = Column(Integer, default=0)
    avg_fill_price = Column(Float)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True))

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    fill_price = Column(Float, nullable=False)
    fill_qty = Column(Integer, nullable=False)
    fee = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
