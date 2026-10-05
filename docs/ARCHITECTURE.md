# APX Architecture

## 1. System purpose

APX is a controlled Accounts Payable exception-resolution system. Its architecture separates:

1. deterministic financial validation;
2. evidence retrieval and validation;
3. bounded investigation and decision logic;
4. risk and approval policy;
5. guarded action execution;
6. durable persistence;
7. API delivery;
8. observability and evaluation.

The central boundary is:

> A model-generated decision is not itself an authorization to perform an irreversible business action.

## 2. Current pipeline

```text
AP Exception / Invoice
        |
        v
Deterministic Validation (R1-R10)
        |
        v
Evidence Retrieval
  BM25 + Dense
        |
        v
Hybrid / RRF Fusion
        |
        v
Cross-Encoder Reranking
        |
        v
Evidence Validity + Temporal Anchoring
        |
        v
Bounded Agent Investigation
        |
        v
Risk / Decision Policy
        |
   +----+----+
   |         |
   v         v
Approval   Escalation
   |
   v
Guarded Action
   |
   v
Persistence
   |
   v
FastAPI Delivery
   |
   v
Observability + Evaluation
```

## 3. Layer boundaries

### Domain and deterministic validation

The domain layer defines the AP exception taxonomy and deterministic financial checks. Monetary values use structured models and Decimal-oriented handling rather than relying on generative output.

The R1-R10 taxonomy includes vendor, PO, amount, GRN, duplicate, tax, currency, line-item, discount, and credit-related exceptions.

### Evidence and retrieval

The retrieval stack is intentionally multi-stage:

- BM25 / sparse retrieval
- dense semantic retrieval
- hybrid fusion
- reciprocal-rank fusion
- cross-encoder reranking
- evidence validity checks
- temporal anchoring

Retrieval should produce evidence candidates; it does not directly authorize actions.

### Agent and decision control

The investigation layer consumes structured validation and evidence outputs. Decision and risk logic remain explicit so that an LLM is not treated as the financial source of truth.

### Approval and guardrails

Approval is a control boundary. Guardrails enforce authorization and execution constraints before actions are performed.

### Persistence and application services

Persistence provides durable state for cases, invoices, approvals, actions, and audit information. Application services orchestrate domain behavior without making the FastAPI layer the business-logic layer.

### API and observability

FastAPI is the delivery boundary. Authentication, RBAC, request correlation, structured logging, metrics, tracing context, redaction, and security headers are handled at the application/API boundary.

## 4. Production-readiness boundary

Phase 6D hardening is **not equivalent to production readiness**.

Recorded implementation includes API security and observability controls, but APX documentation must not imply:

- distributed rate limiting;
- complete distributed tracing infrastructure;
- TLS termination by the application;
- a production ERP integration;
- production financial authorization;
- operational readiness without deployment-specific controls.

See [Security](SECURITY.md) and [Evaluation](EVALUATION.md) for the explicit scope.
