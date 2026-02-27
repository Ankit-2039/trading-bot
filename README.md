# Binance Futures Testnet - Trading Bot

A lightweight Python CLI trading bot for placing orders on Binance Futures Testnet (USDT-M).


---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper
│   ├── orders.py          # Order placement logic & response formatting
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Structured logging setup
├── logs/                  # Auto-created log files
├── cli.py                 # CLI entry point
├── .env.example           # Credentials template
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ankit-2039/trading-bot.git
cd trading-bot
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your Binance Futures Testnet credentials:

```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

Get credentials at: https://testnet.binancefuture.com (login with GitHub → generate API key)

> **Note:** Minimum order notional is $100. Use quantity `0.002` for BTCUSDT.

---

## How to Run

### Market Order — BUY
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

### Market Order — SELL
```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.002
```

### Limit Order — BUY
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.002 --price 85000
```

### Limit Order — SELL
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 99000
```

### Stop-Market Order *(bonus — third order type)*
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.002 --price 95000
```

---

## CLI Arguments

| Argument     | Required | Description                                          |
|-------------|----------|------------------------------------------------------|
| `--symbol`   | Yes      | Trading pair (e.g., `BTCUSDT`, `ETHUSDT`)           |
| `--side`     | Yes      | `BUY` or `SELL`                                     |
| `--type`     | Yes      | `MARKET`, `LIMIT`, or `STOP_MARKET`                 |
| `--quantity` | Yes      | Order quantity (positive number)                     |
| `--price`    | Cond.    | Required for `LIMIT` and `STOP_MARKET` orders       |

---

## Sample Output

```
==================================================
         ORDER REQUEST SUMMARY
==================================================
  Symbol      : BTCUSDT
  Side        : BUY
  Order Type  : MARKET
  Quantity    : 0.002
==================================================

INFO: Placing BUY MARKET order | symbol=BTCUSDT | qty=0.002 | price=N/A (MARKET)
INFO: Order placed successfully | orderId=12414382768 | status=NEW | executedQty=0.000 | avgPrice=0.00

==================================================
         ORDER RESPONSE
==================================================
  Order ID    : 12414382768
  Symbol      : BTCUSDT
  Side        : BUY
  Type        : MARKET
  Status      : NEW
  Quantity    : 0.002
  Executed    : 0.000
  Avg Price   : 0.00
  Price       : 0.00
  Time        : 1771584666934
==================================================

[SUCCESS] Order placed successfully!
```

---

## Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log`.

Each entry includes timestamp, log level, module name, and message. Captures:
- All API requests with full params
- All API responses with full body
- Validation errors (before any API call)
- API errors with Binance error code and message
- Network failures

Console shows `INFO` and above. Log file captures full `DEBUG` detail.

---

## Error Handling

| Scenario             | Behavior                                        |
|---------------------|-------------------------------------------------|
| Invalid side/type   | Validation error, no API call made              |
| Missing price       | Validation error for LIMIT/STOP_MARKET          |
| Invalid quantity    | Validation error (must be positive number)      |
| API key error       | Caught and logged with Binance error code       |
| Timestamp mismatch  | Auto-corrected using Binance server time        |
| Network failure     | Caught with descriptive error message           |
| Non-JSON response   | Caught and logged                               |

---

## Assumptions

- Testnet base URL: `https://testnet.binancefuture.com`
- All orders use USDT-M perpetual futures
- LIMIT orders default to `timeInForce=GTC` (Good-Till-Cancel)
- Minimum notional value is $100 (Binance requirement) — use qty `0.002` for BTCUSDT
- Credentials loaded from `.env` file — never hardcoded in source
- Timestamp synced with Binance server time to avoid clock skew errors
- Python 3.8+ required
