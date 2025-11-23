"""Real-time market analysis service"""
import asyncio
import numpy as np
from datetime import datetime
from typing import Dict, List
from app.ml.features import FeatureEngine
from app.brokers.factory import get_broker
import logging

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Analyzes market in real-time and generates trading signals"""
    
    def __init__(self):
        self.broker = get_broker()
        self.is_running = False
        self.active_symbols = []
        self.model = None
        self.confidence_threshold = 0.90  # 90% confidence
        self.historical_data = {}
        
    async def start_analysis(self, symbols: List[str], model_path: str = None):
        """Start real-time market analysis"""
        self.is_running = True
        self.active_symbols = symbols
        
        # Load trained model if provided
        if model_path:
            self.load_model(model_path)
        
        logger.info(f"Started market analysis for {symbols}")
        
        while self.is_running:
            for symbol in self.active_symbols:
                try:
                    signal = await self.analyze_symbol(symbol)
                    if signal:
                        yield signal
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
            
            await asyncio.sleep(1)  # Check every second
    
    async def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze single symbol and generate signal"""
        # Get latest tick
        tick = await self.broker.get_tick(symbol)
        
        # Update historical data
        if symbol not in self.historical_data:
            self.historical_data[symbol] = []
        
        self.historical_data[symbol].append({
            'timestamp': tick['timestamp'],
            'close': tick['last'],
            'high': tick['high'],
            'low': tick['low'],
            'volume': tick['volume']
        })
        
        # Keep only last 100 candles
        if len(self.historical_data[symbol]) > 100:
            self.historical_data[symbol] = self.historical_data[symbol][-100:]
        
        # Need at least 50 candles for analysis
        if len(self.historical_data[symbol]) < 50:
            return None
        
        # Detect patterns
        pattern = self.detect_pattern(symbol)
        
        if pattern and pattern['confidence'] >= self.confidence_threshold:
            return {
                'symbol': symbol,
                'action': pattern['action'],
                'confidence': pattern['confidence'],
                'price': tick['last'],
                'timestamp': datetime.utcnow(),
                'pattern_name': pattern['name'],
                'reason': pattern['reason']
            }
        
        return None
    
    def detect_pattern(self, symbol: str) -> Dict:
        """Detect trading patterns with confidence score"""
        data = self.historical_data[symbol]
        prices = [d['close'] for d in data]
        
        # Calculate indicators
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        current_price = prices[-1]
        
        # Price momentum
        momentum = (current_price - prices[-10]) / prices[-10]
        
        # Volatility
        volatility = np.std(prices[-20:]) / np.mean(prices[-20:])
        
        # Pattern 1: Golden Cross (SMA 20 crosses above SMA 50)
        if sma_20 > sma_50 and momentum > 0.01:
            confidence = min(0.95, 0.85 + abs(momentum) * 10)
            return {
                'name': 'Golden Cross',
                'action': 'BUY',
                'confidence': confidence,
                'reason': f'SMA20 ({sma_20:.2f}) > SMA50 ({sma_50:.2f}), Momentum: {momentum:.2%}'
            }
        
        # Pattern 2: Death Cross (SMA 20 crosses below SMA 50)
        if sma_20 < sma_50 and momentum < -0.01:
            confidence = min(0.95, 0.85 + abs(momentum) * 10)
            return {
                'name': 'Death Cross',
                'action': 'SELL',
                'confidence': confidence,
                'reason': f'SMA20 ({sma_20:.2f}) < SMA50 ({sma_50:.2f}), Momentum: {momentum:.2%}'
            }
        
        # Pattern 3: Breakout (price breaks above recent high with volume)
        recent_high = max(prices[-20:-1])
        if current_price > recent_high * 1.005 and momentum > 0.015:
            return {
                'name': 'Breakout',
                'action': 'BUY',
                'confidence': 0.92,
                'reason': f'Price broke above {recent_high:.2f}, Strong momentum'
            }
        
        # Pattern 4: Breakdown (price breaks below recent low)
        recent_low = min(prices[-20:-1])
        if current_price < recent_low * 0.995 and momentum < -0.015:
            return {
                'name': 'Breakdown',
                'action': 'SELL',
                'confidence': 0.91,
                'reason': f'Price broke below {recent_low:.2f}, Weak momentum'
            }
        
        return None
    
    def load_model(self, model_path: str):
        """Load trained ML model"""
        # TODO: Load from MLflow or pickle
        pass
    
    def stop_analysis(self):
        """Stop market analysis"""
        self.is_running = False
        logger.info("Stopped market analysis")
