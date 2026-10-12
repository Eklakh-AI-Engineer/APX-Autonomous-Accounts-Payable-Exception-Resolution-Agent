# Master scoreboard

**Status: current DEV run passed its narrow implemented gates; release quality acceptance remains blocked.** Candidate CI run `38211575065` on `97c24cd2f193813a936c38ea2e08f20d61e19582`; fresh output `benchmark_dev_20261012_062054.json`, DEV, seed 42, reference date 2026-08-29, 500 invoices. Artifact: [CI benchmark evidence](https://github.com/Eklakh-AI-Engineer/APX-Autonomous-Accounts-Payable-Exception-Resolution-Agent/actions/runs/38211575065/artifacts/11729645901).

| Current candidate measure | Result | Acceptance interpretation |
|---|---:|---|
| Detection precision / recall / F1 | 75.99% / 99.03% / 85.99% (307 TP, 97 FP, 3 FN) | F1 barely exceeds the configured 0.85 gate; false positives remain high |
| Retrieval Recall@5 / Recall@10 | 100% / 100% | Above configured Recall@5 gate on generated DEV cases and the ten-case curated retrieval subset |
| Retrieval MRR / nDCG@10 | 0.8583 / 0.9131 | DEV result only |
| Valid evidence rate / invalid rejection | 57.67% / 99.04% | Validity remains low; investigate without adapting to unreviewed labels |
| Vendor scope correctness | 100% | DEV result only |
| Decision outcome accuracy / risk accuracy / escalation accuracy | 62.20% / 93.00% / 67.40% | Decision quality remains weak |
| Action accuracy / guardrail accuracy | 49.60% / 58.00% | Action and guardrail quality remain weak |
| Approval accuracy / blocked accuracy | 1.60% / 0.94% | Serious lifecycle/metric gap; not suitable for action acceptance |
| Unauthorized action rate | 0.00% | Simulated metric only; not proof of production authorization |
| Business automation / decision accuracy | 54.4% / 49.6% | Automation exceeds configured 0.50 gate; decision accuracy remains weak |
| Mean latency / estimated net cost | 132.3 ms / -$4.902 per case | Cost is a net estimate with assumptions requiring review, not a validated unit cost |

| Layer / measure | Recorded result | Gate / interpretation |
|---|---:|---|
| Extraction F1 | 1.000 | Synthetic structured-input measure; not OCR extraction evidence |
| Detection precision | 0.1541 | Weak precision |
| Detection recall | 0.9688 | High recall with many false positives |
| Detection F1 | 0.2659 | Fails recorded 0.85 target |
| Retrieval Recall@5 | 0.60 | Fails recorded 0.70 target |
| Retrieval MRR / nDCG@10 | 0.55 / 0.60 | Historical only |
| Valid evidence rate | 0.03 | Material evidence quality gap |
| Vendor scope correctness | 0.09 | Material grounding gap |
| Business decision accuracy | 0.274 | Historical result |
| Automation rate | 0.024 | Fails recorded 0.50 target |
| Unauthorized action rate | 0.00 | Simulated benchmark field only; not proof of API/execution authorization |
| Estimated cost | $514 total; $1.028/case | Historical estimate, model assumptions not independently checked |
| Mean latency | 2712.5 ms | Historical result |

The current benchmark reports `passed: true` because its implemented gates cover detection F1, retrieval Recall@5, automation rate, and unauthorized-action rate only. It does not gate the weak decision/action/approval metrics above, and it explicitly does not measure extraction. Therefore a benchmark command pass does not close APX acceptance. Historical baseline below remains for context and is not current performance.

## Current candidate integrity and gate status

Candidate `97c24cd2f193813a936c38ea2e08f20d61e19582` (CI run `38211575065`, passed): eval data SHA-256 `177297e2c8cd78f21b45ad814dbe5079042be4d051b80649dc9ca3dadc8edfbd`; evidence corpus SHA-256 `09e5e36c37541f3e5dc3eadf7f9d0d1d6f5eda6406abecf5963260d93db66e86`. Structural inspection found 10 unique evaluation IDs, 235 unique evidence IDs, and no duplicate IDs or missing references. The available schema contains retrieval relevance sets but no reviewer/adjudication provenance or invoice/job mappings. Therefore this is an integrity check only; there is no human-reviewed acceptance score yet, and release remains blocked. The deterministic DEV run does not substitute for missing adjudication provenance.
