from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from .models import Decision, DecisionReceipt, EvidenceSnapshot, MarketStatus, Readiness, ReferenceSourceType

POLICY_VERSION = "PULSE_EXECUTABLE_TRUTH_V2"
REFERENCE_MAX_AGE_OPEN = 120
REFERENCE_MAX_AGE_CLOSED = 900
ONCHAIN_MAX_AGE = 120
QUOTE_MAX_AGE = 30
MIN_LIQUIDITY_USD = 25_000
MAX_SLIPPAGE_PCT = 1.0
MAX_EXECUTION_COST_PCT = 0.75
MIN_EXECUTABLE_EDGE_PCT = 0.35
CRITICAL_FIELDS = (
    "reference_price", "reference_price_timestamp", "reference_staleness_seconds",
    "onchain_price", "onchain_price_timestamp", "onchain_staleness_seconds",
    "liquidity_usd", "estimated_slippage_pct", "trade_notional_usd", "quote_age_seconds",
)


def _rounded(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


def _hash(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def evaluate(snapshot: EvidenceSnapshot) -> DecisionReceipt:
    """Evaluate hard gates deterministically; missing evidence never becomes zero."""
    values = vars(snapshot)
    unknown = [name for name in CRITICAL_FIELDS if values.get(name) is None]
    if snapshot.market_status is MarketStatus.UNKNOWN:
        unknown.append("market_status")
    if snapshot.source_count < 1:
        unknown.append("source_count")

    headline = None
    if snapshot.reference_price is not None and snapshot.onchain_price is not None and snapshot.reference_price > 0:
        headline = (snapshot.onchain_price / snapshot.reference_price - 1) * 100
    execution_cost = None
    cost_pct = None
    if snapshot.gas_cost_usd is not None and snapshot.execution_fee_usd is not None:
        execution_cost = snapshot.gas_cost_usd + snapshot.execution_fee_usd
        if snapshot.trade_notional_usd and snapshot.trade_notional_usd > 0:
            cost_pct = execution_cost / snapshot.trade_notional_usd * 100
    executable = None
    if headline is not None and snapshot.estimated_slippage_pct is not None and cost_pct is not None:
        executable = abs(headline) - snapshot.estimated_slippage_pct - cost_pct

    known = [f"Reference market state is {snapshot.market_status.value}."]
    if headline is not None:
        known.append(f"Headline on-chain/reference spread is {headline:+.2f}%.")
    if snapshot.reference_source_type is ReferenceSourceType.DERIVED_RWA_REFERENCE:
        known.append("Reference price is derived, not an official exchange quote.")
    if snapshot.liquidity_usd is not None:
        known.append(f"Reported liquidity is ${snapshot.liquidity_usd:,.0f}.")
    if snapshot.estimated_slippage_pct is not None:
        known.append(f"Estimated slippage is {snapshot.estimated_slippage_pct:.2f}%.")

    reasons: list[str] = []
    changes: list[str] = []
    decision = Decision.ACT
    if unknown:
        decision = Decision.INVESTIGATE
        reasons.append("Critical execution evidence is missing; absence is not treated as zero.")
        changes.append("Resolve every critical unknown with timestamped evidence.")
    elif snapshot.reference_source_type is ReferenceSourceType.UNKNOWN:
        decision = Decision.INVESTIGATE
        reasons.append("Reference-price provenance is unknown.")
        changes.append("Identify and timestamp the reference-price source.")
    elif snapshot.reference_source_type is ReferenceSourceType.DERIVED_RWA_REFERENCE and not snapshot.reference_corroborated:
        decision = Decision.INVESTIGATE
        reasons.append("The only reference is derived from RWA data and lacks independent corroboration.")
        changes.append("Corroborate the derived reference with an independent timestamped market source.")
    elif snapshot.source_confidence in {"LOW", "CONFLICTING", "UNKNOWN"} or snapshot.source_count < 2:
        decision = Decision.INVESTIGATE
        reasons.append("Price provenance is insufficient or conflicting.")
        changes.append("Obtain a second independent source with consistent timestamps.")
    elif snapshot.reference_staleness_seconds > (
        REFERENCE_MAX_AGE_OPEN if snapshot.market_status is MarketStatus.OPEN else REFERENCE_MAX_AGE_CLOSED
    ):
        decision = Decision.WAIT
        reasons.append("Reference evidence is stale for the current market session.")
        changes.append("Wait for a fresh reference observation or the next market open.")
    elif snapshot.market_status in {MarketStatus.CLOSED, MarketStatus.PREMARKET, MarketStatus.AFTER_HOURS}:
        decision = Decision.WAIT
        reasons.append("The reference market is not open; apparent spread may not be price discovery.")
        changes.append("Re-evaluate after the reference market opens with fresh prices.")
    elif snapshot.onchain_staleness_seconds > ONCHAIN_MAX_AGE:
        decision = Decision.WAIT
        reasons.append("The on-chain observation is stale.")
        changes.append("Refresh the on-chain quote.")
    elif snapshot.quote_age_seconds > QUOTE_MAX_AGE:
        decision = Decision.WAIT
        reasons.append("The executable quote has expired.")
        changes.append("Request and simulate a fresh quote.")
    elif snapshot.liquidity_usd < MIN_LIQUIDITY_USD:
        decision = Decision.AVOID
        reasons.append("Liquidity is below the safety floor; headline spread is not safely executable.")
        changes.append(f"Liquidity must exceed ${MIN_LIQUIDITY_USD:,.0f}.")
    elif snapshot.estimated_slippage_pct > MAX_SLIPPAGE_PCT:
        decision = Decision.AVOID
        reasons.append("Slippage consumes too much of the apparent edge.")
        changes.append(f"Estimated slippage must fall to {MAX_SLIPPAGE_PCT:.2f}% or less.")
    elif cost_pct is None:
        decision = Decision.INVESTIGATE
        reasons.append("Total execution cost cannot be computed.")
        changes.append("Provide gas, fees and trade notional.")
    elif cost_pct > MAX_EXECUTION_COST_PCT:
        decision = Decision.AVOID
        reasons.append("Execution costs exceed the allowed fraction of notional.")
        changes.append(f"Execution cost must fall below {MAX_EXECUTION_COST_PCT:.2f}% of notional.")
    elif snapshot.wallet_readiness is Readiness.NOT_READY:
        decision = Decision.AVOID
        reasons.append("Wallet prerequisites are not satisfied.")
        changes.append("Use BSC and satisfy balance, gas and allowance prerequisites through owner-controlled actions.")
    elif snapshot.wallet_readiness is Readiness.UNKNOWN:
        decision = Decision.INVESTIGATE
        reasons.append("Wallet readiness is unknown.")
        changes.append("Read network, balance, gas and allowance state.")
    elif snapshot.simulation_status == "FAILED":
        decision = Decision.AVOID
        reasons.append("Transaction simulation predicts failure.")
        changes.append("Resolve the simulation failure and simulate a fresh prepared transaction.")
    elif snapshot.simulation_status != "SUCCESS":
        decision = Decision.INVESTIGATE
        reasons.append("Transaction simulation is unavailable or inconclusive.")
        changes.append("Obtain a successful, current Transaction API simulation.")
    elif executable is None or executable < MIN_EXECUTABLE_EDGE_PCT:
        decision = Decision.AVOID
        reasons.append("The apparent spread does not survive slippage and execution costs.")
        changes.append(f"Executable edge must exceed {MIN_EXECUTABLE_EDGE_PCT:.2f}%.")
    else:
        reasons.append("Fresh evidence passes every deterministic execution-safety gate.")
        changes.append("Any stale source, wider slippage, failed simulation or critical unknown revokes ACT.")

    snapshot_dict = asdict(snapshot)
    links = tuple(dict.fromkeys(item.source_url for item in snapshot.evidence if item.source_url))
    completeness = "EVIDENCE_INSUFFICIENT" if unknown else (
        "EVIDENCE_PARTIAL" if decision is Decision.INVESTIGATE else "EVIDENCE_COMPLETE"
    )
    core = {
        "policy_version": POLICY_VERSION, "timestamp": snapshot.captured_at, "decision": decision.value,
        "evidence_snapshot": snapshot_dict, "decision_reasons": reasons,
        "what_would_change_decision": changes,
    }
    receipt_hash = _hash(core)
    return DecisionReceipt(
        receipt_id=f"ptr_{receipt_hash[:20]}", receipt_hash=receipt_hash, policy_version=POLICY_VERSION,
        timestamp=snapshot.captured_at, decision=decision, evidence_completeness=completeness,
        asset=snapshot.symbol, tokenized_asset=snapshot.tokenized_asset, chain=snapshot.chain,
        reference_price=snapshot.reference_price, reference_provenance=snapshot.reference_source_type.value,
        reference_freshness_seconds=snapshot.reference_staleness_seconds, onchain_price=snapshot.onchain_price,
        onchain_freshness_seconds=snapshot.onchain_staleness_seconds, headline_spread_pct=_rounded(headline),
        slippage_pct=snapshot.estimated_slippage_pct, execution_cost_usd=_rounded(execution_cost),
        execution_cost_pct=_rounded(cost_pct), executable_spread_pct=_rounded(executable),
        liquidity_usd=snapshot.liquidity_usd, depth_usd=snapshot.depth_usd,
        market_state=snapshot.market_status.value, wallet_readiness=snapshot.wallet_readiness.value,
        simulation_result=snapshot.simulation_status, simulation_fail_reason=snapshot.simulation_fail_reason,
        what_we_know=tuple(known), critical_unknowns=tuple(sorted(set(unknown))),
        decision_reasons=tuple(reasons), what_would_change_decision=tuple(changes), evidence_links=links,
        evidence_snapshot=snapshot_dict,
    )


def replay(receipt: dict) -> DecisionReceipt:
    if receipt.get("policy_version") != POLICY_VERSION:
        raise ValueError(f"Unsupported policy version: {receipt.get('policy_version')}")
    reproduced = evaluate(EvidenceSnapshot.from_dict(receipt["evidence_snapshot"]))
    if reproduced.receipt_hash != receipt.get("receipt_hash"):
        raise ValueError("Receipt hash mismatch: evidence or decision fields were modified")
    return reproduced

