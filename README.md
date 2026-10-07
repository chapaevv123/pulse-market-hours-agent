# Pulse Market Hours Agent

## Executable truth for tokenized stocks.

> **The tokenized-stock agent that refuses bad trades—and proves why.**

Tokenized stocks can trade while their reference markets are closed. Most tools show an apparent spread; Pulse
asks whether that spread is fresh, supported by evidence, and actually executable **before any signature**.

## The problem

An on-chain price difference can disappear after stale-reference risk, market session, slippage, costs, wallet
prerequisites, or a reverting transaction are considered. Missing evidence is also dangerous: UNKNOWN is not zero.

## The product

Pulse checks reference provenance, price freshness, market session, the on-chain quote, slippage, wallet readiness,
transaction simulation, and critical unknowns. A deterministic policy then returns exactly one state:

`ACT` · `WAIT` · `AVOID` · `INVESTIGATE`

Every decision becomes a replayable **Executable Truth Receipt** containing the evidence snapshot, reasons, change
conditions, policy version, source links, and a stable SHA-256 hash.

## The hero example

```text
Headline spread:    +4.20%
Executable spread: -0.69%
Decision:           AVOID
Transaction signed: false
```

Most agents optimize for action. **Pulse optimizes for justified action.**

## Architecture

```text
Binance Web3 evidence
  RWA discovery + price + market state
              |
              v
Executable quote -> wallet readiness -> transaction build -> simulation
              |                                      (no signing)
              v
Deterministic safety policy
              |
              v
ACT / WAIT / AVOID / INVESTIGATE
              |
              v
Replayable receipt + SHA-256 verification
```

Arithmetic, freshness, session state, costs, wallet readiness, simulation status, and hard gates are deterministic.
An explanation layer may summarize a receipt but cannot override its decision.

## Binance Web3 integration

The authenticated, server-side flow was validated on BNB Smart Chain (chain 56):

1. Discover the NVDA tokenized asset through the RWA API.
2. Read its on-chain price and underlying-market state.
3. Label `referencePrice` as `DERIVED_RWA_REFERENCE`, not an official exchange quote.
4. Request an executable quote and price-impact estimate.
5. Read public wallet readiness.
6. Prepare a SWAP transaction without signing it.
7. Run Transaction API preflight simulation without broadcast.

The live preflight caught `BEP20: transfer amount exceeds balance`; Pulse refused ACT before a signature existed.
Credentials are server-side only and are never returned by the health endpoint or browser API.

## Safety model

The execution boundary is:

`PREPARE -> SIMULATE -> EXPLAIN -> OWNER APPROVAL REQUIRED`

There is no private-key ingestion, wallet signing, approval, swap broadcast, or autonomous real-money execution.
The public deployment defaults to deterministic fixture mode to avoid exposing credentials or consuming API quota.

## Receipt replay and verification

Download a receipt from the UI, then replay it against the same policy:

```bash
curl -X POST http://127.0.0.1:8080/api/replay \
  -H "Content-Type: application/json" \
  --data-binary @receipt.json
```

The same evidence and policy reproduce the same decision and hash. Modified evidence is rejected as a hash mismatch.

## Evaluation

- 22 deterministic execution scenarios
- 22 expected decisions reproduced
- **0 false ACT decisions**
- UNKNOWN preservation, replay determinism, hash stability, and tamper rejection tested
- 39 automated tests passing

A false ACT is intentionally treated as worse than a false WAIT.

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e .
.venv/Scripts/python -m market_hours_agent.server
```

Open `http://127.0.0.1:8080`. The default demo is deterministic and needs no credentials.

For authenticated server-side validation, copy `.env.example` to `.env`, provide only the documented Binance Web3
API key/secret and a public BSC address, load those variables into the process, and run `tools/live_audit.py`.
Never provide a seed phrase or private key.

## Quality checks

```bash
python -m pytest -q
python -m ruff check src tests tools
python -m compileall -q src tests tools
```

## Deployment

`Dockerfile` and `render.yaml` provide a minimal HTTPS-ready Render deployment. The checked-in configuration uses
`PULSE_DEMO_MODE=fixture`; no credentials are required for the public judging demo. See
[deployment instructions](docs/DEPLOYMENT.md).

## Limitations

- Binance Web3 `referencePrice` is derived from RWA data, not an independently authoritative TradFi quote.
- The observed quote did not expose defensible aggregate liquidity/depth; Pulse preserves it as UNKNOWN.
- Complete USD execution-cost calculation is unavailable from the observed evidence.
- Live ACT remains blocked without authoritative corroboration and complete execution evidence.
- Agentic Wallet and BNB Agent Studio prize integrations are not claimed.
- This is experimental software, not investment advice.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Live integration](docs/LIVE_INTEGRATION.md)
- [Developer Experience Report](docs/DEVELOPER_EXPERIENCE_REPORT.md)
- [Judging matrix](docs/JUDGING_MATRIX.md)
- [Demo script](docs/DEMO_SCRIPT.md)
- [Screen-recording shot list](docs/SHOT_LIST.md)
- [Submission copy](docs/SUBMISSION.md)
- [Safety and limitations](docs/SAFETY.md)
- [Rules audit](docs/RULES_AUDIT.md)
- [Public-safe reuse audit](docs/REUSE_AUDIT.md)

MIT licensed.
