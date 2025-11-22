from app.services.data_loader import DataLoader
from app.ml.features import FeatureEngine
import pandas as pd

def debug():
    print("Fetching data...")
    df = DataLoader.fetch_history("^NSEI", period="2y")
    print(f"Fetched shape: {df.shape}")
    print(df.head())
    print(df.tail())
    
    print("\nApplying features...")
    df_feat = FeatureEngine.add_technical_indicators(df)
    print(f"Shape after tech indicators: {df_feat.shape}")
    print("NaN counts after tech indicators:")
    print(df_feat.isnull().sum())
    
    df_feat = FeatureEngine.add_lag_features(df_feat)
    df_feat = FeatureEngine.add_time_features(df_feat)
    df_feat = FeatureEngine.create_labels(df_feat)
    
    print(f"\nShape before dropna: {df_feat.shape}")
    print("NaN counts before dropna:")
    print(df_feat.isnull().sum())
    
    df_final = df_feat.dropna()
    print(f"\nShape after dropna: {df_final.shape}")

if __name__ == "__main__":
    debug()
