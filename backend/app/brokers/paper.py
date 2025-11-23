from app.brokers.base import BaseBroker
from app.services.data_loader import DataLoader
from datetime import datetime
import uuid
import asyncio
import yfinance as yf

class PaperBroker(BaseBroker):
    """Paper trading broker using yfinance data"""
    
    def __init__(self):
                "low": 0.0,
                "close": 0.0,
                "volume": 0
            }

    async def get_history(self, symbol: str, interval: str, from_date: datetime, to_date: datetime):
        # Map interval to yfinance format
        yf_interval = interval if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d"] else "1h"
        
        # Calculate period based on dates (approximate)
        # For simplicity, we'll just use a fixed period based on interval for now
        # or let DataLoader handle it if we pass dates? 
        # DataLoader uses period, not dates.
        # We'll use a default period for now.
        period = "1mo"
        if interval == "1m": period = "5d"
        if interval == "5m": period = "1mo"
        
        df = DataLoader.fetch_history(symbol, period=period, interval=yf_interval)
        
        # Convert to list of dicts
        data = []
        for _, row in df.iterrows():
            data.append({
                "timestamp": row['timestamp'],
                "open": row['open'],
                "high": row['high'],
                "low": row['low'],
                "close": row['close'],
                "volume": row['volume']
            })
            
        return data

    async def place_order(self, symbol: str, side: str, order_type: str, qty: int, price: float = None):
        order_id = str(uuid.uuid4())
        
        # Get current price if market order
        current_price = price
        if order_type == "market":
            tick = await self.get_tick(symbol)
            current_price = tick['last']
            
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "qty": qty,
            "price": current_price,
            "status": "filled", # Auto-fill for paper trading
            "filled_qty": qty,
            "avg_price": current_price,
            "timestamp": datetime.now()
        }
        
        self.orders[order_id] = order
        
        # Update positions
        if symbol not in self.positions:
            self.positions[symbol] = {"qty": 0, "avg_price": 0.0}
            
        pos = self.positions[symbol]
        if side == "buy":
            total_cost = (pos['qty'] * pos['avg_price']) + (qty * current_price)
            pos['qty'] += qty
            pos['avg_price'] = total_cost / pos['qty'] if pos['qty'] > 0 else 0
            self.balance -= (qty * current_price)
        else:
            pos['qty'] -= qty
            self.balance += (qty * current_price)
            
        return order

    async def cancel_order(self, order_id: str):
        if order_id in self.orders:
            self.orders[order_id]["status"] = "cancelled"
            return self.orders[order_id]
        return {"error": "Order not found"}

    async def get_order_status(self, order_id: str):
        return self.orders.get(order_id, {"error": "Order not found"})
