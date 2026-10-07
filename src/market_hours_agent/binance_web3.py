from __future__ import annotations

import base64
import hashlib
import hmac
import json
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from typing import Any


class BinanceWeb3Client:
    """Small signed, read-only client. It never broadcasts or signs wallet transactions."""

    base_url = "https://web3.binance.com/build"

    def __init__(self, api_key: str, secret_key: str, *, timeout: float = 10.0) -> None:
        if not api_key or not secret_key:
            raise ValueError("API credentials are required")
        self.api_key = api_key
        self.secret_key = secret_key
        self.timeout = timeout

    @staticmethod
    def _timestamp() -> str:
        now = datetime.now(UTC)
        return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"

    def signed_headers(self, method: str, request_path: str, body: str = "", *, timestamp: str | None = None) -> dict[str, str]:
        timestamp = timestamp or self._timestamp()
        if not request_path.startswith("/build/"):
            raise ValueError("Signed request path must include /build")
        pre_hash = timestamp + method.upper() + request_path + body
        signature = base64.b64encode(
            hmac.new(self.secret_key.encode(), pre_hash.encode(), hashlib.sha256).digest()
        ).decode()
        return {"X-OC-APIKEY": self.api_key, "X-OC-TIMESTAMP": timestamp, "X-OC-SIGN": signature,
                "X-OC-RECV-WINDOW": "60000"}

    def get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        full_path = f"{path}?{query}" if query else path
        signed_path = "/build" + full_path
        request = urllib.request.Request(
            self.base_url + full_path,
            headers=self.signed_headers("GET", signed_path),
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode())
        if payload.get("code") != 0 or not payload.get("success"):
            raise RuntimeError(f"Binance Web3 API error: {payload.get('code')} {payload.get('msg')}")
        return payload

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        signed_path = "/build" + path
        request = urllib.request.Request(
            self.base_url + path,
            data=body.encode(),
            headers={**self.signed_headers("POST", signed_path, body), "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            result = json.loads(response.read().decode())
        if result.get("code") != 0 or not result.get("success"):
            raise RuntimeError(f"Binance Web3 API error: {result.get('code')} {result.get('msg')}")
        return result

    def search_rwa(self, keyword: str, platform: str | None = None) -> dict[str, Any]:
        params = {"keyword": keyword}
        if platform:
            params["platformId"] = platform
        return self.get("/api/v1/dex/market/rwa/search", params)

    def rwa_prices(self, token_addresses: list[str], chain_id: str = "56") -> dict[str, Any]:
        return self.get(
            "/api/v1/dex/market/rwa/price",
            {"binanceChainId": chain_id, "tokenContractAddresses": ",".join(token_addresses)},
        )

    def underlying_market(self, token_address: str, chain_id: str = "56") -> dict[str, Any]:
        return self.get(
            "/api/v1/dex/market/rwa/underlying-market",
            {"binanceChainId": chain_id, "tokenContractAddress": token_address},
        )

    def quote(
        self, from_token: str, to_token: str, amount_atomic: str, wallet_address: str, chain_id: str = "56"
    ) -> dict[str, Any]:
        return self.get(
            "/api/v1/dex/aggregator/quote",
            {"binanceChainId": chain_id, "amount": amount_atomic, "fromTokenAddress": from_token,
             "toTokenAddress": to_token, "userWalletAddress": wallet_address},
        )

    def build_swap(
        self, from_token: str, to_token: str, amount_atomic: str, wallet_address: str,
        quote_id: str, *, slippage_percent: str = "0.5", chain_id: str = "56",
    ) -> dict[str, Any]:
        """Prepare a swap payload without signing or broadcasting it."""
        return self.get(
            "/api/v1/dex/aggregator/swap",
            {"binanceChainId": chain_id, "amount": amount_atomic, "fromTokenAddress": from_token,
             "toTokenAddress": to_token, "userWalletAddress": wallet_address, "quoteId": quote_id,
             "slippagePercent": slippage_percent},
        )

    def wallet_balances(self, wallet_address: str, chain_id: str = "56") -> dict[str, Any]:
        return self.get(
            "/api/v1/dex/balance/all-token-balances-by-address",
            {"address": wallet_address, "chains": chain_id, "excludeRiskToken": "true",
             "page": "1", "pageSize": "100"},
        )

    def simulate_evm(self, transaction: dict[str, str], chain_id: str = "56") -> dict[str, Any]:
        """Off-chain prediction only. This method cannot sign or broadcast."""
        allowed = {key: transaction[key] for key in ("from", "to", "value", "data") if key in transaction}
        if set(allowed) != {"from", "to", "value", "data"}:
            raise ValueError("Simulation requires from, to, value and data")
        return self.post("/api/v1/dex/pre-transaction/simulate", {"binanceChainId": chain_id, "evmTx": allowed})
