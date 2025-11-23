from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, market, orders, positions, strategies, trading, wallet_v2, oauth
from app.core.config import settings

app = FastAPI(
    title="NIFTY AutoTrader API",
    description="AI-powered automated trading for Indian markets",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["oauth"])
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(positions.router, prefix="/api/v1/positions", tags=["positions"])
app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["strategies"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["trading"])
app.include_router(wallet_v2.router, prefix="/api/v1/wallet", tags=["wallet"])

@app.get("/")
async def root():
    return {"status": "ok", "mode": settings.BROKER_MODE, "version": "2.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/indices")
async def get_indices():
    """Get available Indian market indices"""
    return {
        "indices": [
            {"symbol": "NIFTY", "name": "NIFTY 50", "description": "Top 50 companies"},
            {"symbol": "BANKNIFTY", "name": "BANK NIFTY", "description": "Banking sector"},
            {"symbol": "FINNIFTY", "name": "FIN NIFTY", "description": "Financial services"},
            {"symbol": "MIDCPNIFTY", "name": "MIDCAP NIFTY", "description": "Mid-cap companies"},
            {"symbol": "SENSEX", "name": "SENSEX", "description": "BSE 30 index"}
        ]
    }
