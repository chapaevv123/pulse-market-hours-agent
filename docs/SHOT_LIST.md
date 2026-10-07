# Screen-recording shot list

Record at 1080p, browser zoom 100%, notifications disabled, and no credential or `.env` window visible.

| Shot | Time | Screen | Required proof |
|---:|---:|---|---|
| 1 | 0:00 | Hero UI | Product title and “Executable truth for tokenized stocks” |
| 2 | 0:20 | Hero opportunity | Headline spread `+4.20%` |
| 3 | 0:35 | Cost breakdown | Executable spread `-0.69%` |
| 4 | 0:48 | Decision card | `AVOID` and transaction signed `false` |
| 5 | 1:05 | Sanitized live audit | `DERIVED_RWA_REFERENCE` and caveat |
| 6 | 1:20 | Sanitized live audit | Live on-chain quote and AFTER_HOURS state |
| 7 | 1:35 | Receipt/live audit | Wallet readiness `NOT_READY` |
| 8 | 1:45 | Transaction evidence | Prepared SWAP, no signature |
| 9 | 1:55 | Simulation result | Preflight catches insufficient BEP20 balance |
| 10 | 2:08 | Receipt JSON | Evidence, unknown fields, policy version |
| 11 | 2:22 | Receipt footer | Receipt ID and SHA-256 hash |
| 12 | 2:30 | Replay endpoint | Same decision/hash; optionally show tamper rejection |
| 13 | 2:45 | Terminal | `39 passed`; explain 22 scenarios and zero false ACT |
| 14 | 3:05 | README | BNB integration, safety boundary, repository URL |

Before recording, reset the UI to the false-arbitrage case. Crop all terminal output so the wallet address and
environment-variable values cannot appear. Use the sanitized `tools/live_audit.py` output only.
