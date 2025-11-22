from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict

class BaseBroker(ABC):
    """Base broker interface for all broker adapters"""
    
    @abstractmethod
    async def get_tick(self, symbol: str) -> Dict:
        """Get current tick data for symbol"""
        pass
    
    @abstractmethod
    async def get_history(self, symbol: str, interval: str, from_date: datetime, to_date: datetime) -> List[Dict]:
        """Get historical OHLCV data"""
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: str, order_type: str, qty: int, price: float = None) -> Dict:
        """Place an order and return order details"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        pass
