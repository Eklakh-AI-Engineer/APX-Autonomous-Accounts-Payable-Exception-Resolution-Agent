# Implementation gap matrix

Snapshot: `codex/v1-release-audit` at candidate `eade05999b170687f82027caa3e6033b671cdec3`, base `0b6f30ed3a45db3f277cfe4179758d90a8aa593b`. Source implementation, runtime evidence, and external prerequisites are tracked separately.

| Requirement | Source status | Runtime / acceptance evidence | Remaining gap | Status |
|---|---|---|---|---|
| Deterministic R1–R10 validation | Existing validator and regression suite retained | Earlier focused run included failures; final candidate CI is pending | Run complete supported suite after candidate CI stabilizes | BLOCKED |
| Authenticated requester identity | Invoice API passes authenticated subject; service rejects missing or `system` requester | Not verified on final candidate | Run API regressions in supported Linux CI | IMPLEMENTED_NOT_VERIFIED |
| Approver identity, eligibility, separation of duties | API ignores body identity; authentication supplies principal/groups; service checks policy and requester mismatch | Earlier focused API test run predates final candidate; CI pending | Verify role/group mapping with tests; select authoritative production identity provider | IMPLEMENTED_NOT_VERIFIED |
| Approval action/evidence/policy binding | Fingerprints persisted with lifecycle fields; executor revalidates action fingerprint and expiry/revocation state | No migration or final runtime test evidence | Test old-database migration, payload tampering, expiry/revocation, concurrent approval and dispatch | INCOMPLETE |
| DEV auto-approval prevention | Profile-based implicit approval removed | Regression tests added; final CI pending | Confirm full phase 4 suite in CI | IMPLEMENTED_NOT_VERIFIED |
| Production dispatch boundary | Non-dry-run executor returns before invoking an adapter | Regression test added; final CI pending | Durable action claim and verified authorization required before this block can be safely lifted | FAIL_CLOSED / RELEASE BLOCKER |
| Durable action intent, idempotency, recovery, DLQ | Action ORM/repository and unique idempotency field exist; not wired through a durable dispatch/reconciliation protocol | No restart/concurrency/fault injection evidence | Persist atomic dispatch claims, outcomes, downstream references, retry/DLQ state; reconcile unknown outcome before retry | BLOCKED |
| Benchmark schema and provenance | Historical benchmark artifacts and generated benchmark workflow exist | `reports/evaluation/benchmark_gate.json` requires a fresh run; historical artifact failed | Validate frozen reviewer-labelled corpus, IDs, schema, mapping, provenance, hashes, and missing-label denominators | BLOCKED |
| Benchmark quality and economic model | Historical scoreboard reports multiple poor metrics | No current run; no verified master scoreboard | Analyze error categories; add required metrics/cost separation and run predeclared gates without changing labels/thresholds | BLOCKED |
| Backend, integration, E2E, lint, types, security | CI workflow covers focused/full tests, benchmark, and scoped Ruff job | CI #51 on `110e901` cancelled (Ruff passed); CI #52 on `eade059` failed focused test step with exit 1; full suite/benchmark skipped | Diagnose focused regressions, rerun focused and full suites on exact final candidate, then configured scans/type checks | FAILED |
| ERP sandbox | Only mock adapters are registered by default | No authorized ERP sandbox or adapter available | Select ERP, provide sandbox access, add idempotent/reconcilable adapter and execute simulator/sandbox fault tests | BLOCKED — external prerequisite |
| Deployment and smoke tests | FastAPI app and health route exist | No deployment target/configuration or authorization | Provide authorized deployment target and credentials, then deploy and run authenticated smoke tests | BLOCKED — external prerequisite |
| Monitoring and alert delivery | In-process instrumentation exists | No external sink, receiver, or delivery proof | Configure provider/receiver and execute alert-to-response test | BLOCKED — external prerequisite |
| Backup and isolated restore | SQLite persistence and generic runbook exist | No backup target or restore evidence | Define RPO/RTO and retention; backup then isolated restore action/idempotency state and verify integrity | BLOCKED — external prerequisite |
| Release audit and tag | Candidate branch pushed; prior commits preserved | Candidate CI incomplete; no release approval evidence | Complete every mandatory gate and independent final review; do not merge/tag while any gate is blocked | BLOCKED |

## External prerequisites

- Host administrator or supported Linux runner for Python/scikit-learn execution; the local Windows policy blocks the native extension and WSL returns `E_ACCESSDENIED`.
- ERP product choice, authorized sandbox credentials, and downstream idempotency/reconciliation capabilities.
- Authorized deployment environment and credentials.
- Monitoring provider/receiver and named alert responders.
- Backup destination, retention, RPO/RTO, and isolated restore target.
