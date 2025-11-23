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
            
        # Risk Management Settings
        STOP_LOSS_PCT = 0.01  # 1%
        TAKE_PROFIT_PCT = 0.02 # 2%
        
        # State
        active_position = None # { 'side': 'buy'/'sell', 'entry_price': float, 'qty': int }
        
        while self.is_running:
            try:
                # 1. Get Market Data
                df = DataLoader.fetch_history(self.symbol, period="5d", interval="1m")
                
                if df.empty:
                    await asyncio.sleep(5)
                    continue
                
                current_price = df['close'].iloc[-1]
                
                # 2. Check Risk Management (if position exists)
                if active_position:
                    entry_price = active_position['entry_price']
                    side = active_position['side']
                    pnl_pct = 0.0
                    
                    if side == 'buy':
                        pnl_pct = (current_price - entry_price) / entry_price
                    else:
                        pnl_pct = (entry_price - current_price) / entry_price
                        
                    # Check SL/TP
                    exit_reason = None
                    if pnl_pct <= -STOP_LOSS_PCT:
                        exit_reason = "STOP_LOSS"
                    elif pnl_pct >= TAKE_PROFIT_PCT:
                        exit_reason = "TAKE_PROFIT"
                        
                    if exit_reason:
                        logger.info(f"{exit_reason} Hit! PnL: {pnl_pct*100:.2f}%")
                        # Close Position
                        exit_side = "sell" if side == "buy" else "buy"
                        await broker.place_order(self.symbol, exit_side, "market", active_position['qty'])
                        self._save_order_to_db(self.symbol, exit_side, active_position['qty'], current_price)
                        active_position = None
                        await asyncio.sleep(5)
                        continue

                # 3. Prepare Features & Predict (Only if no position)
                if not active_position:
                    df = FeatureEngine.prepare_features(df)
                    
                    if not df.empty:
                        latest_features = df.iloc[[-1]]
                        exclude_cols = ['label_binary', 'label_regression', 'future_return', 'returns']
                        feature_cols = [col for col in latest_features.columns if col not in exclude_cols]
                        
                        if model:
                            try:
                                X_pred = latest_features[feature_cols]
                                prob = model.predict_proba(X_pred)[0][1]
                                logger.info(f"Prediction Probability: {prob:.4f}")
                                
                                # 4. Execute Entry
                                action = None
                                # Strict thresholds
                                if prob > 0.8: # Very high confidence Buy
                                    action = "buy"
                                elif prob < 0.2: # Very high confidence Sell
                                    action = "sell"
                                    
                                if action:
                                    logger.info(f"Signal: {action.upper()}")
                                    qty = 50 # 1 Lot NIFTY (approx)
                                    
                                    # Place order
                                    order_data = await broker.place_order(self.symbol, action, "market", qty)
                                    
                                    # Record Position
                                    active_position = {
                                        'side': action,
                                        'entry_price': order_data['price'] if order_data.get('price') else current_price,
                                        'qty': qty
                                    }
                                    
                                    self._save_order_to_db(self.symbol, action, qty, active_position['entry_price'])
                                    
                            except Exception as e:
                                logger.error(f"Prediction error: {e}")
                
                await asyncio.sleep(15) # Poll faster (15s) to check SL/TP
                
            except asyncio.CancelledError:
                logger.info("Trading loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(5)

    def _save_order_to_db(self, symbol, side, qty, price):
        from app.core.database import SessionLocal
        from app.models.order import Order, OrderSide, OrderType, OrderStatus
        
        db = SessionLocal()
        try:
            db_order = Order(
                ext_id=f"auto_{int(datetime.now().timestamp())}",
                user_id=1, # Demo user
                symbol=symbol,
                side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
                type=OrderType.MARKET,
                qty=qty,
                price=price,
                status=OrderStatus.FILLED
            )
            db.add(db_order)
            db.commit()
            logger.info(f"Order saved to DB: {db_order.id}")
        except Exception as e:
            logger.error(f"Failed to save order to DB: {e}")
        finally:
            db.close()
