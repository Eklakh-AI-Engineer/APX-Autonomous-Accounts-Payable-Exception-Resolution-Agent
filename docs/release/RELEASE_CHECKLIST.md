# v1.0.0 release checklist

**Current decision: BLOCKED. Do not tag.**

- [ ] Deterministic validation regressions pass on a supported environment.
- [ ] Approval subject is authenticated and policy is bound to invoice/action/parameters/policy/evidence.
- [ ] Separation of duties, expiry/revocation and execution-boundary checks fail closed.
- [ ] Production auto-approval bypass is removed and covered by tests.
- [ ] Durable approval/action transactions survive restart and concurrent workers.
- [ ] Idempotency, uncertain-outcome reconciliation and durable dead-letter replay pass failure injection.
- [ ] Dataset schema/checksum and evaluator denominator/label contracts pass independent review.
- [ ] Expected action, guardrail, approval and execution-failure labels have independent provenance, source invoice/job mappings, and policy-owner sign-off.
- [ ] Fresh benchmark meets predeclared quality and safety gates; all metrics are reported.
- [ ] Full backend, API, security, integration and required E2E suites pass.
- [ ] ERP sandbox dry-run and reconciliation pass with auditable evidence.
- [ ] Authorized deployment, health/smoke checks and rollback are verified.
- [ ] Monitoring alert delivery and backup/restore exercise pass.
- [ ] Threat model, operator docs, changelog, release notes and independent audit are current.
- [ ] Confirm clean release commit, CI result, and absence of an existing `v1.0.0` tag before tagging.

## Latest candidate evidence and release blockers (2026-10-12)

Candidate `540a3bd1dd32dc21f0bec32e58f0d4b15caba3dc` passed CI #144 (`38282478544`): API 61 passed/1 skipped, focused modules 132 passed, full suite 430 passed/1 skipped, configured Ruff passed, and deterministic DEV benchmark completed. The fresh benchmark artifact is `benchmark_dev_20261012_171707.json` (ID `11762555548`, SHA-256 `1da2ab46f89ba7e8299f4d4ef97c46c1e51792368b0afa55525e7d21d3b6ce7f`); test artifact ID `11762061701` (SHA-256 `b4b1b5528837e251333b65ecfa3fe146f6d1db15e0661b635bff50dea3b8da0d`).

Release acceptance remains blocked. Metrics on the 500 synthetic structured invoice cases: detection F1 85.99% (307 TP, 97 FP, 3 FN); decision outcome 62.20% (311/500); action type 62.20% (311/500); completion 49.60% (248/500); execution success 49.60% (248/500 attempts); guardrail 58.00% (290/500); inferred approval requirement 38.40% (192/500); blocked precision 0.94% (2/212) and recall 100% (2/2); evidence validity 57.67%. The blocked-recall denominator is only two positives. Comparison #138→#144 changed zero of 687 combined action/decision rows: 498 action-error and 189 decision-error rows. Error categories overlap. Evaluator retrieval uses 10 curated queries, each with relevant/invalid labels; it is not a 500-query benchmark. Validity is macro-averaged over query-specific candidate-validity ratios; invalid rejection is macro-averaged over 10 labeled queries. Frozen query set has 10 relevant IDs, 35 irrelevant IDs, and 2,305 invalid IDs. Dataset/evidence SHA-256 remain `177297e2c8cd78f21b45ad814dbe5079042be4d051b80649dc9ca3dadc8edfbd` / `09e5e36c37541f3e5dc3eadf7f9d0d1d6f5eda6406abecf5963260d93db66e86`; human-review provenance and invoice/job mappings are absent. CI #138 diagnostic output locates 22/48 invalid candidates: 20 stale against the pinned date and 2 with invalid outcomes. The agent now filters non-VALID evidence from model inputs and accepted evidence IDs; CI #144 verifies this boundary without changing the synthetic benchmark case rows. Inputs are synthetic structured invoices; document extraction/OCR is not measured.

Exact outstanding evidence: independent reviewers/adjudication records and source invoice/job IDs linked to frozen labels; policy-owner validation of approval/guardrail mappings and quality thresholds; a passing configured type-check, standalone security/dependency scan, and required E2E suite (the current workflow only runs narrowly scoped Ruff plus backend/API tests); authorized ERP sandbox/provider credentials and idempotency/reconciliation evidence; deployment credentials/target plus smoke/rollback evidence; monitoring receiver with actual alert delivery proof; backup destination, retention/RPO/RTO and isolated restore target/results; independent final audit. No such external credentials or targets are currently available. Keep live financial dispatch disabled, PR #4 draft, and do not merge or tag.

Historical snapshot (superseded by the latest candidate evidence above): tested code candidate `9179840cd029120e4d019ad421b91a1a5ea25d39` passed CI push run `38228330768` (#91) and PR run `38228335549` (#92): full suite 423 passed, 1 skipped; API 61 passed, 1 skipped; deterministic DEV benchmark and configured Ruff passed. Migration from a populated legacy schema is covered and passed in the full suite. The benchmark pass is limited to configured gates; updated scoring reports action completion 49.60% (248/500), action-type accuracy 62.20% (311/500), execution success 49.60% (248/500 attempts), guardrail accuracy 58.00% (290/500), inferred approval-requirement accuracy 38.40% (192/500), blocked-decision precision 0.94% (2/212 predicted BLOCK); 498/500 cases have an action/guardrail/approval error. The enum-normalization fix produced zero case-level changes versus run #83 across action and decision error rows, and zero row changes compared with run #90; a new direct plain non-string Enum regression test passes in CI. Decision/action/evidence quality, reviewer provenance, invoice/job mappings, and independent document extraction remain unresolved. Ad-hoc mypy did not pass. ERP sandbox, deployment smoke, actual alert delivery, isolated restore, security/dependency scanning, and required E2E evidence remain open. Keep PR #4 draft and do not merge/tag. Benchmark artifact `benchmark_dev_20261012_091921.json` (seed 42, pinned date 2026-08-29); dataset SHA-256 values are unchanged and recorded in the scoreboard. The documentation snapshot commit will be separately CI-verified. See [candidate audit](../audit/FINAL_AUDIT_REPORT.md), [gap matrix](../audit/IMPLEMENTATION_GAP_MATRIX.md), and [master scoreboard](../../reports/evaluation/master_scoreboard.md).

## Evidence-chain status

- Latest candidate `540a3bd1dd32dc21f0bec32e58f0d4b15caba3dc` is CI-verified by run #144 (`38282478544`); the latest audit head passed CI.
- Latest benchmark result and denominators are recorded above and in the current benchmark gate and master scoreboard; previous benchmark runs remain historical.
- Current CI evidence: run #144 succeeded on `540a3bd`; see the candidate evidence above.
- Release acceptance remains `BLOCKED`; preserve PR #4 as draft and unmerged, do not tag `v1.0.0`, and keep live financial dispatch disabled.
