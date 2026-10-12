# v1.0.0 release checklist

**Current decision: BLOCKED. Do not tag.**

- [ ] Deterministic validation regressions pass on a supported environment.
- [ ] Approval subject is authenticated and policy is bound to invoice/action/parameters/policy/evidence.
- [ ] Separation of duties, expiry/revocation and execution-boundary checks fail closed.
- [ ] Production auto-approval bypass is removed and covered by tests.
- [ ] Durable approval/action transactions survive restart and concurrent workers.
- [ ] Idempotency, uncertain-outcome reconciliation and durable dead-letter replay pass failure injection.
- [ ] Dataset schema/checksum and evaluator denominator/label contracts pass independent review.
- [ ] Fresh benchmark meets predeclared quality and safety gates; all metrics are reported.
- [ ] Full backend, API, security, integration and required E2E suites pass.
- [ ] ERP sandbox dry-run and reconciliation pass with auditable evidence.
- [ ] Authorized deployment, health/smoke checks and rollback are verified.
- [ ] Monitoring alert delivery and backup/restore exercise pass.
- [ ] Threat model, operator docs, changelog, release notes and independent audit are current.
- [ ] Confirm clean release commit, CI result, and absence of an existing `v1.0.0` tag before tagging.

Tested code candidate `9179840cd029120e4d019ad421b91a1a5ea25d39` passed CI push run `38228330768` (#91) and PR run `38228335549` (#92): full suite 423 passed, 1 skipped; API 61 passed, 1 skipped; deterministic DEV benchmark and configured Ruff passed. Migration from a populated legacy schema is covered and passed in the full suite. The benchmark pass is limited to configured gates; updated scoring reports action completion 49.60% (248/500), action-type accuracy 62.20% (311/500), execution success 49.60% (248/500 attempts), guardrail accuracy 58.00% (290/500), inferred approval-requirement accuracy 38.40% (192/500), blocked-decision precision 0.94% (2/212 predicted BLOCK); 498/500 cases have an action/guardrail/approval error. The enum-normalization fix produced zero case-level changes versus run #83 across action and decision error rows, and zero row changes compared with run #90; a new direct plain non-string Enum regression test passes in CI. Decision/action/evidence quality, reviewer provenance, invoice/job mappings, and independent document extraction remain unresolved. Ad-hoc mypy did not pass. ERP sandbox, deployment smoke, actual alert delivery, isolated restore, security/dependency scanning, and required E2E evidence remain open. Keep PR #4 draft and do not merge/tag. Benchmark artifact `benchmark_dev_20261012_091921.json` (seed 42, pinned date 2026-08-29); dataset SHA-256 values are unchanged and recorded in the scoreboard. The documentation snapshot commit will be separately CI-verified. See [candidate audit](../audit/FINAL_AUDIT_REPORT.md), [gap matrix](../audit/IMPLEMENTATION_GAP_MATRIX.md), and [master scoreboard](../../reports/evaluation/master_scoreboard.md).

## Evidence-chain status

- Current metadata synchronization is based on branch head `149a47f6915042efc6cad80a9b9cf6643746673d`; it changes audit/scoreboard documentation only.
- Latest benchmarked code/evaluator candidate: `9179840cd029120e4d019ad421b91a1a5ea25d39`, run #91 (`38228330768`), artifact `benchmark_dev_20261012_091921.json`. Its numbers remain attributed to that code candidate, not to documentation commits.
- Latest completed CI previously verified the metadata/code continuation at `e9f56ffc3a34047b277d8e18afe6fcae5de366d2`, run #94 (`38229883761`): API 61 passed/1 skipped, full suite 423 passed/1 skipped, configured Ruff passed, benchmark completed. Subsequent documentation commits trigger separate CI; verify the current PR head's check result before stating those commits passed.
- Release acceptance remains `BLOCKED`; preserve PR #4 as draft and unmerged, do not tag `v1.0.0`, and keep live financial dispatch disabled.
