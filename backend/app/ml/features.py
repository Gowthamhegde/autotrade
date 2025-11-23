import pandas as pd
import numpy as np
import pandas_ta as ta

class FeatureEngine:
    """Feature engineering for ML models"""
    
    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Ensure pandas-ta is available
        try:
            import pandas_ta as ta
        except ImportError:
            raise ImportError("pandas-ta is required. pip install pandas-ta")

        # 1. Trend Indicators
        df['sma_20'] = df.ta.sma(length=20)
        df['sma_50'] = df.ta.sma(length=50)
        df['ema_9'] = df.ta.ema(length=9)
        df['ema_21'] = df.ta.ema(length=21)
        
        # MACD
        macd = df.ta.macd(fast=12, slow=26, signal=9)
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
            
        # ADX (Trend Strength)
        adx = df.ta.adx(length=14)
        if adx is not None:
            df = pd.concat([df, adx], axis=1)

        # 2. Momentum Indicators
        df['rsi'] = df.ta.rsi(length=14)
        df['stoch_k'] = df.ta.stoch(k=14, d=3, smooth_k=3)['STOCHk_14_3_3']
        df['stoch_d'] = df.ta.stoch(k=14, d=3, smooth_k=3)['STOCHd_14_3_3']
        
        # CCI (Commodity Channel Index)
        df['cci'] = df.ta.cci(length=20)

        # 3. Volatility Indicators
        # Bollinger Bands
        bbands = df.ta.bbands(length=20, std=2)
        if bbands is not None:
            df = pd.concat([df, bbands], axis=1)
            
        # ATR (Average True Range)
        df['atr'] = df.ta.atr(length=14)
        
        # 4. Volume Indicators
        # VWAP (Volume Weighted Average Price) - Requires 'volume'
        if 'volume' in df.columns:
            # VWAP requires datetime index
            df.ta.vwap(append=True)
            
            # OBV (On Balance Volume)
            df['obv'] = df.ta.obv()

        # 5. Custom Features
        # Distance from SMA
        df['dist_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']
        
        # RSI Divergence (Simplified: RSI slope vs Price slope)
        df['rsi_slope'] = df['rsi'].diff(3)
        df['price_slope'] = df['close'].diff(3)
        
        # Supertrend
        supertrend = df.ta.supertrend(length=7, multiplier=3)
        if supertrend is not None:
            df = pd.concat([df, supertrend], axis=1)

        return df

    @staticmethod
    def add_lag_features(df: pd.DataFrame, lags=[1, 5, 15]) -> pd.DataFrame:
        """Add lagged return features"""
        df = df.copy()
        df['returns'] = df['close'].pct_change()
        
        for lag in lags:
            df[f'return_lag_{lag}'] = df['returns'].shift(lag)
        
        return df
    
    @staticmethod
    def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        df = df.copy()
        
        # Ensure index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'timestamp' in df.columns:
                df.set_index('timestamp', inplace=True)
            elif 'date' in df.columns:
                df.set_index('date', inplace=True)
        
        if isinstance(df.index, pd.DatetimeIndex):
            df['hour'] = df.index.hour
            df['minute'] = df.index.minute
            df['day_of_week'] = df.index.dayofweek
            
            # Market session (Indian market: 9:15 AM - 3:30 PM)
            df['is_opening'] = ((df['hour'] == 9) & (df['minute'] < 30)).astype(int)
            df['is_closing'] = ((df['hour'] == 15) & (df['minute'] > 0)).astype(int)
        else:
            # Fallback if no datetime info
            df['hour'] = 0
            df['minute'] = 0
            df['day_of_week'] = 0
            df['is_opening'] = 0
            df['is_closing'] = 0
        
        return df
    
    @staticmethod
    def create_labels(df: pd.DataFrame, horizon=5, threshold=0.0015) -> pd.DataFrame:
        """Create labels for classification/regression"""
        df = df.copy()
        
        # Future return (5 candles ahead)
        df['future_return'] = df['close'].pct_change(horizon).shift(-horizon)
        
        # Binary label: 1 if return > threshold, 0 otherwise
        df['label_binary'] = (df['future_return'] > threshold).astype(int)
        
        # Regression label
        df['label_regression'] = df['future_return']
        
        return df
    
    @staticmethod
    def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
        """Full feature pipeline"""
        df = df.copy()
        
        # Ensure index is datetime for technical indicators (VWAP needs it)
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'timestamp' in df.columns:
                df.set_index('timestamp', inplace=True)
            elif 'date' in df.columns:
                df.set_index('date', inplace=True)

        df = FeatureEngine.add_technical_indicators(df)
        df = FeatureEngine.add_lag_features(df)
        df = FeatureEngine.add_time_features(df)
        df = FeatureEngine.create_labels(df)
        
        # Drop NaN rows
        
        # Check if any column is all NaN
        all_nan_cols = df.columns[df.isnull().all()].tolist()
        if all_nan_cols:
            # print(f"WARNING: Columns with all NaN: {all_nan_cols}")
            df = df.drop(columns=all_nan_cols)
            
        # Drop sparse columns from Supertrend if they exist (contain 'SUPERTl' or 'SUPERTs')
        sparse_cols = [c for c in df.columns if 'SUPERTl' in c or 'SUPERTs' in c]
        if sparse_cols:
            df = df.drop(columns=sparse_cols)
            
        df = df.dropna()
        
        return df
