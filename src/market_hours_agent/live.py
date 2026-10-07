from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .binance_web3 import BinanceWeb3Client
from .models import EvidenceItem, EvidenceSnapshot, MarketStatus, Readiness, ReferenceSourceType

RWA_DOC = "https://web3.binance.com/en/dev-docs/catalog/web3-wallet/api/rest-api/rwa-data"
TRADING_DOC = "https://web3.binance.com/en/dev-docs/catalog/web3-wallet/api/rest-api/trading-api"
WALLET_DOC = "https://web3.binance.com/en/dev-docs/catalog/web3-wallet/api/rest-api/wallet-api"
SIM_DOC = "https://web3.binance.com/en/dev-docs/catalog/web3-wallet/api/rest-api/transaction-api"


def _iso(milliseconds: int | None) -> str | None:
    return None if milliseconds is None else datetime.fromtimestamp(milliseconds / 1000, UTC).isoformat()


def _age(milliseconds: int | None, now: datetime) -> int | None:
    return None if milliseconds is None else max(0, int(now.timestamp() - milliseconds / 1000))


def _market(value: str | None) -> MarketStatus:
    return {
        "regular": MarketStatus.OPEN, "closed": MarketStatus.CLOSED, "premarket": MarketStatus.PREMARKET,
        "postmarket": MarketStatus.AFTER_HOURS, "overnight": MarketStatus.AFTER_HOURS,
    }.get((value or "").lower(), MarketStatus.UNKNOWN)


def _assets(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [asset for page in payload.get("data", []) for asset in page.get("tokenAssets", [])]


def collect_live_snapshot(
    client: BinanceWeb3Client, *, ticker: str, wallet_address: str, from_token: str,
    amount_atomic: str, trade_notional_usd: float,
) -> EvidenceSnapshot:
    """Collect authenticated read-only evidence. No method in this flow signs or broadcasts."""
    now = datetime.now(UTC)
    search = client.search_rwa(ticker)
    matches = [asset for row in search.get("data", []) for asset in row.get("assets", [])
               if str(asset.get("binanceChainId")) == "56"]
    if not matches:
        raise RuntimeError(f"No BSC tokenized stock found for {ticker}")
    asset = matches[0]
    token_address = asset["tokenContractAddress"]
    prices = client.rwa_prices([token_address])
    price = (prices.get("data") or [{}])[0]
    market_payload = client.underlying_market(token_address)
    market = market_payload.get("data") or {}
    status = market.get("statusInfo") or {}
    market_data = market.get("marketData") or {}
    quote_payload = client.quote(from_token, token_address, amount_atomic, wallet_address)
    quote = (quote_payload.get("data") or [{}])[0]
    build = None
    simulation = None
    if quote.get("quoteId"):
        build_payload = client.build_swap(
            from_token, token_address, amount_atomic, wallet_address, str(quote["quoteId"])
        )
        build = build_payload.get("data") or {}
        transaction = build.get("tx") if isinstance(build, dict) else None
        if isinstance(transaction, dict) and {"from", "to", "value", "data"} <= transaction.keys():
            simulation = client.simulate_evm(transaction).get("data") or {}
    balances_payload = client.wallet_balances(wallet_address)
    balances = _assets(balances_payload)
    native = next((x for x in balances if x.get("tokenContractAddress") == ""), None)
    spend = next((x for x in balances if str(x.get("tokenContractAddress", "")).lower() == from_token.lower()), None)
    spend_usd = None if not spend else float(spend.get("balance", 0)) * float(spend.get("tokenPrice", 0))
    gas_native = None if not native else float(native.get("balance", 0))
    if isinstance(balances_payload.get("data"), list):
        wallet_ready = (Readiness.READY if spend_usd is not None and spend_usd >= trade_notional_usd
                        and bool(gas_native) else Readiness.NOT_READY)
    else:
        wallet_ready = Readiness.UNKNOWN

    response_ms = price.get("tokenPriceUpdatedAt") or prices.get("timestamp")
    reference_ms = market_payload.get("timestamp")
    quote_ms = quote_payload.get("timestamp")
    evidence = (
        EvidenceItem("rwa_metadata", asset, _iso(search.get("timestamp")), RWA_DOC, "BINANCE_RWA_API"),
        EvidenceItem("reference_price", market_data.get("referencePrice"), _iso(reference_ms), RWA_DOC,
                     "DERIVED_RWA_REFERENCE", validation_state="NEEDS_CORROBORATION"),
        EvidenceItem("onchain_price", price.get("tokenPrice"), _iso(response_ms), RWA_DOC, "BINANCE_RWA_API"),
        EvidenceItem("quote", quote, _iso(quote_ms), TRADING_DOC, "BINANCE_TRADING_API"),
        EvidenceItem("prepared_action", build, now.isoformat(), TRADING_DOC, "BINANCE_TRADING_API",
                     validation_state="VALID" if build else "UNAVAILABLE"),
        EvidenceItem("wallet_readiness", wallet_ready.value, _iso(balances_payload.get("timestamp")), WALLET_DOC,
                     "BINANCE_WALLET_API"),
        EvidenceItem("simulation", simulation, now.isoformat(), SIM_DOC, "BINANCE_TRANSACTION_API",
                     validation_state=("VALID" if simulation else "SIGNATURE_REQUIRED"
                                       if build and build.get("executionMode") == "RFQ" else "UNAVAILABLE")),
    )
    return EvidenceSnapshot(
        captured_at=now.isoformat(), symbol=ticker.upper(), tokenized_asset=asset.get("tokenSymbol") or ticker,
        token_address=token_address, reference_asset=ticker.upper(),
        reference_price=float(market_data["referencePrice"]) if market_data.get("referencePrice") else None,
        reference_price_timestamp=_iso(reference_ms),
        reference_source_type=ReferenceSourceType.DERIVED_RWA_REFERENCE, reference_corroborated=False,
        reference_staleness_seconds=_age(reference_ms, now),
        onchain_price=float(price["tokenPrice"]) if price.get("tokenPrice") else None,
        onchain_price_timestamp=_iso(response_ms), onchain_staleness_seconds=_age(response_ms, now),
        market_status=_market(status.get("marketStatus")), liquidity_usd=None, depth_usd=None,
        estimated_slippage_pct=abs(float(quote["priceImpactPercent"])) if quote.get("priceImpactPercent") else None,
        gas_cost_usd=None, execution_fee_usd=float(quote["tradeFee"]) if quote.get("tradeFee") else None,
        trade_notional_usd=trade_notional_usd, quote_age_seconds=_age(quote_ms, now),
        wallet_readiness=wallet_ready, wallet_network="56", wallet_balance_usd=spend_usd,
        gas_balance_native=gas_native, allowance_state="UNKNOWN",
        simulation_status=(simulation.get("status") if simulation else "SIGNATURE_REQUIRED"
                           if build and build.get("executionMode") == "RFQ" else None),
        simulation_fail_reason=(simulation.get("failReason") if simulation else
                                "RFQ requires wallet signature before a transaction exists; Pulse stopped before signing."
                                if build and build.get("executionMode") == "RFQ" else None),
        simulation_expected_output=str(quote.get("toTokenAmount")) if quote.get("toTokenAmount") else None,
        source_count=4, source_confidence="MEDIUM", evidence=evidence,
    )
