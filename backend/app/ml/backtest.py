import pandas as pd
import numpy as np
from typing import Dict

class Backtester:
    """Event-driven backtester with realistic costs"""
    
    def __init__(self, initial_capital=100000, commission=0.0003, slippage=0.0001):
        self.initial_capital = initial_capital
        self.commission = commission  # 0.03%
        self.slippage = slippage      # 0.01%
        
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
    
    def calculate_costs(self, price: float, qty: int) -> float:
        """Calculate transaction costs"""
        notional = price * qty
        comm = notional * self.commission
        slip = notional * self.slippage
        
        # Indian taxes (simplified)
        stt = notional * 0.00025  # STT on sell side
        gst = comm * 0.18         # GST on brokerage
        
        return comm + slip + stt + gst
    
    def execute_trade(self, timestamp, price: float, signal: int, qty: int):
        """Execute trade based on signal"""
        if signal == 1 and self.position == 0:  # Buy
            cost = self.calculate_costs(price, qty)
            self.capital -= (price * qty + cost)
            self.position = qty
            self.trades.append({
                'timestamp': timestamp,
                'action': 'BUY',
                'price': price,
                'qty': qty,
                'cost': cost
            })
        
        elif signal == -1 and self.position > 0:  # Sell
            cost = self.calculate_costs(price, self.position)
            pnl = (price - self.trades[-1]['price']) * self.position - cost
            self.capital += (price * self.position - cost)
            self.position = 0
            self.trades.append({
                'timestamp': timestamp,
                'action': 'SELL',
                'price': price,
                'qty': self.position,
                'cost': cost,
                'pnl': pnl
            })
    
    def run(self, df: pd.DataFrame, signals: pd.Series) -> Dict:
        """Run backtest"""
        for idx, row in df.iterrows():
            signal = signals.loc[idx]
            self.execute_trade(idx, row['close'], signal, qty=1)
            
            # Track equity
            equity = self.capital + (self.position * row['close'] if self.position > 0 else 0)
            self.equity_curve.append({'timestamp': idx, 'equity': equity})
        
        # Calculate metrics
        equity_df = pd.DataFrame(self.equity_curve).set_index('timestamp')
        returns = equity_df['equity'].pct_change().dropna()
        
        total_return = (equity_df['equity'].iloc[-1] / self.initial_capital - 1) * 100
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        max_dd = (equity_df['equity'] / equity_df['equity'].cummax() - 1).min() * 100
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'num_trades': len(self.trades),
            'final_equity': equity_df['equity'].iloc[-1],
            'trades': self.trades
        }
