# APX threat model (initial)

## Assets

Invoice and vendor data; approval identity and intent; action parameters; ERP state; credentials; evidence and evaluation labels; audit history.

## Trust boundaries

1. Submitted invoice/API client to FastAPI.
2. Authentication and role middleware to application services.
3. Decision and retrieval components to approval policy.
4. Approval service to guarded executor.
5. Executor to external ERP/action target.
6. Persistent database, logs, traces and evaluation artifacts.

## High-priority threats observed

| Threat | Current observation | Required mitigation |
|---|---|---|
| Caller forges approver identity | Approval body supplies `approver_id`; auth currently records roles, not human subjects | Derive subject from trusted authentication; verify eligibility and requester separation |
| Pending action implicitly approved | Pipeline uses `DEV` retrieval profile to set approval status | Remove implicit approval and reauthorize at executor dispatch |
| Action changed after approval | Approval model shown does not bind canonical action parameters/evidence digest | Persist and verify cryptographic/canonical action binding |
| Duplicate external effect after timeout | No external ERP idempotency/reconciliation contract established | Durable outbox/ledger and target reconciliation before retry |
| Dead-letter loss | Executor queue is in-memory | Persist, audit and control replay |
| Evidence leakage or wrong scope | Historical evidence validity 3%, vendor scope 9% | Strict evidence applicability/validity tests and frozen evaluation |
| Credential exposure / weak perimeter | Deployment not configured or audited | Secret manager, TLS ingress, distributed throttling, least privilege, log review |

## Assumptions and status

This is a source-level initial threat model, not a penetration test or deployment certification. CI/runtime verification, provider configuration, external attack surface, retention, incident response, and ERP permissions remain unverified. Release stays blocked until P0 mitigations are implemented and tested.
