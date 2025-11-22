from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.order import Order, OrderSide, OrderType, OrderStatus
from app.brokers.factory import get_broker
from pydantic import BaseModel

router = APIRouter()

class OrderCreate(BaseModel):
    symbol: str
    side: OrderSide
    type: OrderType
    qty: int
    price: float = None
    strategy_id: int = None

class OrderResponse(BaseModel):
    id: int
    ext_id: str
    symbol: str
    side: OrderSide
    type: OrderType
    qty: int
    filled_qty: int
    status: OrderStatus
    
    class Config:
        from_attributes = True

@router.post("/", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    broker = get_broker()
    
    # Place order with broker
    ext_order = await broker.place_order(
        symbol=order_data.symbol,
        side=order_data.side,
        order_type=order_data.type,
        qty=order_data.qty,
        price=order_data.price
    )
    
    # Save to DB
    order = Order(
        ext_id=ext_order["order_id"],
        user_id=current_user.id,
        strategy_id=order_data.strategy_id,
        symbol=order_data.symbol,
        side=order_data.side,
        type=order_data.type,
        qty=order_data.qty,
        price=order_data.price,
        status=OrderStatus.SUBMITTED
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/")
async def list_orders(db: Session = Depends(get_db)):
    # For demo, use user_id=1
    user_id = 1
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).limit(100).all()
    return orders
