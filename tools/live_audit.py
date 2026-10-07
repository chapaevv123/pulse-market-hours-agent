from __future__ import annotations

import json
import os
import time
import urllib.error

from market_hours_agent.binance_web3 import BinanceWeb3Client
from market_hours_agent.engine import evaluate
from market_hours_agent.live import collect_live_snapshot

USDT_BSC = "0x55d398326f99059fF775485246999027B3197955"


def main() -> int:
    started = time.perf_counter()
    client = BinanceWeb3Client(os.environ["BINANCE_WEB3_API_KEY"], os.environ["BINANCE_WEB3_SECRET_KEY"], timeout=30)
    try:
        snapshot = collect_live_snapshot(
            client, ticker="NVDA", wallet_address=os.environ["PULSE_WALLET_ADDRESS"],
            from_token=USDT_BSC, amount_atomic="10000000000000000000", trade_notional_usd=10.0,
        )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        try:
            payload = json.loads(body)
            error = {"http_status": exc.code, "code": payload.get("code"),
                     "message": payload.get("msg") or payload.get("message")}
        except json.JSONDecodeError:
            error = {"http_status": exc.code, "body_kind": "non_json", "body_length": len(body)}
        print(json.dumps({"success": False, "error": error, "elapsed_seconds": round(time.perf_counter() - started, 2)}))
        return 1
    except (RuntimeError, ValueError, TimeoutError, OSError) as exc:
        print(json.dumps({"success": False, "error_type": type(exc).__name__, "message": str(exc)[:300],
                          "elapsed_seconds": round(time.perf_counter() - started, 2)}))
        return 1
    receipt = evaluate(snapshot)
    safe = {
        "success": True, "elapsed_seconds": round(time.perf_counter() - started, 2),
        "asset": receipt.asset, "tokenized_asset": receipt.tokenized_asset, "chain": receipt.chain,
        "reference_price_present": receipt.reference_price is not None,
        "reference_provenance": receipt.reference_provenance,
        "onchain_price_present": receipt.onchain_price is not None,
        "market_state": receipt.market_state, "liquidity_present": receipt.liquidity_usd is not None,
        "slippage_present": receipt.slippage_pct is not None,
        "execution_cost_present": receipt.execution_cost_usd is not None,
        "wallet_readiness": receipt.wallet_readiness, "simulation_result": receipt.simulation_result,
        "simulation_fail_reason": receipt.simulation_fail_reason,
        "execution_mode": next((item.value.get("executionMode") for item in snapshot.evidence
                                if item.field == "prepared_action" and isinstance(item.value, dict)), None),
        "evidence_items": len(snapshot.evidence), "evidence_completeness": receipt.evidence_completeness,
        "decision": receipt.decision.value, "critical_unknowns": list(receipt.critical_unknowns),
        "receipt_id": receipt.receipt_id, "receipt_hash": receipt.receipt_hash,
    }
    print(json.dumps(safe))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
