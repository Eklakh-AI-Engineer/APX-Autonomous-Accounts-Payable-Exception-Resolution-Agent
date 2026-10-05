# APX Documentation

This directory contains the **current, maintained documentation** for APX.

## Start here

| Document | Purpose |
|---|---|
| [Architecture](ARCHITECTURE.md) | Current system boundaries and decision pipeline |
| [Evaluation](EVALUATION.md) | Evaluation layers, retrieval metrics, reproducibility, and benchmark boundaries |
| [Development](DEVELOPMENT.md) | Local setup, tests, linting, and contribution workflow |
| [Security](SECURITY.md) | Authentication, RBAC, rate limiting, redaction, tracing, and security scope |
| [API](API.md) | FastAPI delivery boundary and endpoint conventions |
| [History](history/README.md) | Archived audits, phase reports, build briefs, and diagnostics |

## Documentation policy

Active documentation describes the **current repository state** and should not be used as a historical changelog.

Historical implementation evidence is retained under `docs/history/` so that prior decisions, audits, benchmark findings, and phase reports remain reviewable without competing with current guidance.

### Status language

APX documentation distinguishes:

- **Implemented** — present in the repository and described as current behavior.
- **Recorded verification** — backed by an existing phase report or test record.
- **Target / planned** — an engineering objective that is not presented as an achieved result.
- **Historical** — preserved for traceability but not treated as current guidance.

No benchmark, production-readiness, or performance claim should be inferred from architecture documentation alone.
