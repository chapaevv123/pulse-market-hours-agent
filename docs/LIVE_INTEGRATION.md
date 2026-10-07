# Live integration status

Validated on 7 October 2026 with owner-supplied server-side credentials. No secret value was printed, persisted in
a receipt, or sent to browser JavaScript.

| Integration | Status | Observed result |
|---|---|---|
| RWA metadata / on-chain price | READY | Live NVDAon on BSC returned |
| Derived reference / market state | READY | Derived reference present; AFTER_HOURS observed |
| Quote / price impact | READY | Executable quote and slippage returned |
| Wallet balances / gas readiness | READY | Public demo wallet correctly classified NOT_READY |
| Swap preparation | READY | Execution mode SWAP; no signature |
| Transaction simulation | READY | Preflight ran and safely failed on insufficient BEP20 balance |
| Independent official reference | NEEDS CREDENTIAL | Binance reference remains derived, so ACT is blocked |
| Liquidity/depth | NEEDS IMPLEMENTATION/SOURCE | Quote did not expose defensible aggregate liquidity; preserved UNKNOWN |
| Agentic Wallet | SKIPPED | Distinct Wallet Skills integration not claimed |
| Agent Studio | SKIPPED | Main-prize execution-safety path prioritized |

## Safe credential setup

Create `.env` from `.env.example` and set `BINANCE_WEB3_API_KEY`, `BINANCE_WEB3_SECRET_KEY`, a public
`PULSE_WALLET_ADDRESS`, and `PULSE_DEMO_MODE=live`. `.env` is excluded by `.gitignore`.

Only API access for RWA/market data, quotes, read-only wallet balances, transaction construction and simulation is
needed. Never supply a private key, seed phrase, withdrawal/transfer permission, unlimited approval, wallet signing,
or transaction broadcast authority.

The `/api/health` endpoint reports only booleans and missing variable names. Run `tools/live_audit.py` for the
authenticated server-side validation; its output is deliberately sanitized.
