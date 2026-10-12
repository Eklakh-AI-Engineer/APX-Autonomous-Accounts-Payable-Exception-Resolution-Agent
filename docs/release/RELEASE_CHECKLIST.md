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

The invoice-processing regression is fixed. CI run `38208777459` at `82112a237fcb6bb8bb6a3cc4fb7f89e14386e1a7` passed the isolated repro, API and related focused modules, full backend suite (406 passed, 1 skipped), benchmark command, and configured Ruff job. Durable dispatch/recovery, benchmark integrity and quality acceptance, and ERP/deployment/monitoring/restore evidence still preclude release. No merge or `v1.0.0` tag was created. See [candidate audit](../audit/FINAL_AUDIT_REPORT.md) and [gap matrix](../audit/IMPLEMENTATION_GAP_MATRIX.md) for exact evidence and prerequisites.
