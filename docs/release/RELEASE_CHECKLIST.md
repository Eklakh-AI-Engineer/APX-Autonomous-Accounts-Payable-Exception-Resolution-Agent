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

Current CI run `38206301164` on `ba55296116050d8b1d7527e2bd78b7cf6a8cb227` failed `test_process_invoice` (HTTP 500); 189 focused tests passed and 1 was skipped. Full tests and benchmark were skipped. Durable dispatch/recovery, the failed historical benchmark gate, and missing ERP/deployment/monitoring/restore evidence also preclude release. No merge or `v1.0.0` tag was created. See [candidate audit](../audit/FINAL_AUDIT_REPORT.md) and [gap matrix](../audit/IMPLEMENTATION_GAP_MATRIX.md) for exact evidence and prerequisites.
