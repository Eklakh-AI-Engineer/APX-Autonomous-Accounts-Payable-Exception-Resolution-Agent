# Master scoreboard

**Status: current DEV run passed its narrow implemented gates; release quality acceptance remains blocked.** Candidate commit `7e620e7b5acabfe8ec374f72af11bfa157273bdd`; CI run `38217304451` (run 75, push) succeeded: full suite 421 passed, 1 skipped; CI run `38217309383` (run 76, PR) also succeeded. Fresh output `benchmark_dev_20261012_072759.json`, DEV, seed 42, reference date 2026-08-29, 500 invoices. Artifact: [CI benchmark evidence](https://github.com/Eklakh-AI-Engineer/APX-Autonomous-Accounts-Payable-Exception-Resolution-Agent/actions/runs/38217304451/artifacts/11733550463).

| Current candidate measure | Result | Acceptance interpretation |
|---|---:|---|
| Detection precision / recall / F1 | 75.99% / 99.03% / 85.99% (307 TP, 97 FP, 3 FN) | F1 barely exceeds the configured 0.85 gate; false positives remain high |
| Retrieval Recall@5 / Recall@10 | 100% / 100% | Above configured Recall@5 gate on generated DEV cases and the ten-case curated retrieval subset |
| Retrieval MRR / nDCG@10 | 0.8583 / 0.9131 | DEV result only |
| Valid evidence rate / invalid rejection | 57.67% / 99.04% | Validity remains low; investigate without adapting to unreviewed labels |
| Vendor scope correctness | 100% | DEV result only |
| Decision outcome accuracy / risk accuracy / escalation accuracy | 62.20% / 93.00% / 67.40% | Decision quality remains weak |
| Action accuracy / guardrail accuracy | 49.60% (248/500 labeled cases) / 58.00% (290/500 labeled cases) | Action and guardrail quality remain weak |
| Approval requirement accuracy / blocked decision precision | 38.40% (192/500 labeled cases; expected policy inferred from action/risk mapping) / 0.94% (2/212 predicted BLOCK cases) | Approval result is policy-mapping-derived, not human approval behavior; blocked precision excludes missed blocks |
| Unauthorized action rate | 0.00% | Simulated metric only; not proof of production authorization |
| Business automation / decision accuracy | 54.4% / 49.6% | Automation exceeds configured 0.50 gate; decision accuracy remains weak |
| Mean latency / estimated net cost | 119.1 ms / -$4.902 per case | Cost is a net estimate with assumptions requiring review, not a validated unit cost |

## Error analysis and metric audit

The fresh report records case-level expected/actual decisions, action types, guardrail decisions, success, inferred approval requirements, and error tags. Among 500 synthetic structured-input invoice cases, 498 have at least one action/guardrail/approval error: action type mismatch 189, unsuccessful execution 252, guardrail mismatch 210, approval-requirement mismatch 308 (categories overlap). Decision rows record 189 outcome mismatches, 35 risk mismatches, and 163 escalation mismatches (overlapping categories). The approval mapping is heuristic and needs policy-owner validation. Failures are not patched by case ID or hidden from the denominator.

The action evaluator now excludes cases without an expected-decision label from action, guardrail, and approval accuracy denominators instead of crediting an action for matching itself. In this generated run all 500 have labels. Approval requirement accuracy uses all labeled cases; predicted-positive blocked precision is clearly named and reported with its denominator. Frozen curated retrieval cases have no reviewer/adjudication provenance or invoice/job mapping, so they cannot serve as human-reviewed acceptance evidence. Layer 1 extraction remains NOT MEASURED: inputs are already structured synthetic invoices.

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

Candidate `7e620e7b5acabfe8ec374f72af11bfa157273bdd` (CI run `38217304451`, passed): eval data SHA-256 `177297e2c8cd78f21b45ad814dbe5079042be4d051b80649dc9ca3dadc8edfbd`; evidence corpus SHA-256 `09e5e36c37541f3e5dc3eadf7f9d0d1d6f5eda6406abecf5963260d93db66e86`. Structural inspection found 10 unique evaluation IDs, 235 unique evidence IDs, no duplicate IDs, and no missing references. The available schema has no reviewer/adjudication provenance or invoice/job mappings; this is integrity evidence only. Human-reviewed acceptance remains blocked.
