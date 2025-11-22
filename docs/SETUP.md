# Setup Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend development)

## Quick Start

1. **Clone the repository**
```bash
git clone <repo-url>
cd nifty-autotrader
```

2. **Start services**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Frontend UI (port 3000)

3. **Access the dashboard**
```
http://localhost:3000
```

Demo credentials:
- Email: `admin@example.com`
- Password: `admin123`

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy env file
cp .env.example .env

# Run migrations (if using Alembic)
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Configuration

Edit `backend/.env` for:
- Database connection
- Broker mode (mock/zerodha/upstox)
- API keys (store in secrets manager for production)
- Risk limits

## Broker Setup

### Mock Mode (Default)
No setup needed. Simulates orders locally.

### Zerodha Kite Connect
1. Register at https://kite.trade/
2. Get API key & secret
3. Set in `.env`:
```
BROKER_MODE=zerodha
ZERODHA_API_KEY=your_key
ZERODHA_API_SECRET=your_secret
```

## Data Ingestion

Place historical data in `data/raw/` as Parquet files:
```
data/raw/NIFTY_1m_2023.parquet
data/raw/BANKNIFTY_1m_2023.parquet
```

Or use the data ingestion script:
```bash
python backend/scripts/ingest_data.py --symbol NIFTY --start 2023-01-01 --end 2023-12-31
```

## Model Training

```bash
cd notebooks
jupyter notebook 02_model_training.ipynb
```

Or via CLI:
```bash
python backend/scripts/train_model.py --data data/processed/features.parquet
```

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Production Deployment

See [docs/DEPLOYMENT.md](DEPLOYMENT.md) for Kubernetes setup.

## Troubleshooting

**Database connection error:**
- Check PostgreSQL is running: `docker ps`
- Verify DATABASE_URL in `.env`

**TA-Lib installation fails:**
- Install system dependencies first (see Dockerfile)

**Frontend can't connect to API:**
- Check NEXT_PUBLIC_API_URL in frontend/.env
- Verify CORS settings in backend
