#!/usr/bin/env python3
"""
Trading Bot CLI — Binance Futures Testnet (USDT-M)

Usage examples:
  # Market BUY
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Limit SELL
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 99000

  # Stop-Market BUY (bonus order type)
  python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --price 95000
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceFuturesClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import place_order, format_order_response
from bot.validators import validate_all, ValidationError

load_dotenv()
logger = setup_logger("trading_bot.cli")


def print_request_summary(symbol: str, side: str, order_type: str, quantity: float, price=None):
    print("\n" + "=" * 50)
    print("         ORDER REQUEST SUMMARY")
    print("=" * 50)
    print(f"  Symbol      : {symbol}")
    print(f"  Side        : {side}")
    print(f"  Order Type  : {order_type}")
    print(f"  Quantity    : {quantity}")
    if price is not None:
        label = "Stop Price" if order_type == "STOP_MARKET" else "Price"
        print(f"  {label:<12}: {price}")
    print("=" * 50)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--symbol",   required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",     required=True, help="BUY or SELL")
    parser.add_argument("--type",     required=True, dest="order_type", help="MARKET, LIMIT, or STOP_MARKET")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price",    required=False, default=None, help="Price (required for LIMIT/STOP_MARKET)")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # ── Validate inputs ──────────────────────────────────────────────
    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as e:
        logger.error("Validation failed: %s", e)
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    symbol     = validated["symbol"]
    side       = validated["side"]
    order_type = validated["order_type"]
    quantity   = validated["quantity"]
    price      = validated["price"]

    # ── Load credentials ─────────────────────────────────────────────
    api_key    = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        msg = (
            "API credentials not found. "
            "Set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file or environment."
        )
        logger.error(msg)
        print(f"\n[ERROR] {msg}")
        sys.exit(1)

    # ── Print request summary ─────────────────────────────────────────
    print_request_summary(symbol, side, order_type, quantity, price)

    # ── Initialize client & place order ──────────────────────────────
    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

        # Quick connectivity check
        logger.debug("Pinging Binance Futures Testnet...")
        client.ping()

        response = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )

    except BinanceClientError as e:
        logger.error("Order failed: %s", e)
        print(f"\n[FAILED] Order could not be placed.\nReason: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)

    # ── Print response ────────────────────────────────────────────────
    print(format_order_response(response))
    print("\n[SUCCESS] Order placed successfully!\n")
    logger.info("Session complete.")


if __name__ == "__main__":
    main()
