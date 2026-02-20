import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised for Binance API-level errors (non-2xx or error code in body)."""
    pass


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> str:
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _server_time_offset(self) -> int:
        """Calculate offset between local time and Binance server time."""
        try:
            response = self.session.get(f"{BASE_URL}/fapi/v1/time", timeout=5)
            server_time = response.json()["serverTime"]
            return server_time - int(time.time() * 1000)
        except Exception:
            return 0

    def _timestamp(self) -> int:
        return int(time.time() * 1000) + self._server_time_offset()

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        url = f"{BASE_URL}{endpoint}"
        params = params or {}

        if signed:
            params["timestamp"] = self._timestamp()
            params["signature"] = self._sign(params)

        logger.debug("REQUEST  %s %s | params: %s", method.upper(), endpoint, params)

        try:
            response = self.session.request(method, url, params=params, timeout=10)
        except requests.exceptions.ConnectionError as e:
            logger.error("Network connection error: %s", e)
            raise BinanceClientError(f"Network connection error: {e}") from e
        except requests.exceptions.Timeout as e:
            logger.error("Request timed out: %s", e)
            raise BinanceClientError(f"Request timed out: {e}") from e
        except requests.exceptions.RequestException as e:
            logger.error("Request failed: %s", e)
            raise BinanceClientError(f"Request failed: {e}") from e

        logger.debug("RESPONSE %s %s | status: %s | body: %s", method.upper(), endpoint, response.status_code, response.text)

        try:
            data = response.json()
        except ValueError:
            logger.error("Non-JSON response: %s", response.text)
            raise BinanceClientError(f"Non-JSON response received: {response.text}")

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            logger.error("API error — code: %s | msg: %s", data.get("code"), data.get("msg"))
            raise BinanceClientError(f"API error {data.get('code')}: {data.get('msg')}")

        if not response.ok:
            logger.error("HTTP error %s | body: %s", response.status_code, response.text)
            raise BinanceClientError(f"HTTP {response.status_code}: {response.text}")

        return data

    # ------------------------------------------------------------------
    # Public endpoints
    # ------------------------------------------------------------------

    def ping(self) -> bool:
        """Test connectivity."""
        self._request("GET", "/fapi/v1/ping")
        return True

    def get_exchange_info(self) -> dict:
        return self._request("GET", "/fapi/v1/exchangeInfo")

    # ------------------------------------------------------------------
    # Order endpoints
    # ------------------------------------------------------------------

    def place_order(self, params: dict) -> dict:
        return self._request("POST", "/fapi/v1/order", params=params, signed=True)

    def get_order(self, symbol: str, order_id: int) -> dict:
        return self._request(
            "GET",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )
