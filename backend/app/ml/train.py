import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, roc_auc_score
import xgboost as xgb
import mlflow
import mlflow.xgboost
from app.ml.features import FeatureEngine

class ModelTrainer:
    """Train and evaluate ML models"""
    
    def __init__(self, experiment_name="nifty_trading"):
        mlflow.set_experiment(experiment_name)
        self.feature_cols = None
    
    def train_random_forest(self, df: pd.DataFrame):
        """Train Random Forest classifier with high confidence threshold"""
        from sklearn.ensemble import RandomForestClassifier
        
        # Prepare features
        print(f"Data shape before features: {df.shape}")
        df = FeatureEngine.prepare_features(df)
        print(f"Data shape after features: {df.shape}")
        
        if df.empty:
            raise ValueError("Dataframe is empty after feature engineering")
        
        # Feature columns
        exclude_cols = ['label_binary', 'label_regression', 'future_return', 'returns']
        self.feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[self.feature_cols]
        y = df['label_binary']
        
        # Train/Test Split
        tscv = TimeSeriesSplit(n_splits=5)
        
        scores = []
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate only high confidence predictions (>0.8 or <0.2)
            probs = model.predict_proba(X_val)[:, 1]
            
            # Create a mask for high confidence
            high_conf_mask = (probs > 0.7) | (probs < 0.3)
            
            if sum(high_conf_mask) > 0:
                y_val_conf = y_val[high_conf_mask]
                y_pred_conf = (probs[high_conf_mask] > 0.5).astype(int)
                acc = accuracy_score(y_val_conf, y_pred_conf)
                scores.append(acc)
                print(f"Fold High Confidence Accuracy: {acc:.4f} (Trades: {sum(high_conf_mask)})")
            else:
                print("Fold: No high confidence trades")
        
        avg_acc = np.mean(scores) if scores else 0
        print(f"Average High Confidence Accuracy: {avg_acc:.4f}")
        
        # Train final model
        final_model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
        final_model.fit(X, y)
        
        # Save model to disk
        import joblib
        joblib.dump(final_model, "model.pkl")
        print("Model saved to model.pkl")
        
        return final_model, avg_acc

    def train_model(self, symbol: str = "^NSEI", period: str = "2y"):
        """Train model for a specific symbol"""
        from app.services.data_loader import DataLoader
        
        print(f"Loading data for {symbol}...")
        df = DataLoader.fetch_history(symbol, period=period)
        
        print(f"Training model on {len(df)} rows...")
        model, acc = self.train_random_forest(df)
        
        return model, acc

if __name__ == "__main__":
    trainer = ModelTrainer()
    # Train on NIFTY 50
    model, auc = trainer.train_model("^NSEI")
    print(f"Final NIFTY 50 Model AUC: {auc:.4f}")
