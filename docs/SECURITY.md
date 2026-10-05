# APX Security

## Security boundary

APX separates business decisioning from authorization and execution. A generated recommendation does not automatically authorize a financial action.

## Recorded controls

Phase 6D documentation records the following controls:

- API-key authentication;
- RBAC preservation;
- in-process token-bucket rate limiting;
- configurable request-rate limits;
- `429 Too Many Requests` responses with `Retry-After`;
- request-size enforcement;
- `413 Request Entity Too Large` handling;
- security response headers;
- CSP configuration compatible with development Swagger UI;
- conditional HSTS for HTTPS;
- request/correlation identifiers;
- W3C trace-context propagation at the API boundary;
- centralized recursive sensitive-data redaction;
- redaction of audit payloads and metadata before persistence;
- structured request lifecycle logging.

## Scope limitations

These controls have explicit boundaries.

### Rate limiting

The recorded implementation is **in-process**. It should not be described as a distributed rate limiter.

### Tracing

W3C trace context is supported at the API boundary. This is not equivalent to a complete distributed tracing deployment.

### TLS / HSTS

The application can emit HSTS when operating over HTTPS, but it does not provide TLS termination itself.

### Secrets

Credentials and API keys must remain external configuration. They must never be committed to the repository or emitted into logs/traces.

## Evaluation and action safety

Security review must include the action boundary. The guardrail remains the authorization boundary for execution.

Tests should verify that:

- unauthorized actions remain blocked;
- approval requirements are enforced;
- sensitive fields are redacted;
- authentication/RBAC behavior is preserved;
- request limits behave as expected.

Security documentation describes implemented controls and scope; it does not constitute a production security certification.
