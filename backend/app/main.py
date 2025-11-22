from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, market, orders, positions, wallet, strategies
from app.core.config import settings

app = FastAPI(
    title="NIFTY AutoTrader API",
    description="ML-driven algo trading platform for Indian derivatives",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(positions.router, prefix="/api/v1/positions", tags=["positions"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["wallet"])
app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["strategies"])

@app.get("/")
async def root():
    return {"status": "ok", "mode": settings.BROKER_MODE}

@app.get("/health")
async def health():
    return {"status": "healthy"}
