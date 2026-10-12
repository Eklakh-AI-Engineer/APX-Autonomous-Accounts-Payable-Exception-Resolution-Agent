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

Candidate `37e61bd21f9d121e08e04462afa3063030989f6d` passed CI push run `38223749502` and PR run `38223756416`: full suite 421 passed, 1 skipped; API 61 passed, 1 skipped; deterministic DEV benchmark and configured Ruff passed. Migration from a populated legacy schema is covered and passed in the full suite. The benchmark pass is limited to configured gates; updated scoring reports action accuracy 49.60%, guardrail accuracy 58.00%, inferred approval-requirement accuracy 38.40%, blocked-decision precision 0.94%, and 498/500 cases with at least one action-related error. Decision/action/evidence quality, reviewer provenance, invoice/job mappings, and independent document extraction remain unresolved. Ad-hoc mypy did not pass. ERP sandbox, deployment smoke, actual alert delivery, isolated restore, security/dependency scanning, and required E2E evidence remain open. Keep PR #4 draft and do not merge/tag. See [candidate audit](../audit/FINAL_AUDIT_REPORT.md), [gap matrix](../audit/IMPLEMENTATION_GAP_MATRIX.md), and [master scoreboard](../../reports/evaluation/master_scoreboard.md).
