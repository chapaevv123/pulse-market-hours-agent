from __future__ import annotations

from .models import EvidenceItem, EvidenceSnapshot, MarketStatus, Readiness, ReferenceSourceType

DOC = "https://web3.binance.com/en/dev-docs/catalog/web3-wallet/api/rest-api/rwa-data"
QUOTE = "https://web3.binance.com/en/dev-docs/catalog/web3-wallet/api/rest-api/trading-api"
SIM = "https://web3.binance.com/en/dev-docs/catalog/web3-wallet/api/rest-api/transaction-api"
CAPTURED = "2026-10-07T13:30:15Z"

EXPECTED = {
    "healthy": "ACT", "fresh_reference": "ACT", "market_open": "ACT",
    "stale_reference": "WAIT", "closed": "WAIT", "premarket": "WAIT", "after_hours": "WAIT",
    "derived_only": "INVESTIGATE", "conflict": "INVESTIGATE", "missing": "INVESTIGATE",
    "source_unavailable": "INVESTIGATE", "malformed_timestamp": "INVESTIGATE",
    "thin": "AVOID", "high_slippage": "AVOID", "high_gas": "AVOID",
    "failed_simulation": "AVOID", "simulation_timeout": "INVESTIGATE",
    "wallet_low_gas": "AVOID", "wallet_wrong_network": "AVOID", "quote_stale": "WAIT",
    "false_arbitrage": "AVOID", "stale_onchain": "WAIT",
}


def scenario(name: str) -> EvidenceSnapshot:
    base = {
        "captured_at": CAPTURED, "symbol": "NVDA", "tokenized_asset": "NVDAon",
        "token_address": "0xa9ee28c80f960b889dfbd1902055218cba016f75", "reference_asset": "NVDA",
        "reference_price": 180.00, "reference_price_timestamp": "2026-10-07T13:30:00Z",
        "reference_source_type": ReferenceSourceType.DERIVED_RWA_REFERENCE,
        "reference_corroborated": True, "reference_staleness_seconds": 15,
        "onchain_price": 181.26, "onchain_price_timestamp": "2026-10-07T13:30:10Z",
        "onchain_staleness_seconds": 5, "market_status": MarketStatus.OPEN,
        "liquidity_usd": 180_000, "depth_usd": 60_000, "estimated_slippage_pct": 0.12,
        "gas_cost_usd": 0.04, "execution_fee_usd": 0.10, "trade_notional_usd": 100.0,
        "quote_age_seconds": 5, "wallet_readiness": Readiness.READY, "wallet_network": "56",
        "wallet_balance_usd": 250.0, "gas_balance_native": 0.02, "allowance_state": "READY",
        "simulation_status": "SUCCESS", "simulation_gas_used": 180_000,
        "simulation_expected_output": "0.552 NVDAon", "source_count": 3, "source_confidence": "HIGH",
        "evidence": (
            EvidenceItem("reference_price", 180.0, "2026-10-07T13:30:00Z", DOC, "BINANCE_RWA_DERIVED"),
            EvidenceItem("quote", 181.26, "2026-10-07T13:30:10Z", QUOTE, "BINANCE_TRADING_API"),
            EvidenceItem("simulation", "SUCCESS", "2026-10-07T13:30:14Z", SIM, "BINANCE_TRANSACTION_API"),
        ),
    }
    variants = {
        "healthy": {}, "fresh_reference": {"reference_staleness_seconds": 1}, "market_open": {},
        "stale_reference": {"reference_staleness_seconds": 600},
        "closed": {"market_status": MarketStatus.CLOSED, "reference_staleness_seconds": 3600},
        "premarket": {"market_status": MarketStatus.PREMARKET},
        "after_hours": {"market_status": MarketStatus.AFTER_HOURS},
        "derived_only": {"reference_corroborated": False, "source_count": 1},
        "conflict": {"source_confidence": "CONFLICTING"},
        "missing": {"liquidity_usd": None}, "source_unavailable": {"source_count": 0},
        "malformed_timestamp": {"reference_price_timestamp": None, "reference_staleness_seconds": None},
        "thin": {"onchain_price": 187.56, "liquidity_usd": 4_000, "estimated_slippage_pct": 4.7},
        "high_slippage": {"estimated_slippage_pct": 2.4}, "high_gas": {"gas_cost_usd": 2.0},
        "failed_simulation": {"simulation_status": "FAILED", "simulation_fail_reason": "execution reverted"},
        "simulation_timeout": {"simulation_status": "TIMEOUT"},
        "wallet_low_gas": {"wallet_readiness": Readiness.NOT_READY, "gas_balance_native": 0.0},
        "wallet_wrong_network": {"wallet_readiness": Readiness.NOT_READY, "wallet_network": "1"},
        "quote_stale": {"quote_age_seconds": 90},
        "false_arbitrage": {"onchain_price": 187.56, "estimated_slippage_pct": 4.4, "execution_fee_usd": 0.45},
        "stale_onchain": {"onchain_staleness_seconds": 900},
    }
    if name not in variants:
        raise KeyError(name)
    base.update(variants[name])
    return EvidenceSnapshot(**base)

