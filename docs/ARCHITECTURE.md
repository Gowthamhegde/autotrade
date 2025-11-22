# Architecture Overview

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  Dashboard | Charts | Orders | Positions | Wallet | Admin   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API / WebSocket
┌────────────────────────┴────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │  Market  │  │  Orders  │  │  Wallet  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
│   Execution  │  │  ML Engine  │  │  Database  │
│    Engine    │  │             │  │ PostgreSQL │
│              │  │  Features   │  │   Redis    │
│  ┌────────┐  │  │  Training   │  └────────────┘
│  │ Broker │  │  │  Inference  │
│  │Adapters│  │  │  Backtest   │
│  └────────┘  │  └─────────────┘
│  Mock/Zerodha│
│  Upstox/IB   │
└──────────────┘
```

## Data Flow

### Order Execution Flow
1. User places order via UI
2. API validates order & checks wallet balance
3. Execution engine routes to broker adapter
4. Broker places order (mock/real)
5. Order status updates via WebSocket
6. Fills update positions & wallet ledger

### ML Prediction Flow
1. Data ingestion: OHLCV → Parquet/DB
2. Feature engineering: Technical indicators, lags, time features
3. Model training: XGBoost/LSTM with walk-forward CV
4. Model versioning: MLflow tracking
5. Inference: Real-time feature computation → prediction
6. Signal generation: Threshold-based buy/sell signals
7. Order placement: Via execution engine

### Wallet & Ledger Flow
1. Deposit: Admin adds funds → ledger entry
2. Order placed: Reserve margin → hold entry
3. Order filled: Debit cost → trade entry
4. Position closed: Credit P&L → trade entry
5. Fees/taxes: Deduct → fee/tax entries

## Database Schema

### Core Tables
- `users`: User accounts with roles
- `wallets`: Per-user balance tracking
- `ledger`: Immutable transaction log
- `orders`: Order lifecycle tracking
- `trades`: Fill-level details
- `positions`: Open position tracking
- `strategies`: Strategy configs
- `models`: ML model metadata

### Time-Series Data
- Stored in Parquet files or ClickHouse
- Indexed by symbol + timestamp
- Partitioned by date for fast queries

## Security

### Authentication
- JWT tokens with expiry
- Role-based access control (admin/trader/viewer)
- Password hashing with bcrypt

### Secrets Management
- API keys stored in environment variables
- Production: Use Vault or AWS Secrets Manager
- Never commit secrets to repo

### Risk Controls
- Position size limits
- Daily loss limits
- Circuit breakers on large drawdowns
- Manual kill-switch

## Scalability

### Horizontal Scaling
- Stateless API servers behind load balancer
- Redis for session/cache
- PostgreSQL read replicas for analytics

### Performance
- WebSocket for real-time updates (avoid polling)
- Feature caching in Redis
- Async I/O for broker API calls
- Database connection pooling

## Monitoring

### Metrics (Prometheus)
- API latency, throughput
- Order fill rates
- Model prediction latency
- Database query performance

### Alerts (Telegram/Email)
- Order failures
- Large drawdowns
- System errors
- Model drift detection

### Logging (ELK/Loki)
- Structured JSON logs
- Request/response tracing
- Error stack traces
- Audit trail for compliance
