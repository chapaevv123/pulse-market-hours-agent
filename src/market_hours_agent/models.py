from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Decision(StrEnum):
    ACT = "ACT"
    WAIT = "WAIT"
    AVOID = "AVOID"
    INVESTIGATE = "INVESTIGATE"


class MarketStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PREMARKET = "PREMARKET"
    AFTER_HOURS = "AFTER_HOURS"
    UNKNOWN = "UNKNOWN"


class ReferenceSourceType(StrEnum):
    DERIVED_RWA_REFERENCE = "DERIVED_RWA_REFERENCE"
    OFFICIAL_MARKET_REFERENCE = "OFFICIAL_MARKET_REFERENCE"
    SECONDARY_CORROBORATION = "SECONDARY_CORROBORATION"
    UNKNOWN = "UNKNOWN"


class Readiness(StrEnum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class EvidenceItem:
    field: str
    value: Any
    observed_at: str | None
    source_url: str
    source_kind: str
    confidence: str = "HIGH"
    validation_state: str = "VALID"


@dataclass(frozen=True)
class EvidenceSnapshot:
    captured_at: str
    symbol: str
    tokenized_asset: str
    chain: str = "BSC"
    chain_id: str = "56"
    token_address: str | None = None
    reference_asset: str | None = None
    reference_price: float | None = None
    reference_price_timestamp: str | None = None
    reference_source_type: ReferenceSourceType = ReferenceSourceType.UNKNOWN
    reference_corroborated: bool = False
    reference_staleness_seconds: int | None = None
    onchain_price: float | None = None
    onchain_price_timestamp: str | None = None
    onchain_staleness_seconds: int | None = None
    market_status: MarketStatus = MarketStatus.UNKNOWN
    liquidity_usd: float | None = None
    depth_usd: float | None = None
    estimated_slippage_pct: float | None = None
    gas_cost_usd: float | None = None
    execution_fee_usd: float | None = None
    trade_notional_usd: float | None = None
    quote_age_seconds: int | None = None
    wallet_readiness: Readiness = Readiness.UNKNOWN
    wallet_network: str | None = None
    wallet_balance_usd: float | None = None
    gas_balance_native: float | None = None
    allowance_state: str | None = None
    simulation_status: str | None = None
    simulation_fail_reason: str | None = None
    simulation_gas_used: int | None = None
    simulation_expected_output: str | None = None
    source_count: int = 0
    source_confidence: str = "UNKNOWN"
    evidence: tuple[EvidenceItem, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> EvidenceSnapshot:
        data = dict(raw)
        data["market_status"] = MarketStatus(data.get("market_status", "UNKNOWN"))
        data["reference_source_type"] = ReferenceSourceType(data.get("reference_source_type", "UNKNOWN"))
        data["wallet_readiness"] = Readiness(data.get("wallet_readiness", "UNKNOWN"))
        data["evidence"] = tuple(EvidenceItem(**item) for item in data.get("evidence", ()))
        return cls(**data)


@dataclass(frozen=True)
class DecisionReceipt:
    receipt_id: str
    receipt_hash: str
    policy_version: str
    timestamp: str
    decision: Decision
    evidence_completeness: str
    asset: str
    tokenized_asset: str
    chain: str
    reference_price: float | None
    reference_provenance: str
    reference_freshness_seconds: int | None
    onchain_price: float | None
    onchain_freshness_seconds: int | None
    headline_spread_pct: float | None
    slippage_pct: float | None
    execution_cost_usd: float | None
    execution_cost_pct: float | None
    executable_spread_pct: float | None
    liquidity_usd: float | None
    depth_usd: float | None
    market_state: str
    wallet_readiness: str
    simulation_result: str | None
    simulation_fail_reason: str | None
    what_we_know: tuple[str, ...]
    critical_unknowns: tuple[str, ...]
    decision_reasons: tuple[str, ...]
    what_would_change_decision: tuple[str, ...]
    evidence_links: tuple[str, ...]
    evidence_snapshot: dict[str, Any]
    deterministic: bool = True
    owner_approval_required: bool = True
    transaction_prepared: bool = False
    transaction_signed: bool = False
    transaction_broadcast: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

