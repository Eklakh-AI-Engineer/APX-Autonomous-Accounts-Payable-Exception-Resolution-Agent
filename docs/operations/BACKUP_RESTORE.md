# Backup and restore

No backup target, retention schedule, RPO, RTO, or restore exercise is configured or evidenced in this repository. Recovery is a release blocker.

## Required procedure before production

- Select a durable backup target; document encryption, access, retention, immutability and deletion controls.
- Define business-approved RPO/RTO and backup cadence.
- Capture a consistent snapshot, migration version, application commit and non-secret configuration references.
- Restore into an isolated environment; verify schema migrations and integrity.
- Verify invoice, case, approval, action, idempotency and audit relationships; reconcile unresolved external outcomes.
- Record artifact identifier, timestamps, operator, checks, duration and discrepancies.

Do not claim recoverability until a restore has passed and evidence is retained.
