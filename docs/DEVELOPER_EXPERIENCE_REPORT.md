# Binance Web3 Developer Experience Report

All observations below came from hands-on authenticated use on 7 October 2026. No setup duration is claimed because
credential creation was completed separately by the owner. No signature or transaction broadcast occurred.

## What was tested

An end-to-end BSC path: RWA search -> RWA price -> underlying market -> aggregator quote -> public wallet balances ->
SWAP construction -> pre-transaction simulation. A complete successful audit took 3.02 seconds from the client.

## Authentication and error handling

- HMAC authentication was straightforward once the signing path included the `/build` prefix documented by Binance.
- The first authenticated request returned business error `40103` because the default receive window was exceeded in
  this environment. Setting the documented `X-OC-RECV-WINDOW` header to 60,000 ms resolved it.
- API business errors were machine-readable and useful for diagnosis.
- A concise official end-to-end signing example covering canonical query encoding and `/build` would reduce mistakes.

## RWA and reference-price semantics

- NVDAon discovery on BSC and its token price worked as expected.
- `tokenPriceUpdatedAt` made on-chain freshness inspectable.
- The underlying-market response exposed session state; the observed state was AFTER_HOURS.
- The most important semantic caveat is that `referencePrice` is derived from RWA/on-chain data rather than an
  official traditional-exchange quote. The name can invite overconfidence. A name such as `derivedReferencePrice`,
  plus explicit provenance and an independent observation timestamp, would be safer for agent developers.

## Quote and transaction preparation

- The quote returned an executable route and price-impact information suitable for slippage checks.
- The observed quote did not provide a defensible aggregate liquidity/depth value. Pulse left liquidity UNKNOWN
  instead of substituting volume or zero.
- The transaction build returned execution mode `SWAP` and a simulation-ready EVM transaction.
- A documented, read-only ticker-to-quote example would make the RWA-to-trading transition easier to understand.

## Wallet and pre-transaction simulation

- The Wallet API supported read-only balance checks for a public BSC address.
- The demo address lacked the required spend balance, so wallet readiness was correctly NOT_READY.
- The Transaction API accepted the prepared EVM transaction without a wallet signature or broadcast.
- Preflight returned `FAILED` with the actionable reason `BEP20: transfer amount exceeds balance`. This was the most
  valuable safety signal in the integration: the bad action was caught before irreversible execution.

## What worked well

- One credential pair covered the full evidence path.
- Timestamps, market status, quote impact, prepared transaction, and simulation outcome were machine-readable.
- Transaction preflight could be used as a genuine safety gate without custody or signing authority.
- Error payloads were specific enough to drive deterministic handling.

## What could be improved

- Return explicit provenance and independent observation time for each price component.
- Rename or strongly type derived `referencePrice` to prevent it being mistaken for an official exchange quote.
- Provide executable depth or quote bands at several notionals alongside price impact.
- Provide execution fees and estimated gas in directly comparable units, including a documented USD conversion path.
- Publish one read-only end-to-end example: ticker -> BSC asset -> quote -> build -> simulate, with no broadcast.
- Distinguish market closed, source stale, and source unavailable in consistently typed fields.
