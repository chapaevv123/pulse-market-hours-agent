# Pulse reuse audit and public-safe boundary

## Concepts reused

- Missing data remains UNKNOWN.
- Evidence carries provenance and observation time.
- Deterministic safety policy is separate from narrative explanation.
- Negative-EV and unsafe actions are rejected early.
- Owner approval gates every irreversible action.
- Source health and freshness are first-class inputs.

## Explicitly not reused

- No private database or data export.
- No owner records, wallets, watchlists or submissions.
- No private source inventory, secrets or private API credentials.
- No copied private implementation or confidential thresholds.
- No dependency on the private Pulse runtime.

All code in this directory is a clean public implementation created for this event. The numerical demo policy
is documented in source and must be tuned against public evidence; it is not a copy of private production policy.

