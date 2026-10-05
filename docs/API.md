# APX API

## Delivery boundary

APX exposes its application through FastAPI. The API layer is a delivery boundary over application services; domain validation and decision logic should not be duplicated inside route handlers.

The repository's current API surface includes route families for:

- health / service status;
- invoices;
- exception cases;
- approvals;
- audit events;
- metrics / observability;
- authenticated and role-aware operations.

Consult the implementation under `apx/api/` for the authoritative route definitions.

## Cross-cutting behavior

The API boundary includes the recorded Phase 6D controls:

- API-key authentication;
- RBAC;
- request IDs;
- correlation IDs;
- W3C trace context propagation;
- request-rate limiting;
- request-size enforcement;
- security headers;
- structured request lifecycle logging;
- sensitive-data redaction.

## Request safety

Clients should treat the API as a controlled application boundary. A successful decision response does not imply that an action can bypass approval or guardrail checks.

## Local verification

Run the API-focused tests with:

```bash
python -m pytest apx/tests/test_api.py -q
```

For a running local development service, use the repository's FastAPI/Uvicorn entry point under `apx/api/` rather than introducing a second server path.

## API documentation policy

Do not copy route definitions into this document when that would create a second source of truth. Keep endpoint behavior in the implementation and use this page to describe architectural/API boundaries.
