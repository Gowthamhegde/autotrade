import pytest
import pandas as pd
import numpy as np
from app.ml.features import FeatureEngine

def test_technical_indicators():
    """Test technical indicator calculation"""
    dates = pd.date_range('2023-01-01', periods=100, freq='1min')
    df = pd.DataFrame({
        'open': 19500 + np.random.randn(100),
        'high': 19520 + np.random.randn(100),
        'low': 19480 + np.random.randn(100),
        'close': 19500 + np.random.randn(100),
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    df_features = FeatureEngine.add_technical_indicators(df)
    
    assert 'sma_5' in df_features.columns
    assert 'rsi' in df_features.columns
    assert 'macd' in df_features.columns
    assert 'atr' in df_features.columns

def test_prepare_features():
    """Test full feature pipeline"""
    dates = pd.date_range('2023-01-01', periods=100, freq='1min')
    df = pd.DataFrame({
        'open': 19500 + np.random.randn(100),
        'high': 19520 + np.random.randn(100),
        'low': 19480 + np.random.randn(100),
        'close': 19500 + np.random.randn(100),
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    df_features = FeatureEngine.prepare_features(df)
    
    assert 'label_binary' in df_features.columns
    assert 'hour' in df_features.columns
    assert len(df_features) < len(df)  # Some rows dropped due to NaN
