@echo off
echo Starting NIFTY AutoTrader Backend...
cd backend
python init_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
