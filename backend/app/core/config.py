from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./autotrader.db"
    REDIS_URL: Optional[str] = None
    SECRET_KEY: str = "dev_secret_key_change_in_production_min_32_chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    BROKER_MODE: str = "paper"
    ZERODHA_API_KEY: str = ""
    ZERODHA_API_SECRET: str = ""
    
    # Razorpay Payment Gateway
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    
    MAX_POSITION_SIZE: int = 100000
    MAX_DAILY_LOSS: int = 50000
    MAX_LEVERAGE: int = 5
    
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
