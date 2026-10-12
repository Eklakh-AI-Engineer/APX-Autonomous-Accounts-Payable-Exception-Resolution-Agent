# Incident response

Initial response outline; alert routing and a live exercise have not been verified.

## Financial action or approval incident

1. Disable external action dispatch and revoke affected credentials/tokens.
2. Preserve audit logs, approval records, action ledger, request/correlation IDs and ERP transaction identifiers.
3. Identify affected invoices, approvers, action payloads, timestamps, idempotency keys and uncertain outcomes.
4. Reconcile every possible external effect with the ERP before retrying, compensating, or marking complete.
5. Escalate to designated finance, security and incident owners; follow notification policy.
6. Restore only from verified backups; re-enable dispatch after authorization controls and reconciliation are checked.
7. Record timeline, scope, root cause, corrective actions and evidence retention.

Before release, name on-call roles, contact paths, severity criteria, retention period, and test an alert-to-response exercise.
