import pytest
import pandas as pd
import numpy as np
from app.ml.backtest import Backtester

def test_backtester_basic():
    """Test basic backtester functionality"""
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='1min')
    df = pd.DataFrame({
        'close': 19500 + np.random.randn(100).cumsum()
    }, index=dates)
    
    # Simple buy-hold-sell signals
    signals = pd.Series([0] * 100, index=dates)
    signals.iloc[10] = 1  # Buy
    signals.iloc[50] = -1  # Sell
    
    backtester = Backtester(initial_capital=100000)
    results = backtester.run(df, signals)
    
    assert 'total_return' in results
    assert 'sharpe_ratio' in results
    assert 'max_drawdown' in results
    assert results['num_trades'] == 2
