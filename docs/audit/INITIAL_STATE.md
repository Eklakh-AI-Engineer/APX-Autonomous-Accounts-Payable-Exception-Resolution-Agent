# Initial repository state

Audit date: 2026-10-12 (Asia/Calcutta)

## Source snapshot

- Starting checkout: `main`, commit `172598db54c47c31a0c84dfa1793ae052823693d`.
- Starting worktree: clean; `main` was 32 commits behind its configured `origin/main` and had no uncommitted changes.
- Configured remote: `origin` points to the APX GitHub repository.
- Available local `origin/main`: `0b6f30ed3a45db3f277cfe4179758d90a8aa593b`.
- Implementation work was moved onto `codex/v1-release-audit` at that existing remote-tracking commit. No pull, remote write, commit, or tag was performed.
- Current worktree baseline is the newer commit above; it includes reliability changes, security redaction tests, and `.github/workflows/apx-ci.yml` that were absent from the starting checkout.

## Architecture and project claims inspected

Inspected `README.md`, `pyproject.toml`, `docs/{ARCHITECTURE,API,DEVELOPMENT,EVALUATION,SECURITY}.md`, the CI workflow, phase history, approval API/service/repositories, action pipeline/executor, risk/guardrail code, persistence models and migration, data/evaluation implementation, benchmark artifacts, and the test tree.

The repository retains deterministic R1–R10 validation, hybrid BM25/dense/RRF/reranking, evidence validity checks, bounded investigation, risk/guardrail logic, FastAPI, SQLite repositories, and six-layer evaluation. These features are not equivalent to a production ERP execution system.

## Baseline execution

Attempted `python -m pytest apx/tests -q` using the checked-in `.venv` and the bundled desktop Python runtime. The repository `.venv` was generated under `/mnt/d/Opencode` with Python 3.14 and contains a Unix-layout interpreter unavailable to Windows PowerShell; WSL launch returned `E_ACCESSDENIED`. The bundled Windows Python starts but reports `No module named pytest`. Thus test execution is **blocked by the local runtime**, not reported as passing or failing. No dependency installation was attempted.

No current benchmark was run for the same reason. The latest committed artifact (`apx/evaluation/results/benchmark_dev_20260819_171101.json`) is historical and explicitly has `passed: false`; it records 500 cases, seed 42, reference date 2026-08-29, detection F1 0.265931, retrieval Recall@5 0.60, evidence validity rate 0.03, and business automation rate 0.024. It is not a fresh baseline result.

## Critical observations

1. `/cases/{case_id}/approve` and `/reject` receive a caller-supplied `approver_id`; API authentication associates keys with roles, not a verified human subject. `ApprovalService` records the supplied value and marks the approval resolved without enforcing `required_approvers` or separation of duties. A role check alone does not bind the recorded approver to an authenticated person.
2. `Phase4Pipeline.process` changes a pending approval to approved when the active retrieval profile is `DEV`. A profile selector is not a safe authorization boundary; this behavior can be reached by `run_full_pipeline`, which executes approved actions.
3. The default executor uses mock adapters and an in-memory dead-letter list. Persistent SQL models exist for cases, approvals, and actions, but inspection did not find durable dead-letter storage or an uncertain-outcome reconciliation workflow.
4. The last saved benchmark fails its own recorded gates and has weak detection, retrieval, evidence validity, decision quality, and automation measures.
5. This checkout has no ERP provider credentials, deployment target, monitoring/alert sink, backup target, or restore evidence configured in the repository.

See [IMPLEMENTATION_GAP_MATRIX.md](IMPLEMENTATION_GAP_MATRIX.md) for acceptance criteria and status.
