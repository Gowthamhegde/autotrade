# NIFTY F&O AutoTrader

ML-driven algorithmic trading platform for Indian derivatives (NIFTY & BankNIFTY futures & options).

## Features

- **Data Pipeline**: Ingest & store OHLCV + options chain data
- **ML Engine**: XGBoost/LSTM models with feature engineering & MLflow tracking
- **Backtester**: Event-driven simulation with realistic costs
- **Execution**: Pluggable broker adapters (Zerodha/Upstox/IB) with mock mode
- **Wallet & Ledger**: Margin management, P&L settlement, audit trail
- **Dashboard**: Real-time positions, orders, P&L, risk metrics
- **Risk Controls**: Position limits, circuit breakers, kill-switch

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd nifty-autotrader

# Start services (PostgreSQL, API, UI)
docker-compose up -d

# Access dashboard
open http://localhost:3000
```

## Architecture

```
├── backend/          # FastAPI services
│   ├── api/         # REST endpoints
│   ├── core/        # Business logic
│   ├── ml/          # Model training & inference
│   └── brokers/     # Broker adapters
├── frontend/        # React dashboard
├── data/            # Data ingestion & storage
├── notebooks/       # Research & analysis
└── infra/          # Docker, K8s configs
```

## Development

See [docs/SETUP.md](docs/SETUP.md) for detailed setup instructions.

**Default mode**: Paper trading (sandbox). No real money at risk.

## Security

- API keys stored in secrets manager (never in code)
- JWT authentication with RBAC
- Audit logs for all trades
- Manual approval required for live trading

## License

MIT
