# Architecture

```text
Binance RWA + Market + Trading + Wallet APIs
                    │ timestamped evidence
                    ▼
          EvidenceSnapshot (typed, nullable)
                    │
                    ▼
       Deterministic execution safety engine
        freshness · session · liquidity · cost
        wallet readiness · simulation · UNKNOWN
                    │
                    ▼
          Executable Truth Decision Receipt
      ACT / WAIT / AVOID / INVESTIGATE + evidence
                    │
           optional explanation layer
                    │
                    ▼
   PREPARE → SIMULATE → EXPLAIN → OWNER APPROVAL
```

No LLM computes prices or overrides a gate. No component broadcasts or signs.

