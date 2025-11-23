from sqlalchemy.orm import Session
from app.models.order import Order, OrderSide, OrderStatus
import pandas as pd

class AnalyticsService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_performance_metrics(self):
        orders = self.db.query(Order).filter(
            Order.user_id == self.user_id,
            Order.status == OrderStatus.FILLED
        ).order_by(Order.created_at).all()

        if not orders:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "profit_factor": 0,
                "max_drawdown": 0
            }

        # Convert to DataFrame for easier calculation
        data = []
        for o in orders:
            data.append({
                "id": o.id,
                "side": o.side,
                "qty": o.qty,
                "price": o.price,
                "timestamp": o.created_at
            })
        
        df = pd.DataFrame(data)
        
        # Simple PnL calculation (FIFO or assumption of paired trades)
        # This is a simplified PnL estimator assuming sequential Buy -> Sell pairs
        # In a real system, we'd match specific buy/sell orders.
        
        pnl_list = []
        balance_curve = [0]
        
        # We need to reconstruct trades from orders
        # Assumption: We always close the full position.
        # We'll just iterate and match buys with subsequent sells.
        
        position = []
        closed_trades = []
        
        for _, row in df.iterrows():
            if row['side'] == OrderSide.BUY:
                position.append(row)
            elif row['side'] == OrderSide.SELL:
                if position:
                    entry = position.pop(0) # FIFO
                    pnl = (row['price'] - entry['price']) * row['qty']
                    closed_trades.append(pnl)
                    balance_curve.append(balance_curve[-1] + pnl)
        
        total_trades = len(closed_trades)
        winning_trades = len([p for p in closed_trades if p > 0])
        losing_trades = len([p for p in closed_trades if p <= 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum(closed_trades)
        
        gross_profit = sum([p for p in closed_trades if p > 0])
        gross_loss = abs(sum([p for p in closed_trades if p < 0]))
        
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
        
        # Max Drawdown
        peak = -float('inf')
        max_dd = 0
        for bal in balance_curve:
            if bal > peak:
                peak = bal
            dd = peak - bal
            if dd > max_dd:
                max_dd = dd
                
        return {
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "Inf",
            "max_drawdown": round(max_dd, 2),
            "balance_curve": balance_curve
        }
