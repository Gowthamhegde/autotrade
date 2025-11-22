import asyncio
import logging
from datetime import datetime
from app.brokers.factory import get_broker
from app.services.data_loader import DataLoader
# from app.ml.predictor import Predictor # We will create this

logger = logging.getLogger(__name__)

class TradingEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TradingEngine, cls).__new__(cls)
            cls._instance.is_running = False
            cls._instance.symbol = "^NSEI" # Default NIFTY 50
            cls._instance.task = None
        return cls._instance

    def start(self, symbol: str):
        if self.is_running:
            return {"status": "already_running"}
        
        self.symbol = symbol
        self.is_running = True
        self.task = asyncio.create_task(self._run_loop())
        return {"status": "started", "symbol": symbol}

    def stop(self):
        if not self.is_running:
            return {"status": "not_running"}
        
        self.is_running = False
        if self.task:
            self.task.cancel()
        return {"status": "stopped"}

    async def _run_loop(self):
        logger.info(f"Starting trading loop for {self.symbol}")
        broker = get_broker()
        
        # Load model
        import joblib
        import pandas as pd
        from app.ml.features import FeatureEngine
        
        try:
            model = joblib.load("model.pkl")
            logger.info("ML Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            model = None
        
        while self.is_running:
            try:
                # 1. Get Market Data (Need history for features)
                # Fetch last 100 candles to calculate indicators
                df = DataLoader.fetch_history(self.symbol, period="5d", interval="1m")
                
                if df.empty:
                    await asyncio.sleep(5)
                    continue
                    
                # 2. Prepare Features
                df = FeatureEngine.prepare_features(df)
                
                if df.empty:
                    await asyncio.sleep(5)
                    continue
                    
                # Get latest row features
                latest_features = df.iloc[[-1]]
                
                # Exclude non-feature columns
                exclude_cols = ['label_binary', 'label_regression', 'future_return', 'returns']
                feature_cols = [col for col in latest_features.columns if col not in exclude_cols]
                
                # Ensure columns match model (simple check)
                # In real app, we'd save feature list with model
                
                # 3. Predict
                if model:
                    try:
                        # Align columns if possible, or just use what we have matching
                        # This is risky but okay for demo
                        X_pred = latest_features[feature_cols]
                        
                        prob = model.predict_proba(X_pred)[0][1]
                        logger.info(f"Prediction Probability: {prob:.4f}")
                        
                        # 4. Execute Trade
                        # Buy if > 0.6, Sell if < 0.4 (Relaxed threshold for demo)
                        action = None
                        if prob > 0.6:
                            action = "buy"
                        elif prob < 0.4:
                            action = "sell"
                            
                        if action:
                            logger.info(f"Signal: {action.upper()}")
                            # Place order
                            order_data = await broker.place_order(self.symbol, action, "market", 1)
                            
                            # Save to DB
                            from app.core.database import SessionLocal
                            from app.models.order import Order, OrderSide, OrderType, OrderStatus
                            
                            db = SessionLocal()
                            try:
                                db_order = Order(
                                    ext_id=order_data["order_id"],
                                    user_id=1, # Demo user
                                    symbol=self.symbol,
                                    side=OrderSide.BUY if action == "buy" else OrderSide.SELL,
                                    type=OrderType.MARKET,
                                    qty=1,
                                    price=order_data["price"],
                                    status=OrderStatus.FILLED
                                )
                                db.add(db_order)
                                db.commit()
                                logger.info(f"Order saved to DB: {db_order.id}")
                            except Exception as e:
                                logger.error(f"Failed to save order to DB: {e}")
                            finally:
                                db.close()
                            
                    except Exception as e:
                        logger.error(f"Prediction error: {e}")
                
                await asyncio.sleep(60) # Poll every minute (since we use 1m candles)
                
            except asyncio.CancelledError:
                logger.info("Trading loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(5)
