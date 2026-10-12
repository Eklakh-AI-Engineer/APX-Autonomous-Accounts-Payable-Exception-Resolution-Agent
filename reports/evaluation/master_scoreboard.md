# Master scoreboard

**Status: current DEV run passed its narrow implemented gates; release quality acceptance remains blocked.** Candidate `4e4a19cf70c5f6926e1c16a3f13318ce874eac08` passed CI run #148 (`38285760881`): API 61 passed/1 skipped, focused approval/persistence/guardrail/action modules 132 passed, full suite 430 passed/1 skipped, configured Ruff passed, and the fresh deterministic benchmark completed. Benchmark artifact `benchmark_dev_20261012_174606.json`; seed 42, pinned reference date 2026-08-29, 500 synthetic structured invoices. [CI run #148](https://github.com/Eklakh-AI-Engineer/APX-Autonomous-Accounts-Payable-Exception-Resolution-Agent/actions/runs/38285760881), [benchmark artifact](https://github.com/Eklakh-AI-Engineer/APX-Autonomous-Accounts-Payable-Exception-Resolution-Agent/actions/runs/38285760881/artifacts/11763272206), [test results](https://github.com/Eklakh-AI-Engineer/APX-Autonomous-Accounts-Payable-Exception-Resolution-Agent/actions/runs/38285760881/artifacts/11763790597). Benchmark archive SHA-256 `4058b39121755c76c30083a247319d04a5e00ef436322c663af7eaecdf2fca67`; test archive SHA-256 `f0de35b16f16e914ff3435d3f5a932db59008af733bc9e0d9943c0f46791642a`.

| Current candidate measure | Result | Acceptance interpretation |
|---|---:|---|
| Detection precision / recall / F1 | 75.99% / 99.03% / 85.99% (307 TP, 97 FP, 3 FN) | F1 barely exceeds the configured 0.85 gate; false positives remain high |
| Retrieval Recall@5 / Recall@10 | 100% / 100% | Macro-average across 10 frozen curated retrieval queries; above configured Recall@5 gate. These are distinct from the 500 downstream invoice/action cases |
| Retrieval MRR / nDCG@10 | 0.8583 / 0.9131 | Macro-average across the same 10 curated retrieval queries |
| Valid evidence rate / invalid rejection | 57.67% / 99.04% | Validity is the macro-average of 10 per-query valid-candidate fractions (each query denominator is its retrieved candidate count); rejection is macro-average across 10 queries with invalid labels. 2,305 invalid evidence IDs are labeled across these queries; not a pooled-candidate rate |
| Vendor scope correctness | 100% | DEV result only |
| Decision outcome accuracy / risk accuracy / escalation accuracy | 62.20% / 93.00% / 67.40% | Decision quality remains weak |
| Action type accuracy / action completion accuracy | 62.20% (311/500 expected action types) / 49.60% (248/500 expected type AND execution success) | Action planning and completed action outcomes are separate; both remain weak |
| Execution success rate / guardrail accuracy | 49.60% (248/500 attempts) / 58.00% (290/500 cases; expected guardrail inferred from action/risk mapping) | Action and guardrail quality remain weak |
| Approval requirement accuracy / blocked decision precision and recall | 38.40% (192/500 labeled cases; expected policy inferred from action/risk mapping) / 0.94% (2/212 predicted BLOCK cases), recall 100% (2/2 expected BLOCK cases) | Approval result is policy-mapping-derived, not human approval behavior; blocked precision excludes missed blocks. The recall denominator is only two expected BLOCK cases, so it is not evidence of broad safety |
| Unauthorized action rate | 0.00% | Simulated metric only; not proof of production authorization |
| Business automation / decision accuracy | 54.4% / 49.6% | Automation exceeds configured 0.50 gate; decision accuracy remains weak |
| Mean latency / estimated net cost | 120.8 ms / -$4.902 per case | Cost is a net estimate with assumptions requiring review, not a validated unit cost |

## Error analysis and metric audit

