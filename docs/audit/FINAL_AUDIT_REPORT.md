# Release candidate audit — release blocked

Audit date: 2026-10-12. Candidate branch: `codex/v1-release-audit`. Candidate commit at audit: `ba55296116050d8b1d7527e2bd78b7cf6a8cb227`. Base: `0b6f30ed3a45db3f277cfe4179758d90a8aa593b`.

## Decision

**IMPLEMENTATION_INCOMPLETE / RELEASE_BLOCKED.** The candidate binds API requester and approver subjects to configured credentials, stores approval fingerprints and lifecycle fields, checks the binding at executor entry, removes profile-based DEV auto-approval, and fails closed for non-dry-run execution because a durable dispatch/reconciliation protocol is not configured. CI run `38206301164` on this exact candidate failed one focused API test; all focused tests completed (189 passed, 1 skipped, 1 failed), and the full suite and benchmark were skipped. Durable action claims/recovery, benchmark quality, ERP sandbox, deployment, alert delivery, and backup/restore remain unverified or blocked. Do not merge or tag `v1.0.0`.

## Verified evidence and limits

- Existing candidate history is preserved: `26f1079` and `723c3e5`; follow-up implementation commits include `110e901`, `eade059`, `26eed4b`, and subsequent focused fixes through `ba55296`.
- `process_invoice` requires an authenticated requester and uses it for approval/audit records. Approval routes ignore body-supplied approver identity; configured approver identity/group is taken from authentication middleware.
- Approval rows now carry action/evidence/policy fingerprints and expiration/revocation fields. `ApprovalService` checks expiry, revocation, role eligibility, and separation of duties. SQLite resolution uses one conditional terminal transition. The executor verifies the persisted binding for approved actions.
- Real execution is rejected before adapter dispatch while durable action ledger and unknown-outcome reconciliation are absent. Default adapters remain mocks. This is a safety block, not proof that a production dispatch protocol works.
- Local Python launch is unavailable in this Windows execution environment: `python` is not on PATH and `.venv-py312\Scripts\python.exe` cannot create its configured interpreter process. Earlier Python 3.12.10 setup had a clean `pip check`, but native imports were blocked by Windows Application Control; WSL remains inaccessible with `E_ACCESSDENIED`. The authorized hosted runner established Python 3.11.17, installed `.[dev]`, and ran the focused tests.
- Earlier focused pytest invocation produced `3 failed, 184 passed, 1 skipped` and two teardown errors (SQLite file `WinError 32`). The failures included the invoice API processing test and two phase 4 integration tests. Subsequent rerun could not load pytest configuration because of the blocked scikit-learn native extension. Those results predate the final two candidate commits and are not a passing verification.
- Ruff was invoked across the whole repository and reported 1,419 findings, mostly pre-existing repository-wide lint issues; the configured CI lint job is narrower. The command did not establish lint cleanliness.
- CI run `38206301164` for `ba55296` failed at `apx/tests/test_api.py::TestInvoiceEndpoints::test_process_invoice`: processing returned HTTP 500 rather than the expected 200. The run completed 189 focused tests successfully and skipped 1; the full suite and benchmark were skipped. The scoped Ruff job passed. No exception detail was emitted in the test summary. Therefore CI does not pass on the final candidate.
- `reports/evaluation/benchmark_gate.json` still records the 2026-08-19 historical benchmark as failed and requires a fresh run. No benchmark labels or thresholds were changed in this continuation.
- No authorized ERP sandbox, deployment target, external monitoring receiver, or backup target was available. No deployment, financial side effect, merge, or release tag was performed.

## Gate disposition

| Gate | Status | Evidence / remaining work |
|---|---|---|
| 1 — supported runtime | FAILED | Hosted Python 3.11.17 runner installed declared dev dependencies; focused CI failed on invoice processing (HTTP 500). Local Python launch is unavailable and WSL returns `E_ACCESSDENIED`. |
| 2 — approval boundary | INCOMPLETE | Identity, policy binding, expiry, and atomic resolution source changes are present. Focused API/approval tests completed except the invoice-processing regression. Revocation operation, legacy migration verification, and concurrent dispatch verification remain absent. |
| 3 — durable execution/recovery | BLOCKED | Production dispatch fails closed. Action ledger is not wired to dispatch; no durable retries, DLQ, downstream reference, or timeout reconciliation protocol. |
| 4 — benchmark integrity/quality | BLOCKED | Historical report fails; no fresh frozen benchmark execution or verified master scoreboard. |
| 5 — complete verification/operations | BLOCKED | Focused CI failed; full suite and benchmark were skipped; ERP sandbox, deploy/smoke, alert delivery, and isolated restore unavailable. |
| 6 — final release | BLOCKED | Required evidence is incomplete. Preserve candidate; do not merge or tag. |

See [implementation gap matrix](IMPLEMENTATION_GAP_MATRIX.md), [benchmark gate](../../reports/evaluation/benchmark_gate.json), and [release checklist](../release/RELEASE_CHECKLIST.md).
