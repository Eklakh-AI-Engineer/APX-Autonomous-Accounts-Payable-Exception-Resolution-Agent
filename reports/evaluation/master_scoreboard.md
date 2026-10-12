# Master scoreboard

**Status: current DEV run passed its narrow implemented gates; release quality acceptance remains blocked.** Latest CI-verified code commit `37e61bd21f9d121e08e04462afa3063030989f6d`; CI push run `38223749502` (run 81) and PR run `38223756416` (run 82) succeeded: full suite 421 passed, 1 skipped. Output `benchmark_dev_20261012_083441.json`, DEV, seed 42, reference date 2026-08-29, 500 synthetic structured invoices. Artifact: [CI benchmark evidence](https://github.com/Eklakh-AI-Engineer/APX-Autonomous-Accounts-Payable-Exception-Resolution-Agent/actions/runs/38223749502/artifacts/11734749508).

| Current candidate measure | Result | Acceptance interpretation |
|---|---:|---|
| Detection precision / recall / F1 | 75.99% / 99.03% / 85.99% (307 TP, 97 FP, 3 FN) | F1 barely exceeds the configured 0.85 gate; false positives remain high |
| Retrieval Recall@5 / Recall@10 | 100% / 100% | Above configured Recall@5 gate on generated DEV cases and the ten-case curated retrieval subset |
| Retrieval MRR / nDCG@10 | 0.8583 / 0.9131 | DEV result only |
| Valid evidence rate / invalid rejection | 57.67% / 99.04% | Validity remains low; investigate without adapting to unreviewed labels |
| Vendor scope correctness | 100% | DEV result only |
| Decision outcome accuracy / risk accuracy / escalation accuracy | 62.20% / 93.00% / 67.40% | Decision quality remains weak |
| Action type accuracy / action completion accuracy | 62.20% (311/500 expected action types) / 49.60% (248/500 expected type AND execution success) | Action planning and completed action outcomes are separate; both remain weak |
| Execution success rate / guardrail accuracy | 49.60% (248/500 attempts) / 58.00% (290/500 cases; expected guardrail inferred from action/risk mapping) | Action and guardrail quality remain weak |
| Approval requirement accuracy / blocked decision precision | 38.40% (192/500 labeled cases; expected policy inferred from action/risk mapping) / 0.94% (2/212 predicted BLOCK cases) | Approval result is policy-mapping-derived, not human approval behavior; blocked precision excludes missed blocks |
| Unauthorized action rate | 0.00% | Simulated metric only; not proof of production authorization |
| Business automation / decision accuracy | 54.4% / 49.6% | Automation exceeds configured 0.50 gate; decision accuracy remains weak |
| Mean latency / estimated net cost | 119.1 ms / -$4.902 per case | Cost is a net estimate with assumptions requiring review, not a validated unit cost |

## Error analysis and metric audit

The fresh report records case-level expected/actual decisions, action types, guardrail decisions, success, inferred approval requirements, and error tags. Among 500 synthetic structured-input invoice cases, 498 have at least one action/guardrail/approval error: action type mismatch 189, unsuccessful execution 252, guardrail mismatch 210, approval-requirement mismatch 308 (categories overlap). Decision rows record 189 outcome mismatches, 35 risk mismatches, and 163 escalation mismatches (overlapping categories). The approval mapping is heuristic and needs policy-owner validation. Failures are not patched by case ID or hidden from the denominator.

The action evaluator now excludes cases without an expected-decision label from action, guardrail, and approval accuracy denominators instead of crediting an action for matching itself. It separates action-type planning (62.20%) from completion (49.60%, requiring both expected type and success) and execution success (49.60%). In this generated run all 500 have labels. Approval requirement accuracy uses all labeled cases; predicted-positive blocked precision is clearly named and reported with its denominator. Frozen curated retrieval cases have no reviewer/adjudication provenance or invoice/job mapping, so they cannot serve as human-reviewed acceptance evidence. Layer 1 extraction remains NOT MEASURED: inputs are already structured synthetic invoices.

| Historical baseline measure | Recorded result | Historical interpretation |
|---|---:|---|
| Extraction F1 | 1.000 | Historical synthetic structured-input metric; independent document extraction remains NOT MEASURED |
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

Candidate `37e61bd21f9d121e08e04462afa3063030989f6d` (push run `38223749502` passed): eval data SHA-256 `177297e2c8cd78f21b45ad814dbe5079042be4d051b80649dc9ca3dadc8edfbd`; evidence corpus SHA-256 `09e5e36c37541f3e5dc3eadf7f9d0d1d6f5eda6406abecf5963260d93db66e86`. Structural inspection found 10 unique evaluation IDs, 235 unique evidence IDs, no duplicate IDs, and no missing references. The available schema has no reviewer/adjudication provenance or invoice/job mappings; this is integrity evidence only. Human-reviewed acceptance remains blocked.
