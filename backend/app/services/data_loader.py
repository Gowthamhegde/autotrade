import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional

class DataLoader:
    """Service to load market data from yfinance"""
    
    @staticmethod
    def fetch_history(symbol: str, period: str = "2y", interval: str = "1h") -> pd.DataFrame:
        """
        Fetch historical data for a symbol
        
        Args:
            symbol: Ticker symbol (e.g., ^NSEI for NIFTY 50, RELIANCE.NS)
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        """
        # Add .NS suffix if not present and not an index
        if not symbol.startswith("^") and not symbol.endswith(".NS"):
            symbol = f"{symbol}.NS"
            
        print(f"Fetching data for {symbol}...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            raise ValueError(f"No data found for symbol {symbol}")
            
        # Reset index to make Date/Datetime a column
        df.reset_index(inplace=True)
        
        # Standardize column names to lowercase
        df.columns = [c.lower() for c in df.columns]
        
        # Ensure timestamp column exists and is timezone-naive for compatibility
        if 'date' in df.columns:
            df.rename(columns={'date': 'timestamp'}, inplace=True)
        elif 'datetime' in df.columns:
            df.rename(columns={'datetime': 'timestamp'}, inplace=True)
            
        # Remove timezone info if present
        if pd.api.types.is_datetime64_any_dtype(df['timestamp']):
             df['timestamp'] = df['timestamp'].dt.tz_localize(None)

        return df

    @staticmethod
    def get_indian_indices() -> List[str]:
        return ["^NSEI", "^NSEBANK"] # NIFTY 50, NIFTY BANK

    @staticmethod
    def get_top_stocks() -> List[str]:
        # Top 10 NIFTY 50 stocks by weightage (approx)
        return [
            "HDFCBANK.NS", "RELIANCE.NS", "ICICIBANK.NS", "INFY.NS", 
            "ITC.NS", "TCS.NS", "L&T.NS", "AXISBANK.NS", "KOTAKBANK.NS", "SBIN.NS"
        ]
