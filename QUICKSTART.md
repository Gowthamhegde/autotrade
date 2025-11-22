# Quick Start (Without Docker)

## Step 1: Install Backend Dependencies

Open a terminal and run:

```bash
cd backend
pip install -r requirements.txt
```

**Note:** TA-Lib installation might fail on Windows. If it does, you can skip it for now (the system will work without it, but some technical indicators won't be available).

## Step 2: Initialize Database

```bash
python init_db.py
```

This creates a SQLite database with a demo user.

## Step 3: Start Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or simply double-click `start_backend.bat`

The API will be available at: http://localhost:8000

## Step 4: Start Frontend

Open a **new terminal** and run:

```bash
cd frontend
npm install
npm run dev
```

Or simply double-click `start_frontend.bat`

The dashboard will be available at: http://localhost:3000

## Step 5: Login

Open http://localhost:3000 in your browser and login with:
- **Email:** admin@example.com
- **Password:** admin123

## What You'll See

- **Real-time price chart** for NIFTY (mock data)
- **Wallet balance** (₹100,000 demo funds)
- **Positions panel** (empty initially)
- **Orders panel** (empty initially)
- **Paper/Live toggle** (stays in Paper mode for safety)

## Try It Out

The system is running in **mock mode** — all orders are simulated, no real money involved.

You can:
- View live price updates
- Check your wallet balance
- See positions and orders (once you place some)

## Troubleshooting

**TA-Lib installation fails:**
- Skip it for now: `pip install -r requirements.txt --no-deps` then manually install packages except ta-lib
- Or use: `pip install TA-Lib-Precompiled` (Windows wheel)

**Port already in use:**
- Backend: Change port in start command: `--port 8001`
- Frontend: It will auto-detect and suggest port 3001

**Database errors:**
- Delete `autotrader.db` and run `python init_db.py` again

## Next Steps

1. Explore the Jupyter notebooks in `notebooks/`
2. Add real NSE data to `data/raw/`
3. Train ML models
4. Configure Zerodha/Upstox when ready for live trading

## Installing Docker (Optional)

If you want to use Docker later:
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and restart your computer
3. Run: `docker compose up -d`
