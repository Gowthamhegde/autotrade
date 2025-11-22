from app.brokers.base import BaseBroker
from datetime import datetime, timedelta
import random
import uuid

class MockBroker(BaseBroker):
    """Mock broker for testing and paper trading"""
    
    def __init__(self):
        self.orders = {}
        self.base_price = 19500  # NIFTY base price
    
    async def get_tick(self, symbol: str):
        price = self.base_price + random.uniform(-50, 50)
        return {
            "symbol": symbol,
            "timestamp": datetime.utcnow(),
            "last": price,
            "open": price - 10,
            "high": price + 20,
            "low": price - 30,
            "close": price,
            "volume": random.randint(1000, 10000)
        }
    
    async def get_history(self, symbol: str, interval: str, from_date: datetime, to_date: datetime):
        # Return mock historical data
        data = []
        current = from_date
        while current < to_date:
            price = self.base_price + random.uniform(-100, 100)
            data.append({
                "timestamp": current,
                "open": price,
                "high": price + 20,
                "low": price - 20,
                "close": price + random.uniform(-10, 10),
                "volume": random.randint(1000, 10000)
            })
            current = current + timedelta(minutes=1)
        return data
    
    async def place_order(self, symbol: str, side: str, order_type: str, qty: int, price: float = None):
        order_id = str(uuid.uuid4())
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "qty": qty,
            "price": price,
            "status": "submitted",
            "filled_qty": 0
        }
        self.orders[order_id] = order
        
        # Auto-fill market orders
        if order_type == "market":
            order["status"] = "filled"
            order["filled_qty"] = qty
            order["avg_price"] = self.base_price + random.uniform(-5, 5)
        
        return order
    
    async def cancel_order(self, order_id: str):
        if order_id in self.orders:
            self.orders[order_id]["status"] = "cancelled"
            return self.orders[order_id]
        return {"error": "Order not found"}
    
    async def get_order_status(self, order_id: str):
        return self.orders.get(order_id, {"error": "Order not found"})
