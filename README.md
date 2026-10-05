# APX — Autonomous Accounts Payable Exception Resolution Agent

> **A controlled, evidence-grounded system for Accounts Payable exception resolution.**

APX is an engineering/research system that separates deterministic financial validation, evidence retrieval, bounded investigation, risk and approval policy, guarded action execution, persistence, API delivery, observability, and evaluation.

The core principle is simple:

> **A model decision is useful only when the system can constrain it, explain it, persist it, observe it, and evaluate it.**

---

## Current status

**Latest recorded milestone: Phase 6D — Observability & Security.**

| Area | Status |
|---|---|
| Deterministic AP validation | Complete |
| Evidence / retrieval foundation | Complete |
| Bounded agent + decision flow | Complete |
| Risk, approval, guardrails, actions | Complete |
| Evaluation / observability foundation | Complete / frozen |
| SQLite persistence | Complete |
| Application services / FastAPI delivery | Complete |
| Case + approval lifecycle | Complete |
| API observability + security hardening | Complete |
| Production readiness | **Not claimed** |

Phase completion describes the repository's engineering milestone; it is not a production deployment certification.

---

## Architecture

```text
AP Exception / Invoice
        |
        v
Deterministic Validation (R1-R10)
        |
        v
Evidence Retrieval
  BM25 + Dense + Hybrid
        |
        v
RRF + Cross-Encoder Reranking
        |
        v
Evidence Validity + Temporal Anchoring
        |
        v
Bounded Investigation / Decision
        |
        v
Risk + Approval Policy
        |
   +----+----+
   |         |
   v         v
Auto      Human / Escalate
Resolve      |
   |         |
   +----+----+
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

The important architectural boundary is:

```text
Decision != Authorization != Execution
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the maintained architecture reference.

---

## Retrieval engineering

APX uses a multi-stage evidence pipeline:

- **BM25** for lexical / identifier-sensitive retrieval
- **Dense retrieval** for semantic matching
- **Hybrid fusion**
- **Reciprocal Rank Fusion (RRF)**
- **Cross-encoder reranking**
- **Evidence validity checks**
- **Temporal anchoring**

The evaluation layer measures retrieval independently using explicit relevance judgments. Historical retrieval and ground-truth audits are preserved under [docs/history/](docs/history/).

---

## Deterministic exception taxonomy

The current system models ten AP exception classes:

```text
R1  VENDOR_MISMATCH
R2  PO_MISMATCH
R3  AMOUNT_MISMATCH
R4  GRN_MISMATCH
R5  DUPLICATE_INVOICE
R6  TAX_ERROR
R7  CURRENCY_MISMATCH
R8  LINE_ITEM_MISMATCH
R9  DISCOUNT_ERROR
R10 CREDIT_ISSUE
```

Financial validation is explicit and reproducible rather than delegated to generative text.

---

## Verification

The latest Phase 6D report records:

- focused observability/security verification;
- tracing, persistence, validator, evidence, risk, guardrail, and action regression coverage;
- API verification;
- **180 passed, 0 failed, 0 skipped** in the report's regression accounting;
- API suite separately recorded as **60 passed, 1 expected skip**.

These are **recorded historical verification results**, not a claim that the current environment has just executed the suite.

Run the current suite locally before treating them as fresh results:

```bash
python -m pytest apx/tests -q
```

---

## Repository structure

```text
APX/
├── README.md
├── apx/
│   ├── agent/
│   ├── api/
│   ├── application/
│   ├── approval/
│   ├── data/
│   ├── evidence/
│   ├── evaluation/
│   ├── exceptions/
│   ├── guardrail/
│   ├── intelligence/
│   ├── observability/
│   ├── persistence/
│   ├── risk/
│   └── tests/
├── docs/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── EVALUATION.md
│   ├── DEVELOPMENT.md
│   ├── SECURITY.md
│   ├── API.md
│   └── history/
├── pyproject.toml
└── evaluation / diagnostic artifacts
```

---

## Documentation

| Document | Purpose |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Current system boundaries and pipeline |
| [Evaluation](docs/EVALUATION.md) | Metrics, ground truth, reproducibility |
| [Development](docs/DEVELOPMENT.md) | Setup, testing, linting, contribution workflow |
| [Security](docs/SECURITY.md) | Security controls and explicit scope boundaries |
| [API](docs/API.md) | FastAPI delivery boundary |
| [History](docs/history/README.md) | Archived audits and phase evidence |

---

## Development

Project metadata declares **Python >= 3.11**.

Install locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
python -m pytest apx/tests -q
```

Lint:

```bash
ruff check .
```

Type-check:

```bash
mypy apx
```

---

## Engineering principles

1. **Deterministic financial truth** — financial validation remains explicit.
2. **Evidence before reasoning** — retrieved evidence is a first-class artifact.
3. **Risk-aware autonomy** — autonomous resolution is bounded by policy.
4. **Human approval as a control boundary** — approval is architectural.
5. **Guarded execution** — authorization and execution remain separate.
6. **Persistent state** — cases, actions, and audit information are durable.
7. **Observable execution** — API and system events are traceable.
8. **Reproducible evaluation** — benchmark inputs and semantics are versioned.
9. **Honest measurement** — targets are not presented as achieved results.

---

## Scope boundary

APX should not be represented as a production financial system merely because its Phase 6D milestone is complete.

The repository does **not** claim:

- production ERP integration;
- distributed rate limiting;
- complete distributed tracing deployment;
- application-managed TLS termination;
- production authorization approval;
- regulatory/security certification;
- production readiness without deployment-specific controls.

---

## License / attribution

See the repository's existing project metadata and source files for licensing and attribution information.
