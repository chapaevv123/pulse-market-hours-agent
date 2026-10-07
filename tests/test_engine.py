from dataclasses import replace

import pytest

from market_hours_agent.binance_web3 import BinanceWeb3Client
from market_hours_agent.config import Settings
from market_hours_agent.engine import POLICY_VERSION, evaluate, replay
from market_hours_agent.fixtures import EXPECTED, scenario
from market_hours_agent.models import Decision, EvidenceSnapshot


@pytest.mark.parametrize(("name", "expected"), EXPECTED.items())
def test_evaluation_matrix(name, expected):
    assert evaluate(scenario(name)).decision is Decision(expected)


def test_false_act_rate_is_zero():
    false_acts = [name for name, expected in EXPECTED.items()
                  if evaluate(scenario(name)).decision is Decision.ACT and expected != "ACT"]
    assert false_acts == []


def test_unknown_is_not_zero():
    receipt = evaluate(EvidenceSnapshot(captured_at="2026-10-07T00:00:00Z", symbol="NVDA", tokenized_asset="NVDAon"))
    assert receipt.decision is Decision.INVESTIGATE
    assert "reference_price" in receipt.critical_unknowns
    assert receipt.headline_spread_pct is None


def test_derived_reference_caveat_is_visible():
    receipt = evaluate(scenario("derived_only"))
    assert receipt.reference_provenance == "DERIVED_RWA_REFERENCE"
    assert any("not an official exchange quote" in line for line in receipt.what_we_know)


def test_receipt_never_signs_or_broadcasts():
    receipt = evaluate(scenario("healthy"))
    assert receipt.owner_approval_required
    assert not receipt.transaction_signed
    assert not receipt.transaction_broadcast


def test_replay_same_evidence_same_policy_same_decision():
    original = evaluate(scenario("false_arbitrage"))
    reproduced = replay(original.as_dict())
    assert reproduced.decision == original.decision
    assert reproduced.receipt_hash == original.receipt_hash
    assert reproduced.receipt_id == original.receipt_id


def test_receipt_hash_is_stable():
    assert evaluate(scenario("healthy")).receipt_hash == evaluate(scenario("healthy")).receipt_hash


def test_tampered_receipt_is_rejected():
    receipt = evaluate(scenario("healthy")).as_dict()
    receipt["evidence_snapshot"]["liquidity_usd"] = 1
    with pytest.raises(ValueError, match="hash mismatch"):
        replay(receipt)


def test_wrong_policy_cannot_replay():
    receipt = evaluate(scenario("healthy")).as_dict()
    receipt["policy_version"] = "UNKNOWN_POLICY"
    with pytest.raises(ValueError, match="Unsupported policy"):
        replay(receipt)


def test_receipt_contract_is_complete():
    receipt = evaluate(scenario("healthy")).as_dict()
    required = {"receipt_id", "receipt_hash", "policy_version", "timestamp", "asset", "chain",
                "reference_price", "reference_provenance", "reference_freshness_seconds", "onchain_price",
                "onchain_freshness_seconds", "headline_spread_pct", "liquidity_usd", "slippage_pct",
                "execution_cost_usd", "market_state", "wallet_readiness", "simulation_result",
                "critical_unknowns", "decision", "decision_reasons", "what_would_change_decision",
                "evidence_links", "evidence_snapshot"}
    assert required <= receipt.keys()
    assert receipt["policy_version"] == POLICY_VERSION


def test_signature_matches_known_computation():
    client = BinanceWeb3Client("key", "secret")
    headers = client.signed_headers(
        "GET", "/build/api/v1/dex/market/rwa/search?keyword=NVDA", timestamp="2026-10-07T00:00:00.000Z"
    )
    assert headers["X-OC-APIKEY"] == "key"
    assert headers["X-OC-SIGN"].endswith("=")
    assert headers["X-OC-RECV-WINDOW"] == "60000"


def test_signature_rejects_missing_build_prefix():
    with pytest.raises(ValueError):
        BinanceWeb3Client("key", "secret").signed_headers("GET", "/api/v1/test")


def test_simulation_rejects_incomplete_transaction_before_network():
    with pytest.raises(ValueError, match="requires"):
        BinanceWeb3Client("key", "secret").simulate_evm({"from": "0x0"})


def test_build_swap_is_prepare_only():
    client = BinanceWeb3Client("key", "secret")
    captured = {}

    def fake_get(path, params):
        captured.update({"path": path, "params": params})
        return {"success": True, "code": 0, "data": {"executionMode": "RFQ"}}

    client.get = fake_get
    result = client.build_swap("from", "to", "10", "wallet", "quote")
    assert captured["path"] == "/api/v1/dex/aggregator/swap"
    assert captured["params"] == {
        "binanceChainId": "56", "amount": "10", "fromTokenAddress": "from",
        "toTokenAddress": "to", "userWalletAddress": "wallet", "quoteId": "quote",
        "slippagePercent": "0.5",
    }
    assert result["data"] == {"executionMode": "RFQ"}


def test_fixture_mode_needs_no_credentials():
    Settings(None, None, None, "fixture").validate_startup()


def test_live_mode_fails_safely_without_credentials():
    with pytest.raises(RuntimeError, match="server-side variables"):
        Settings(None, None, None, "live").validate_startup()


def test_wallet_address_validation():
    health = Settings("key", "secret", "not-an-address", "live").health()
    assert not health["wallet_valid"]
    assert not health["live_ready"]


def test_hash_changes_when_source_evidence_changes():
    original = scenario("healthy")
    changed = replace(original, liquidity_usd=original.liquidity_usd + 1)
    assert evaluate(original).receipt_hash != evaluate(changed).receipt_hash
