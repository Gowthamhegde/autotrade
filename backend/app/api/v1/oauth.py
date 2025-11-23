"""OAuth authentication endpoints for Google and Facebook"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.wallet import Wallet
from app.api.v1.auth import create_access_token
from pydantic import BaseModel
import httpx
import bcrypt
from app.core.config import settings

router = APIRouter()

class GoogleLoginRequest(BaseModel):
    token: str  # Google ID token

class FacebookLoginRequest(BaseModel):
    access_token: str

class OAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/google", response_model=OAuthResponse)
async def google_login(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Login with Google OAuth"""
    try:
        # Verify Google token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={req.token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid Google token")
            
            google_data = response.json()
            email = google_data.get("email")
            name = google_data.get("name", email.split("@")[0])
            
            if not email:
                raise HTTPException(status_code=400, detail="Email not found in Google account")
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user
            # Generate random password for OAuth users
            random_password = bcrypt.hashpw(
                f"google_oauth_{email}".encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            user = User(
                email=email,
                name=name,
                hashed_password=random_password,
                role=UserRole.TRADER
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create wallet for new user
            wallet = Wallet(
                user_id=user.id,
                total_balance=0.0,
                reserved_balance=0.0,
                available_balance=0.0
            )
            db.add(wallet)
            db.commit()
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": user.id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google login failed: {str(e)}")

@router.post("/facebook", response_model=OAuthResponse)
async def facebook_login(req: FacebookLoginRequest, db: Session = Depends(get_db)):
    """Login with Facebook OAuth"""
    try:
        # Verify Facebook token and get user info
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.facebook.com/me?fields=id,name,email&access_token={req.access_token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid Facebook token")
            
            fb_data = response.json()
            email = fb_data.get("email")
            name = fb_data.get("name", "Facebook User")
            
            if not email:
                raise HTTPException(status_code=400, detail="Email not found in Facebook account")
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user
            random_password = bcrypt.hashpw(
                f"facebook_oauth_{email}".encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            user = User(
                email=email,
                name=name,
                hashed_password=random_password,
                role=UserRole.TRADER
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create wallet for new user
            wallet = Wallet(
                user_id=user.id,
                total_balance=0.0,
                reserved_balance=0.0,
                available_balance=0.0
            )
            db.add(wallet)
            db.commit()
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": user.id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Facebook login failed: {str(e)}")
