# API Documentation

Base URL: `http://localhost:8000/api/v1`

## Authentication

### POST /auth/login
Login and get access token.

**Request:**
```json
{
  "username": "admin@example.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

Use token in subsequent requests:
```
Authorization: Bearer <token>
```

## Market Data

### GET /market/tick?symbol=NIFTY
Get current tick data.

**Response:**
```json
{
  "symbol": "NIFTY",
  "timestamp": "2023-12-01T10:30:00Z",
  "last": 19500.50,
  "open": 19480.00,
  "high": 19520.00,
  "low": 19470.00,
  "close": 19500.50,
  "volume": 5000
}
```

### GET /market/history
Get historical OHLCV data.

**Query params:**
- `symbol`: NIFTY, BANKNIFTY
- `interval`: 1m, 5m, 15m, 1h, 1d
- `from_date`: ISO datetime
- `to_date`: ISO datetime

## Orders

### POST /orders
Create new order.

**Request:**
```json
{
  "symbol": "NIFTY",
  "side": "buy",
  "type": "market",
  "qty": 1,
  "price": null,
  "strategy_id": 1
}
```

**Response:**
```json
{
  "id": 123,
  "ext_id": "abc-123",
  "symbol": "NIFTY",
  "side": "buy",
  "type": "market",
  "qty": 1,
  "filled_qty": 1,
  "status": "filled"
}
```

### GET /orders
List user orders (last 100).

### GET /orders/{id}
Get order details.

## Positions

### GET /positions
List open positions.

**Response:**
```json
[
  {
    "id": 1,
    "symbol": "NIFTY",
    "side": "buy",
    "qty": 1,
    "avg_price": 19500.00,
    "current_price": 19520.00,
    "unrealized_pnl": 20.00
  }
]
```

## Wallet

### GET /wallet
Get wallet balance.

**Response:**
```json
{
  "total_balance": 100000.00,
  "reserved_balance": 19500.00,
  "available_balance": 80500.00
}
```

### POST /wallet/deposit
Deposit funds (admin only).

**Request:**
```json
{
  "amount": 50000.00
}
```

## Strategies

### GET /strategies
List all strategies.

### POST /strategies/{id}/deploy
Deploy strategy (admin only).

## WebSocket

Connect to `ws://localhost:8000/ws/updates` for real-time updates.

**Message format:**
```json
{
  "type": "order_update",
  "data": {
    "order_id": 123,
    "status": "filled"
  }
}
```
