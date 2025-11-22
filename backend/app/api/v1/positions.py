from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.position import Position

router = APIRouter()

@router.get("/")
async def get_positions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    positions = db.query(Position).filter(Position.user_id == current_user.id).all()
    return positions
