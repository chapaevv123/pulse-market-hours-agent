# Final submission copy

## Project name

Pulse Market Hours Agent

## Tagline

The tokenized-stock agent that refuses bad trades—and proves why.

## One-line description

Pulse converts an apparent tokenized-stock opportunity into a replayable, evidence-backed Executable Truth Receipt
using live BNB Chain pricing, reference provenance, market state, slippage, wallet readiness, and transaction
simulation before any signature happens.

## Long description

Tokenized stocks can trade around the clock while their underlying reference markets are closed. That creates a
dangerous gap between **apparent spread** and **executable spread**: a price difference may depend on a stale or
derived reference, disappear under slippage and costs, or fail because the wallet or transaction is not ready.

Pulse Market Hours Agent is a pre-trade execution-safety layer for tokenized stocks on BNB Smart Chain. It collects
timestamped Binance Web3 evidence for the tokenized asset, derived reference price, market session, on-chain quote,
price impact, public wallet readiness, prepared transaction, and preflight simulation. Deterministic safety gates—not
an LLM—produce one state: ACT, WAIT, AVOID, or INVESTIGATE.

Missing values are never converted to zero. Binance's RWA `referencePrice` is labeled as derived rather than claimed
as an official TradFi quote. If provenance, freshness, liquidity, cost, wallet, or simulation evidence is incomplete,
Pulse refuses ACT and states exactly what evidence would change the decision.

Each result is exported as an **Executable Truth Receipt** containing the complete evidence snapshot, decision
reasons, critical unknowns, source links, and policy version. Canonical JSON is protected by a stable SHA-256 hash.
The same snapshot and policy replay to the same decision; modified evidence fails verification.

The hero demo turns an apparent `+4.20%` spread into `-0.69%` executable spread and returns AVOID. In the authenticated
live path, Pulse discovered NVDAon on BSC, prepared a SWAP without signing, and used Binance's Transaction API
preflight to catch `BEP20: transfer amount exceeds balance`. It stopped before signature or broadcast.

The deterministic evaluation covers 22 scenarios and produces 22 expected decisions with **zero false ACT** results.
No private key, autonomous trading, wallet signature, transaction broadcast, or real-money action is implemented.

## Binance Web3 APIs used

- RWA search, price, and underlying-market data
- Aggregator quote and SWAP construction
- Public wallet token balances
- Pre-transaction EVM simulation

## Truthful limitations

- The Binance RWA reference is derived, not an independently official TradFi quote.
- Aggregate liquidity/depth was not defensibly available in the observed response and remains UNKNOWN.
- Complete execution cost in USD remains unavailable from the observed evidence.
- Agentic Wallet and BNB Agent Studio integrations are not claimed.
- Pulse prepares and simulates; it never signs or broadcasts.
