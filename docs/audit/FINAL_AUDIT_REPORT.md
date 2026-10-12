# Release candidate audit — release blocked

Audit date: 2026-10-12. Candidate branch: `codex/v1-release-audit`. Implementation tested at `82112a237fcb6bb8bb6a3cc4fb7f89e14386e1a7`; audit docs updated in a descendant commit. Base: `0b6f30ed3a45db3f277cfe4179758d90a8aa593b`.

## Decision

**IMPLEMENTATION_INCOMPLETE / RELEASE_BLOCKED.** The candidate binds API requester and approver subjects to configured credentials, stores approval fingerprints and lifecycle fields, checks the binding at executor entry, removes profile-based DEV auto-approval, and fails closed for non-dry-run execution because a durable dispatch/reconciliation protocol is not configured. The invoice-processing regression is fixed and CI run `38208777459` passed the isolated repro, API module, related focused modules, full backend suite, benchmark command, and configured Ruff job. Durable action claims/recovery, benchmark integrity/quality acceptance, ERP sandbox, deployment, alert delivery, and backup/restore remain unverified or blocked. Do not merge or tag `v1.0.0`.

## Verified evidence and limits

- Existing candidate history is preserved: `26f1079` and `723c3e5`; follow-up implementation commits include `110e901`, `eade059`, `26eed4b`, and subsequent focused fixes through `ba55296`.
- `process_invoice` requires an authenticated requester and uses it for approval/audit records. Approval routes ignore body-supplied approver identity; configured approver identity/group is taken from authentication middleware.
- Approval rows now carry action/evidence/policy fingerprints and expiration/revocation fields. `ApprovalService` checks expiry, revocation, role eligibility, and separation of duties. SQLite resolution uses one conditional terminal transition. The executor verifies the persisted binding for approved actions.
- Real execution is rejected before adapter dispatch while durable action ledger and unknown-outcome reconciliation are absent. Default adapters remain mocks. This is a safety block, not proof that a production dispatch protocol works.
- Regression diagnosis: CI run `38208337598` logged `UnboundLocalError` at stage `case_completion`, with the final service frame in `InvoiceService.process_invoice`. `ApprovalStatus` was imported inside the conditional approval-creation branch, making it a local name for the whole function; the no-approval path skipped that import and later referenced the unbound name. `git blame` attributes the conditional import to the earlier Phase 6C approval integration (`bed9fa6`), so this was pre-existing and not introduced by the current approval-binding changes. The fix removes the conditional `ApprovalStatus` import and uses the existing module-level import. The route now logs exception type, stage, correlation/request IDs, and traceback frame coordinates without exception messages or source lines; public 500 responses are generic.
- CI run `38208777459` at `82112a2`: isolated invoice repro **1 passed**; API module **61 passed, 1 skipped**; related modules **130 passed**; full `apx/tests` suite **406 passed, 1 skipped**; deterministic development benchmark command succeeded; configured Ruff job succeeded. Earlier warnings remain non-failing.
- Local Python launch is unavailable in this Windows execution environment: `python` is not on PATH and `.venv-py312\Scripts\python.exe` cannot create its configured interpreter process. Earlier Python 3.12.10 setup had a clean `pip check`, but native imports were blocked by Windows Application Control; WSL remains inaccessible with `E_ACCESSDENIED`. The authorized hosted runner established Python 3.11.17, installed `.[dev]`, and ran the focused tests.
- Earlier focused pytest invocation produced `3 failed, 184 passed, 1 skipped` and two teardown errors (SQLite file `WinError 32`). The failures included the invoice API processing test and two phase 4 integration tests. Subsequent rerun could not load pytest configuration because of the blocked scikit-learn native extension. Those results predate the final two candidate commits and are not a passing verification.
- Ruff was invoked across the whole repository and reported 1,419 findings, mostly pre-existing repository-wide lint issues; the configured CI lint job is narrower. The command did not establish lint cleanliness.
- Earlier CI runs `38206301164` and `38207055833` failed on invoice processing before diagnostic logging was added. The failure was root-caused and fixed; run `38208777459` passes the complete backend suite and configured checks as recorded above.
- `reports/evaluation/benchmark_gate.json` still records the 2026-08-19 historical benchmark as failed and requires a fresh run. No benchmark labels or thresholds were changed in this continuation.
- No authorized ERP sandbox, deployment target, external monitoring receiver, or backup target was available. No deployment, financial side effect, merge, or release tag was performed.

## Gate disposition

| Gate | Status | Evidence / remaining work |
|---|---|---|
| 1 — supported runtime | PASS (hosted) | Hosted Python 3.11.17 runner installed declared dev dependencies; complete backend suite passed (406 passed, 1 skipped). Local Python launch remains unavailable and WSL returns `E_ACCESSDENIED`. |
| 2 — approval boundary | INCOMPLETE | Identity, policy binding, expiry, atomic resolution, and fail-closed paths are present; API/action/persistence tests pass. Revocation operation, legacy migration verification, and concurrent dispatch verification remain absent. |
| 3 — durable execution/recovery | BLOCKED | Production dispatch fails closed. Action ledger is not wired to dispatch; no durable retries, DLQ, downstream reference, or timeout reconciliation protocol. |
| 4 — benchmark integrity/quality | BLOCKED | Historical report fails; no fresh frozen benchmark execution or verified master scoreboard. |
| 5 — complete verification/operations | BLOCKED | Backend suite and CI benchmark command passed. ERP sandbox, deploy/smoke, alert delivery, isolated restore, and additional configured type/security/E2E scans remain unavailable or unverified. |
| 6 — final release | BLOCKED | Required evidence is incomplete. Preserve candidate; do not merge or tag. |

See [implementation gap matrix](IMPLEMENTATION_GAP_MATRIX.md), [benchmark gate](../../reports/evaluation/benchmark_gate.json), and [release checklist](../release/RELEASE_CHECKLIST.md).
