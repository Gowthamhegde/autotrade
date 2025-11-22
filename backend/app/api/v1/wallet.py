from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.wallet import Wallet, Ledger, LedgerType
from app.models.user import UserRole
from pydantic import BaseModel

router = APIRouter()

class WalletResponse(BaseModel):
    total_balance: float
    reserved_balance: float
    available_balance: float
    
    class Config:
        from_attributes = True

class DepositRequest(BaseModel):
    amount: float

@router.get("/", response_model=WalletResponse)
async def get_wallet(db: Session = Depends(get_db)):
    # For demo, use user_id=1 (Admin)
    user_id = 1
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        # Create wallet if doesn't exist
        wallet = Wallet(user_id=user_id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

@router.post("/deposit")
async def deposit(req: DepositRequest, db: Session = Depends(get_db)):
    # For demo, use user_id=1
    user_id = 1
    
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id)
        db.add(wallet)
    
    wallet.total_balance += req.amount
    wallet.available_balance += req.amount
    
    ledger = Ledger(
        wallet_id=wallet.id,
        type=LedgerType.DEPOSIT,
        amount=req.amount,
        balance_after=wallet.total_balance
    )
    db.add(ledger)
    db.commit()
    
    return {"status": "ok", "new_balance": wallet.total_balance}
