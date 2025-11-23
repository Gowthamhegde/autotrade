"""Trading control endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.services.auto_trader import AutoTrader
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Store active traders (in production, use Redis)
active_traders = {}

class StartTradingRequest(BaseModel):
    symbols: List[str]

class TradingStatus(BaseModel):
    is_active: bool
    symbols: List[str]

@router.post("/start")
async def start_trading(
    req: StartTradingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start automated trading"""
    user_id = current_user.id
    
    if user_id in active_traders:
        raise HTTPException(status_code=400, detail="Trading already active")
    
    # Create auto trader
    trader = AutoTrader(user_id, db)
    active_traders[user_id] = trader
    
    # Start in background
    background_tasks.add_task(trader.start_trading, req.symbols)
    
    return {
        "status": "started",
        "symbols": req.symbols,
        "message": "Auto-trading started. System will execute trades when patterns match with 90%+ confidence."
    }

@router.post("/stop")
async def stop_trading(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Stop automated trading"""
    user_id = current_user.id
    
    if user_id not in active_traders:
        raise HTTPException(status_code=400, detail="Trading not active")
    
    trader = active_traders[user_id]
    trader.stop_trading()
    del active_traders[user_id]
    
    return {"status": "stopped", "message": "Auto-trading stopped"}

@router.get("/status", response_model=TradingStatus)
async def get_trading_status(current_user = Depends(get_current_user)):
    """Get trading status"""
    user_id = current_user.id
    
    if user_id in active_traders:
        trader = active_traders[user_id]
        return {
            "is_active": trader.is_active,
            "symbols": trader.analyzer.active_symbols
        }
    
    return {"is_active": False, "symbols": []}

@router.get("/signals")
async def get_recent_signals(current_user = Depends(get_current_user)):
    """Get recent trading signals"""
    # TODO: Store signals in database and return last 10
    return {"signals": []}
