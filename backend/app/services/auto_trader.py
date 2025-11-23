"""Automated trading service"""
import asyncio
from typing import Dict, List
from sqlalchemy.orm import Session
from app.services.market_analyzer import MarketAnalyzer
from app.brokers.factory import get_broker
from app.models.order import Order, OrderSide, OrderType, OrderStatus
from app.models.position import Position
import logging

logger = logging.getLogger(__name__)

class AutoTrader:
    """Executes trades automatically based on signals"""
    
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
        self.analyzer = MarketAnalyzer()
        self.broker = get_broker()
        self.is_active = False
        self.max_position_size = 1  # Max 1 lot per symbol
        self.active_positions = {}
        
    async def start_trading(self, symbols: List[str]):
        """Start automated trading"""
        self.is_active = True
        logger.info(f"Auto-trader started for user {self.user_id}")
        
        async for signal in self.analyzer.start_analysis(symbols):
            if not self.is_active:
                break
            
            # Execute trade based on signal
            await self.execute_signal(signal)
    
    async def execute_signal(self, signal: Dict):
        """Execute trade based on signal"""
        symbol = signal['symbol']
        action = signal['action']
        confidence = signal['confidence']
        
        logger.info(f"Signal: {action} {symbol} @ {signal['price']:.2f} "
                   f"(Confidence: {confidence:.1%}, Pattern: {signal['pattern_name']})")
        
        # Check if we already have a position
        existing_position = self.db.query(Position).filter(
            Position.user_id == self.user_id,
            Position.symbol == symbol
        ).first()
        
        if action == 'BUY' and not existing_position:
            # Open long position
            await self.place_order(symbol, OrderSide.BUY, signal['price'])
            
        elif action == 'SELL' and existing_position and existing_position.side == 'buy':
            # Close long position
            await self.place_order(symbol, OrderSide.SELL, signal['price'])
    
    async def place_order(self, symbol: str, side: OrderSide, price: float):
        """Place order through broker"""
        try:
            # Place market order
            broker_order = await self.broker.place_order(
                symbol=symbol,
                side=side.value,
                order_type='market',
                qty=self.max_position_size,
                price=None
            )
            
            # Save to database
            order = Order(
                ext_id=broker_order['order_id'],
                user_id=self.user_id,
                symbol=symbol,
                side=side,
                type=OrderType.MARKET,
                qty=self.max_position_size,
                status=OrderStatus.SUBMITTED
            )
            self.db.add(order)
            self.db.commit()
            
            logger.info(f"Order placed: {side.value} {symbol} x{self.max_position_size}")
            
            # Update position
            await self.update_position(symbol, side, broker_order.get('avg_price', price))
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
    
    async def update_position(self, symbol: str, side: OrderSide, price: float):
        """Update position after order execution"""
        position = self.db.query(Position).filter(
            Position.user_id == self.user_id,
            Position.symbol == symbol
        ).first()
        
        if side == OrderSide.BUY:
            if not position:
                # Create new position
                position = Position(
                    user_id=self.user_id,
                    symbol=symbol,
                    side=side,
                    qty=self.max_position_size,
                    avg_price=price
                )
                self.db.add(position)
            else:
                # Update existing
                position.qty += self.max_position_size
                position.avg_price = (position.avg_price + price) / 2
        
        elif side == OrderSide.SELL and position:
            # Close position
            position.qty -= self.max_position_size
            if position.qty <= 0:
                self.db.delete(position)
        
        self.db.commit()
    
    def stop_trading(self):
        """Stop automated trading"""
        self.is_active = False
        self.analyzer.stop_analysis()
        logger.info(f"Auto-trader stopped for user {self.user_id}")
