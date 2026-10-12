# Implementation gap matrix

Snapshot: `codex/v1-release-audit`, implementation tested at `82112a237fcb6bb8bb6a3cc4fb7f89e14386e1a7` (audit updates in a descendant commit), base `0b6f30ed3a45db3f277cfe4179758d90a8aa593b`. Source implementation, runtime evidence, and external prerequisites are tracked separately.

| Requirement | Source status | Runtime / acceptance evidence | Remaining gap | Status |
|---|---|---|---|---|
| Deterministic R1–R10 validation | Existing validator and regression suite retained | CI run `38208777459`: full backend suite 406 passed, 1 skipped | Continue with remaining release gates and preserve current regression coverage | PASS (backend suite) |
| Authenticated requester identity | Invoice API passes authenticated subject; service rejects missing or `system` requester | Isolated process test passed; API suite 61 passed, 1 skipped | Select authoritative production identity provider | IMPLEMENTED / TESTED |
| Approver identity, eligibility, separation of duties | API ignores body identity; authentication supplies principal/groups; service checks policy and requester mismatch | CI #64 API and action suites passed, including approval tests | Select authoritative production identity provider and run concurrent dispatch/migration acceptance | IMPLEMENTED_NOT_VERIFIED |
| Approval action/evidence/policy binding | Fingerprints persisted with lifecycle fields; executor revalidates action fingerprint and expiry/revocation state | CI #64 focused API/action/persistence modules passed; migration, payload tampering and concurrent dispatch not verified | Test old-database migration, payload tampering, expiry/revocation, concurrent approval and dispatch | INCOMPLETE |
| DEV auto-approval prevention | Profile-based implicit approval removed | CI #64 action/guardrail modules passed | Maintain this behavior in the full workflow | IMPLEMENTED / TESTED |
| Production dispatch boundary | Non-dry-run executor returns before invoking an adapter | CI #64 action suite passed, including fail-closed regression | Durable action claim and verified authorization required before this block can be safely lifted | FAIL_CLOSED / RELEASE BLOCKER |
| Invoice processing regression | Conditional import caused `UnboundLocalError` on the no-approval path; fixed by using the module-level `ApprovalStatus` import | CI #62 exposed stage `case_completion`; CI #64 isolated repro and API suite passed | No remaining known regression gap; other release gates remain independently open | FIXED / TESTED |
| Durable action intent, idempotency, recovery, DLQ | Action ORM/repository and unique idempotency field exist; not wired through a durable dispatch/reconciliation protocol | No restart/concurrency/fault injection evidence | Persist atomic dispatch claims, outcomes, downstream references, retry/DLQ state; reconcile unknown outcome before retry | BLOCKED |
| Benchmark schema and provenance | Historical benchmark artifacts and generated benchmark workflow exist | `reports/evaluation/benchmark_gate.json` requires a fresh run; historical artifact failed | Validate frozen reviewer-labelled corpus, IDs, schema, mapping, provenance, hashes, and missing-label denominators | BLOCKED |
| Benchmark quality and economic model | Historical scoreboard reports multiple poor metrics | No current run; no verified master scoreboard | Analyze error categories; add required metrics/cost separation and run predeclared gates without changing labels/thresholds | BLOCKED |
| Backend, integration, E2E, lint, types, security | CI workflow covers focused repro, API, focused related modules, full suite, benchmark, and scoped Ruff job | CI run `38208777459` at `82112a2`: repro 1 passed; API 61 passed, 1 skipped; related modules 130 passed; full suite 406 passed, 1 skipped; benchmark command and scoped Ruff passed | Run additional configured type/security scans and required E2E checks | PASS (configured CI only) |
| ERP sandbox | Only mock adapters are registered by default | No authorized ERP sandbox or adapter available | Select ERP, provide sandbox access, add idempotent/reconcilable adapter and execute simulator/sandbox fault tests | BLOCKED — external prerequisite |
| Deployment and smoke tests | FastAPI app and health route exist | No deployment target/configuration or authorization | Provide authorized deployment target and credentials, then deploy and run authenticated smoke tests | BLOCKED — external prerequisite |
| Monitoring and alert delivery | In-process instrumentation exists | No external sink, receiver, or delivery proof | Configure provider/receiver and execute alert-to-response test | BLOCKED — external prerequisite |
| Backup and isolated restore | SQLite persistence and generic runbook exist | No backup target or restore evidence | Define RPO/RTO and retention; backup then isolated restore action/idempotency state and verify integrity | BLOCKED — external prerequisite |
| Release audit and tag | Candidate branch pushed; prior commits preserved | CI #64 passed backend and configured checks; other mandatory release gates remain incomplete | Complete every mandatory gate and independent final review; do not merge/tag while any gate is blocked | BLOCKED |

## External prerequisites

- Local execution remains unavailable because Python cannot launch in this Windows environment and WSL returns `E_ACCESSDENIED`; hosted Python 3.11.17 CI is verified.
- ERP product choice, authorized sandbox credentials, and downstream idempotency/reconciliation capabilities.
- Authorized deployment environment and credentials.
- Monitoring provider/receiver and named alert responders.
- Backup destination, retention, RPO/RTO, and isolated restore target.
