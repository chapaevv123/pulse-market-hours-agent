# Final demo script — target 3:25

## 0:00-0:15 — Problem

“Tokenized stocks trade 24/7, but reference markets do not. A visible spread does not mean a trade is actually
safe or executable.”

## 0:15-0:30 — Product

“Pulse Market Hours Agent checks execution truth before any signature. It converts evidence into one deterministic
decision: ACT, WAIT, AVOID, or INVESTIGATE.”

## 0:30-1:05 — Hero case

Show the false-arbitrage scenario above the fold.

“This looks like a 4.20 percent opportunity. Pulse checks freshness, session state, quote slippage, costs, wallet
readiness, and simulation. The executable result is negative 0.69 percent, so Pulse says AVOID. No transaction is
signed.”

Pause briefly on `+4.20%`, `-0.69%`, and `AVOID`.

## 1:05-1:35 — Live Binance Web3 evidence

Show only the sanitized live-audit output.

“This is the authenticated Binance Web3 path on BNB Smart Chain: live NVDAon discovery, on-chain price, quote, and
AFTER_HOURS market state. Binance documents the reference price as derived, not an official exchange quote, so
Pulse labels that provenance explicitly and will not pretend it is authoritative.”

## 1:35-2:05 — Preflight simulation

“Pulse prepared a SWAP transaction without signing it and sent it to the Transaction API preflight. The simulator
caught `BEP20: transfer amount exceeds balance`. Wallet readiness is NOT_READY, and ACT is impossible. No signature.
No broadcast. No money spent.”

## 2:05-2:35 — Executable Truth Receipt

Export the receipt and show its ID, evidence snapshot, UNKNOWN fields, policy version, and SHA-256 hash.

“The decision is an artifact, not a chat response. Replaying the same evidence under the same policy reproduces the
same decision and hash. Change the evidence and verification rejects it.”

## 2:35-2:55 — Evaluation

Show the test run.

“The evaluation covers 22 deterministic scenarios: fresh and stale prices, every market session, missing and
conflicting sources, thin liquidity, high slippage, wallet failures, simulation failures, and false arbitrage.
All 22 match their expected decisions, with zero false ACT results.”

## 2:55-3:15 — Final message

“Most trading agents optimize for action. Pulse optimizes for justified action—and refuses execution when the
evidence is not good enough.”

## 3:15-3:25 — Close

Show the repository README and BNB Chain integration section.

“Pulse Market Hours Agent: executable truth for tokenized stocks on BNB Chain.”
