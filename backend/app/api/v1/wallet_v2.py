"""Enhanced wallet API with Razorpay integration"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.wallet import Wallet, Ledger, LedgerType
from app.models.user import User
from app.services.payment_service import payment_service
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class WalletResponse(BaseModel):
    total_balance: float
    reserved_balance: float
    available_balance: float
    
    class Config:
        from_attributes = True

class DepositRequest(BaseModel):
    amount: float

class DepositResponse(BaseModel):
    order_id: str
    amount: float
    currency: str
    razorpay_key: str

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class WithdrawRequest(BaseModel):
    amount: float
    upi_id: Optional[str] = None
    bank_account: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    balance_after: float
    timestamp: datetime
    meta_data: Optional[dict] = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=WalletResponse)
async def get_wallet(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get wallet balance"""
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        # Create wallet if doesn't exist
        wallet = Wallet(
            user_id=current_user.id,
            total_balance=0.0,
            reserved_balance=0.0,
            available_balance=0.0
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

@router.post("/deposit/initiate", response_model=DepositResponse)
async def initiate_deposit(
    req: DepositRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initiate deposit via Razorpay"""
    if req.amount < 100:
        raise HTTPException(status_code=400, detail="Minimum deposit amount is ₹100")
    
    if req.amount > 100000:
        raise HTTPException(status_code=400, detail="Maximum deposit amount is ₹1,00,000")
    
    try:
        # Create Razorpay order
        order = payment_service.create_order(
            amount=req.amount,
            receipt=f"deposit_{current_user.id}_{int(datetime.utcnow().timestamp())}"
        )
        
        return {
            "order_id": order['id'],
            "amount": req.amount,
            "currency": "INR",
            "razorpay_key": payment_service.client.auth[0] if payment_service.client else "test_key"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.post("/deposit/verify")
async def verify_deposit(
    req: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify and complete deposit"""
    try:
        # Verify payment signature
        is_valid = payment_service.verify_payment(
            req.razorpay_order_id,
            req.razorpay_payment_id,
            req.razorpay_signature
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Get payment details
        payment = payment_service.get_payment_details(req.razorpay_payment_id)
        amount = payment['amount'] / 100  # Convert from paise to rupees
        
        # Update wallet
        wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
        if not wallet:
            wallet = Wallet(user_id=current_user.id)
            db.add(wallet)
        
        wallet.total_balance += amount
        wallet.available_balance += amount
        
        # Create ledger entry
        ledger = Ledger(
            wallet_id=wallet.id,
            type=LedgerType.DEPOSIT,
            amount=amount,
            balance_after=wallet.total_balance,
            meta_data={
                "razorpay_order_id": req.razorpay_order_id,
                "razorpay_payment_id": req.razorpay_payment_id,
                "method": payment.get('method'),
                "status": "completed"
            }
        )
        db.add(ledger)
        db.commit()
        
        return {
            "status": "success",
            "amount": amount,
            "new_balance": wallet.total_balance,
            "message": f"₹{amount:.2f} added to your wallet"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify payment: {str(e)}")

@router.post("/withdraw")
async def withdraw_funds(
    req: WithdrawRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Withdraw funds to bank/UPI"""
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    if req.amount < 100:
        raise HTTPException(status_code=400, detail="Minimum withdrawal amount is ₹100")
    
    if req.amount > wallet.available_balance:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    if not req.upi_id and not req.bank_account:
        raise HTTPException(status_code=400, detail="UPI ID or bank account required")
    
    # Deduct from wallet
    wallet.total_balance -= req.amount
    wallet.available_balance -= req.amount
    
    # Create ledger entry
    ledger = Ledger(
        wallet_id=wallet.id,
        type=LedgerType.WITHDRAW,
        amount=-req.amount,
        balance_after=wallet.total_balance,
        meta_data={
            "upi_id": req.upi_id,
            "bank_account": req.bank_account,
            "status": "pending",
            "initiated_at": datetime.utcnow().isoformat()
        }
    )
    db.add(ledger)
    db.commit()
    
    return {
        "status": "success",
        "amount": req.amount,
        "new_balance": wallet.total_balance,
        "message": f"Withdrawal of ₹{req.amount:.2f} initiated. Will be processed in 1-2 business days."
    }

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transaction history"""
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    
    if not wallet:
        return []
    
    transactions = db.query(Ledger).filter(
        Ledger.wallet_id == wallet.id
    ).order_by(Ledger.timestamp.desc()).limit(limit).all()
    
    return transactions

@router.get("/stats")
async def get_wallet_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get wallet statistics"""
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    
    if not wallet:
        return {
            "total_deposits": 0,
            "total_withdrawals": 0,
            "total_trades": 0,
            "total_fees": 0
        }
    
    ledger_entries = db.query(Ledger).filter(Ledger.wallet_id == wallet.id).all()
    
    total_deposits = sum(l.amount for l in ledger_entries if l.type == LedgerType.DEPOSIT)
    total_withdrawals = abs(sum(l.amount for l in ledger_entries if l.type == LedgerType.WITHDRAW))
    total_fees = abs(sum(l.amount for l in ledger_entries if l.type == LedgerType.FEE))
    total_trades = len([l for l in ledger_entries if l.type == LedgerType.TRADE])
    
    return {
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_trades": total_trades,
        "total_fees": total_fees,
        "current_balance": wallet.total_balance,
        "available_balance": wallet.available_balance,
        "reserved_balance": wallet.reserved_balance
    }
