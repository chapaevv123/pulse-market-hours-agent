from __future__ import annotations

import json
import os
import urllib.error

from market_hours_agent.binance_web3 import BinanceWeb3Client


def main() -> int:
    client = BinanceWeb3Client(os.environ["BINANCE_WEB3_API_KEY"], os.environ["BINANCE_WEB3_SECRET_KEY"])
    try:
        result = client.search_rwa("NVDA")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        try:
            payload = json.loads(body)
            safe = {"http_status": exc.code, "code": payload.get("code"),
                    "message": payload.get("msg") or payload.get("message")}
        except json.JSONDecodeError:
            safe = {"http_status": exc.code, "body_kind": "non_json", "body_length": len(body)}
        print(json.dumps(safe))
        return 1
    rows = result.get("data") or []
    safe = {"success": result.get("success"), "code": result.get("code"),
            "server_timestamp": result.get("timestamp"), "matches": len(rows),
            "bsc_assets": sum(1 for row in rows for asset in row.get("assets", [])
                              if str(asset.get("binanceChainId")) == "56")}
    print(json.dumps(safe))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

