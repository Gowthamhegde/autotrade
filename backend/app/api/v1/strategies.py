from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.strategy import Strategy
from app.models.user import UserRole

router = APIRouter()

@router.get("/")
async def list_strategies(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    strategies = db.query(Strategy).all()
    return strategies

@router.post("/{strategy_id}/deploy")
async def deploy_strategy(strategy_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    strategy.is_active = True
    db.commit()
    
    return {"status": "deployed", "strategy_id": strategy_id}
