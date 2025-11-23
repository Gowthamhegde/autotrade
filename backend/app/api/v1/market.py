from fastapi import APIRouter, Depends, Query
from datetime import datetime
from app.brokers.factory import get_broker
from app.api.v1.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class TickData(BaseModel):
    symbol: str
    timestamp: datetime
    last: float
    open: float
    high: float
    low: float
    close: float
    volume: int

@router.get("/tick")
async def get_tick(symbol: str, current_user = Depends(get_current_user)):
    broker = get_broker()
    tick = await broker.get_tick(symbol)
    return tick

@router.get("/history")
async def get_history(
    symbol: str,
    interval: str = Query("1m", regex="^(1m|5m|15m|1h|1d)$"),
    from_date: datetime = None,
    to_date: datetime = None,
    current_user = Depends(get_current_user)
):
    broker = get_broker()
    history = await broker.get_history(symbol, interval, from_date, to_date)
    return history

from app.services.trading_engine import TradingEngine
from pydantic import BaseModel

class TradeRequest(BaseModel):
    symbol: str

@router.post("/start")
async def start_trading(req: TradeRequest, current_user = Depends(get_current_user)):
    engine = TradingEngine()
    return engine.start(req.symbol)

@router.post("/stop")
async def stop_trading(current_user = Depends(get_current_user)):
    engine = TradingEngine()
    return engine.stop()

@router.get("/status")
async def get_status(current_user = Depends(get_current_user)):
    engine = TradingEngine()
    return {"is_running": engine.is_running, "symbol": engine.symbol}
