from typing import Optional

from bot.client import BinanceFuturesClient, BinanceClientError
from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.orders")


def build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> dict:
    """Build the parameter dict for the Binance order endpoint."""
    params: dict = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        params["price"] = price
        params["timeInForce"] = "GTC"  # Good-Till-Cancel

    elif order_type == "STOP_MARKET":
        if price is None:
            raise ValueError("Stop price is required for STOP_MARKET orders.")
        params["stopPrice"] = price

    return params


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> dict:
    params = build_order_params(symbol, side, order_type, quantity, price)

    logger.info(
        "Placing %s %s order | symbol=%s | qty=%s | price=%s",
        side,
        order_type,
        symbol,
        quantity,
        price if price is not None else "N/A (MARKET)",
    )

    response = client.place_order(params)

    logger.info(
        "Order placed successfully | orderId=%s | status=%s | executedQty=%s | avgPrice=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
        response.get("avgPrice"),
    )

    return response


def format_order_response(response: dict) -> str:
    """Return a human-readable summary of an order response."""
    lines = [
        "",
        "=" * 50,
        "         ORDER RESPONSE",
        "=" * 50,
        f"  Order ID    : {response.get('orderId', 'N/A')}",
        f"  Symbol      : {response.get('symbol', 'N/A')}",
        f"  Side        : {response.get('side', 'N/A')}",
        f"  Type        : {response.get('type', 'N/A')}",
        f"  Status      : {response.get('status', 'N/A')}",
        f"  Quantity    : {response.get('origQty', 'N/A')}",
        f"  Executed    : {response.get('executedQty', 'N/A')}",
        f"  Avg Price   : {response.get('avgPrice', 'N/A')}",
        f"  Price       : {response.get('price', 'N/A')}",
        f"  Time        : {response.get('updateTime', 'N/A')}",
        "=" * 50,
    ]
    return "\n".join(lines)