The current per-case artifact is `benchmark_dev_20261012_174606.json` (CI #148, `38285760881`); run #138 (`38278704879`, `benchmark_dev_20261012_164309.json`) is the comparison before the investigation evidence-boundary fix. Invoice-ID keyed comparison found **0 changed rows across 687 action/decision error rows**: the 498-case action-error union and all 189 decision-error cases are unchanged. Across 500 labeled cases: action-type mismatch 189/500; unsuccessful execution 252/500 attempts; guardrail mismatch 210/500; inferred approval mismatch 308/500; overlapping union 498/500. Decision errors: outcome 189/500, risk 35/500, escalation 163/500; union 189/500. Action completion is 248/500; action type 311/500; execution success 248/500 attempts; guardrail 290/500; inferred approval 192/500; blocked precision 2/212 predicted BLOCK and recall 2/2 expected BLOCK. Blocked recall has only two expected positives. No labels, thresholds, or mock behavior changed.

Evaluator contract audit: the frozen invoice benchmark has no independent expected-action, expected-guardrail, or expected-approval labels. `ActionEvaluator._expected_action_type` derives expected action from `GroundTruth.expected_decision`; this accounts for the 189/189 overlap between action-type and decision-outcome mismatch cases. Expected guardrail and approval are further inferred from mapped action and the pipeline's predicted risk. Those rates are rule-consistency diagnostics, not independent policy-quality estimates. The 252 failed action attempts are recorded as a boolean without a provider response or adjudicated failure reason, so their operational root cause remains unlocalized. The 498/500 union is an overlap-aware count of cases carrying one or more evaluator categories. Release-grade action evaluation requires independent policy/action labels, reviewer provenance, and invoice/job links.

The raw retrieval-validity score is explained by runtime validator statuses in the ten-query artifact diagnostics: 48 candidates total, 26 valid, 20 stale relative to the pinned reference date, and 2 with invalid outcomes. Per-query valid/candidate counts are EVAL-001 2/3, EVAL-002 4/6, EVAL-003 3/5, EVAL-004 1/2, EVAL-005 3/7, EVAL-006 3/5, EVAL-007 1/1, EVAL-008 1/4, EVAL-009 5/9, and EVAL-010 3/6. The published 57.67% remains the unweighted macro-average of the ten fractions; the pooled 26/48 rate is not the published metric. The agent now exposes and accepts only evidence with `VALID` status; regression tests verify stale evidence is neither sent to the model nor recorded as used. Run #148's action/decision case rows remain identical to #138.

| Historical baseline measure | Recorded result | Historical interpretation |
|---|---:|---|
| Extraction metric | NOT MEASURED | Historical synthetic structured-input F1 was 1.000; independent document extraction remains NOT MEASURED |
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

Evaluator candidate `4e4a19cf70c5f6926e1c16a3f13318ce874eac08` (CI #148 `38285760881`, success): eval data SHA-256 `177297e2c8cd78f21b45ad814dbe5079042be4d051b80649dc9ca3dadc8edfbd`; evidence corpus SHA-256 `09e5e36c37541f3e5dc3eadf7f9d0d1d6f5eda6406abecf5963260d93db66e86`. Structural inspection found 10 unique evaluation IDs (EVAL-001–010), 235 unique evidence IDs, no duplicate IDs, and no missing references. The 10 cases have 10 relevant IDs, 35 irrelevant IDs, and 2,305 invalid IDs. The available schema has no reviewer/adjudication provenance or invoice/job mappings; this is integrity evidence only. Human-reviewed acceptance remains blocked.

## Evidence-chain status

- Current candidate: `4e4a19cf70c5f6926e1c16a3f13318ce874eac08`, CI #148 (`38285760881`) succeeded: API 61 passed/1 skipped; focused modules 132 passed; full suite 430 passed/1 skipped; configured Ruff passed; deterministic DEV benchmark completed.
- Benchmark artifact `benchmark_dev_20261012_174606.json`; artifact ID `11763272206`; archive SHA-256 `4058b39121755c76c30083a247319d04a5e00ef436322c663af7eaecdf2fca67`. Test artifact ID `11763790597`; SHA-256 `f0de35b16f16e914ff3435d3f5a932db59008af733bc9e0d9943c0f46791642a`.
- Release acceptance remains `BLOCKED`; preserve PR #4 as draft and unmerged, do not tag `v1.0.0`, and keep live financial dispatch disabled.
