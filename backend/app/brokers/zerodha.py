from app.brokers.base import BaseBroker
from datetime import datetime

class ZerodhaBroker(BaseBroker):
    """
    Zerodha Kite Connect Broker Implementation.
    Requires 'kiteconnect' package and valid API keys.
    """
    
    def __init__(self):
        try:
            from kiteconnect import KiteConnect
            from app.core.config import settings
            
            self.kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
            self.kite.set_access_token(settings.ZERODHA_ACCESS_TOKEN)
            print("Zerodha Broker Initialized")
        except ImportError:
            print("KiteConnect not installed. pip install kiteconnect")
        except Exception as e:
            print(f"Failed to initialize Zerodha broker: {e}")

    async def get_tick(self, symbol: str):
        # Map symbol to instrument token
        # This is a simplified example. You need a mapping logic.
        # e.g., ^NSEI -> 256265 (NIFTY 50)
        token = 256265 if symbol == "^NSEI" else 260105 # BANKNIFTY
        
        try:
            ticks = self.kite.quote([f"NSE:{token}"])
            tick = ticks[f"NSE:{token}"]
            return {
                "symbol": symbol,
                "timestamp": datetime.now(), # Kite gives timestamp
                "last": tick['last_price'],
                "open": tick['ohlc']['open'],
                "high": tick['ohlc']['high'],
                "low": tick['ohlc']['low'],
                "close": tick['ohlc']['close'],
                "volume": tick['volume']
            }
        except Exception as e:
            print(f"Zerodha tick error: {e}")
            return None

    async def get_history(self, symbol: str, interval: str, from_date: datetime, to_date: datetime):
        # Map symbol to token
        token = 256265 if symbol == "^NSEI" else 260105
        
        # Map interval
        # Kite intervals: minute, day, 3minute, 5minute...
        kite_interval = "minute"
        if interval == "5m": kite_interval = "5minute"
        elif interval == "15m": kite_interval = "15minute"
        elif interval == "1h": kite_interval = "60minute"
        elif interval == "1d": kite_interval = "day"
        
        try:
            records = self.kite.historical_data(
                instrument_token=token,
                from_date=from_date,
                to_date=to_date,
                interval=kite_interval
            )
            
            # Convert to DataFrame-like list of dicts
            data = []
            for r in records:
                data.append({
                    "timestamp": r['date'],
                    "open": r['open'],
                    "high": r['high'],
                    "low": r['low'],
                    "close": r['close'],
                    "volume": r['volume']
                })
            return data
        except Exception as e:
            print(f"Zerodha history error: {e}")
            return []

    async def place_order(self, symbol: str, side: str, order_type: str, qty: int, price: float = None):
        try:
            from kiteconnect import KiteConnect
            
            # Map Index to Futures Symbol (Dynamic based on current date ideally)
            # For 2025-11-23, we assume Nov Futures
            tradingsymbol = "NIFTY25NOVFUT" if symbol == "^NSEI" else "BANKNIFTY25NOVFUT"
            
            transaction_type = KiteConnect.TRANSACTION_TYPE_BUY if side == "buy" else KiteConnect.TRANSACTION_TYPE_SELL
            order_type_kite = KiteConnect.ORDER_TYPE_MARKET if order_type == "market" else KiteConnect.ORDER_TYPE_LIMIT
            
            print(f"Placing Real Order: {side} {qty} {tradingsymbol}")
            
            order_id = self.kite.place_order(
                tradingsymbol=tradingsymbol,
                exchange=KiteConnect.EXCHANGE_NFO,
                transaction_type=transaction_type,
                quantity=qty,
                variety=KiteConnect.VARIETY_REGULAR,
                order_type=order_type_kite,
                product=KiteConnect.PRODUCT_MIS, # Intraday
                price=price
            )
            return {"order_id": order_id, "status": "submitted", "price": price or 0}
        except Exception as e:
            print(f"Zerodha order error: {e}")
            raise e

    async def cancel_order(self, order_id: str):
        try:
            self.kite.cancel_order(variety=self.kite.VARIETY_REGULAR, order_id=order_id)
            return {"status": "cancelled"}
        except Exception as e:
            print(f"Zerodha cancel error: {e}")
            return {"status": "failed"}

    async def get_order_status(self, order_id: str):
        try:
            history = self.kite.order_history(order_id=order_id)
            if history:
                return {"status": history[-1]['status']}
            return {"status": "unknown"}
        except Exception as e:
            print(f"Zerodha status error: {e}")
            return {"status": "failed"}
