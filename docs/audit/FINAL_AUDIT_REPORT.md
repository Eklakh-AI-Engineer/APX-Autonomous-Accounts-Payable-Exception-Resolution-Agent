# Final audit report — release blocked

Audit date: 2026-10-12. Branch: `codex/v1-release-audit`. Base commit: `0b6f30ed3a45db3f277cfe4179758d90a8aa593b`.

## Decision

**IMPLEMENTATION_INCOMPLETE / RELEASE_BLOCKED.** This work removes implicit DEV-profile auto-approval, binds approval API actor identity to configured approver API keys, and enforces configured approver eligibility. P0 approval binding and execution-authorization risks remain, and the required runtime, ERP, deployment, monitoring, and restore evidence is not established. No `v1.0.0` tag was created.

## Evidence

- Source review found caller-supplied `approver_id` was used by the API; the route now ignores it and derives the subject from a configured approver API key. `ApprovalService` now checks required approvers and rejects a match with recorded `requested_by`.
- Approval creation still records `system` as requester, approval is not bound to action parameters/evidence/policy, and executor dispatch does not verify a durable approval. These remain P0 gaps.
- The DEV-profile implicit auto-approval path was removed; its regression test was updated. Runtime verification remains blocked.
- Executor defaults to mock adapters, and its dead-letter queue is process-local.
- The latest committed benchmark artifact is dated 2026-08-19 and reports `passed: false`: extraction F1 1.00 (synthetic structured-input measure), detection F1 0.2659, retrieval Recall@5 0.60, evidence-validity rate 0.03, business decision accuracy 0.274, automation 0.024, unauthorized rate 0.00 in that simulated run. This is historical artifact evidence, not a fresh evaluation.
- Test command attempted: `python -m pytest apx/tests -q`. Result: unable to start the WSL-created `.venv` interpreter in Windows (`Access is denied`); desktop-bundled Python has no pytest installed. No tests are claimed as passing in this audit.
- The repository workflow defines tests and a DEV benchmark, but no run result is available in the local evidence.
- No ERP sandbox, deployment endpoint, alert receiver, or backup/restore target/evidence exists in the inspected checkout.

## Source state

Starting user checkout: `172598db54c47c31a0c84dfa1793ae052823693d`, clean on `main`, behind remote main by 32 commits. Work was based on the existing local `origin/main` commit `0b6f30ed3a45db3f277cfe4179758d90a8aa593b` on branch `codex/v1-release-audit`. No commit was made; worktree contains audit deliverables. No remote changes, deployments, financial actions, or tags were made.

The gap matrix is the authoritative status register. A source-level observation or historical artifact is not treated as runtime verification. Resolve every P0 item and blocked dependency, run supported CI and operational exercises, then request a fresh independent audit before release.
