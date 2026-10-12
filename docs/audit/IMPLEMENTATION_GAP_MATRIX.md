# Implementation gap matrix

Snapshot: `codex/v1-release-audit` at candidate `ba55296116050d8b1d7527e2bd78b7cf6a8cb227`, base `0b6f30ed3a45db3f277cfe4179758d90a8aa593b`. Source implementation, runtime evidence, and external prerequisites are tracked separately.

| Requirement | Source status | Runtime / acceptance evidence | Remaining gap | Status |
|---|---|---|---|---|
| Deterministic R1–R10 validation | Existing validator and regression suite retained | CI run `38206301164` used Python 3.11.17; focused tests 189 passed, 1 skipped, 1 failed | Fix invoice process HTTP 500, then run complete supported suite | FAILED |
| Authenticated requester identity | Invoice API passes authenticated subject; service rejects missing or `system` requester | Focused API test exercises invoice processing but gets HTTP 500; failure detail is not in pytest summary | Diagnose and fix the process failure; rerun API regressions | FAILED |
| Approver identity, eligibility, separation of duties | API ignores body identity; authentication supplies principal/groups; service checks policy and requester mismatch | Focused run completed 189 tests; sole failed item was `test_process_invoice`; scoped approval tests passed | Select authoritative production identity provider and run concurrency/migration acceptance | IMPLEMENTED_NOT_VERIFIED |
| Approval action/evidence/policy binding | Fingerprints persisted with lifecycle fields; executor revalidates action fingerprint and expiry/revocation state | No migration or final runtime test evidence | Test old-database migration, payload tampering, expiry/revocation, concurrent approval and dispatch | INCOMPLETE |
| DEV auto-approval prevention | Profile-based implicit approval removed | Regression tests added; final CI pending | Confirm full phase 4 suite in CI | IMPLEMENTED_NOT_VERIFIED |
| Production dispatch boundary | Non-dry-run executor returns before invoking an adapter | Regression test added; final CI pending | Durable action claim and verified authorization required before this block can be safely lifted | FAIL_CLOSED / RELEASE BLOCKER |
| Durable action intent, idempotency, recovery, DLQ | Action ORM/repository and unique idempotency field exist; not wired through a durable dispatch/reconciliation protocol | No restart/concurrency/fault injection evidence | Persist atomic dispatch claims, outcomes, downstream references, retry/DLQ state; reconcile unknown outcome before retry | BLOCKED |
| Benchmark schema and provenance | Historical benchmark artifacts and generated benchmark workflow exist | `reports/evaluation/benchmark_gate.json` requires a fresh run; historical artifact failed | Validate frozen reviewer-labelled corpus, IDs, schema, mapping, provenance, hashes, and missing-label denominators | BLOCKED |
| Benchmark quality and economic model | Historical scoreboard reports multiple poor metrics | No current run; no verified master scoreboard | Analyze error categories; add required metrics/cost separation and run predeclared gates without changing labels/thresholds | BLOCKED |
| Backend, integration, E2E, lint, types, security | CI workflow covers focused/full tests, benchmark, and scoped Ruff job | CI run `38206301164` at `ba55296`: 189 passed, 1 skipped, 1 failed (`test_process_invoice`, HTTP 500); full suite/benchmark skipped; scoped Ruff passed | Diagnose failure; rerun focused and full suites on exact final candidate, then configured scans/type checks | FAILED |
| ERP sandbox | Only mock adapters are registered by default | No authorized ERP sandbox or adapter available | Select ERP, provide sandbox access, add idempotent/reconcilable adapter and execute simulator/sandbox fault tests | BLOCKED — external prerequisite |
| Deployment and smoke tests | FastAPI app and health route exist | No deployment target/configuration or authorization | Provide authorized deployment target and credentials, then deploy and run authenticated smoke tests | BLOCKED — external prerequisite |
| Monitoring and alert delivery | In-process instrumentation exists | No external sink, receiver, or delivery proof | Configure provider/receiver and execute alert-to-response test | BLOCKED — external prerequisite |
| Backup and isolated restore | SQLite persistence and generic runbook exist | No backup target or restore evidence | Define RPO/RTO and retention; backup then isolated restore action/idempotency state and verify integrity | BLOCKED — external prerequisite |
| Release audit and tag | Candidate branch pushed; prior commits preserved | Candidate CI incomplete; no release approval evidence | Complete every mandatory gate and independent final review; do not merge/tag while any gate is blocked | BLOCKED |

## External prerequisites

- Host administrator or supported Linux runner for Python/scikit-learn execution; the local Windows policy blocks the native extension and WSL returns `E_ACCESSDENIED`.
- Diagnosis of the CI API processing failure; the summarized failure contains status code but no underlying exception detail.
- ERP product choice, authorized sandbox credentials, and downstream idempotency/reconciliation capabilities.
- Authorized deployment environment and credentials.
- Monitoring provider/receiver and named alert responders.
- Backup destination, retention, RPO/RTO, and isolated restore target.
