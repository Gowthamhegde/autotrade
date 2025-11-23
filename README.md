# NIFTY AutoTrader

A full-stack automated trading bot for Indian Markets (NIFTY 50, BANK NIFTY) featuring an AI-driven prediction engine, real-time dashboard, and paper trading simulation.

## 🚀 Features

- **AI/ML Engine**: Random Forest Classifier trained on historical data to predict market direction with high-confidence filtering.
- **Real-time Dashboard**: Next.js + Tailwind CSS UI displaying live prices, charts, and account stats.
- **Paper Trading**: Fully simulated broker environment with wallet management and order execution.
- **Wallet System**: Deposit virtual funds and track your balance.
- **Trade History**: View logs of all executed trades.

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python, SQLAlchemy, Pandas-TA, Scikit-Learn.
- **Frontend**: Next.js, React, Recharts, Tailwind CSS.
- **Data**: `yfinance` for real-time and historical market data.
- **Database**: SQLite (local).

## 🏃‍♂️ How to Run

### 1. Start the Backend
The backend runs on port `8005`.
```bash
cd backend
# Install dependencies (if not done)
# pip install -r requirements.txt
uvicorn app.main:app --reload --port 8005
```

### 2. Start the Frontend
The frontend runs on port `3001`.
```bash
cd frontend
# Install dependencies (if not done)
# npm install
npx next dev -p 3001
```

### 3. Access the App
Open your browser and navigate to:
**http://localhost:3001**

## 📖 Usage Guide

1.  **Add Funds**: Click the "Add Funds" button in the top right to deposit virtual capital.
2.  **Select Index**: Choose between `NIFTY 50` or `BANK NIFTY`.
3.  **Start Trading**: Click "Start Trading". The bot will begin monitoring the market.
4.  **Watch**: The chart will update in real-time. When the ML model detects a high-confidence opportunity (>70%), it will execute a trade.
5.  **Review**: Check the "Recent Trades" section to see buy/sell actions.

## 🤖 ML Model Details

- **Algorithm**: Random Forest Classifier.
- **Features**: VWAP, Supertrend, RSI, MACD, Bollinger Bands.
- **Logic**: Only takes trades when prediction probability is > 0.7 (Buy) or < 0.3 (Sell).
