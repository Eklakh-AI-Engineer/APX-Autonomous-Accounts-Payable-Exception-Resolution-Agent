# APX Development

## Requirements

The project metadata currently declares:

- Python >= 3.11
- pytest >= 8
- FastAPI
- SQLAlchemy
- Alembic
- Sentence Transformers
- rank-bm25
- NumPy
- scikit-learn
- Pydantic / pydantic-settings
- Uvicorn
- httpx

Development tooling includes Ruff and mypy.

## Setup

Create a virtual environment and install the project according to the repository's preferred Python workflow.

Example:

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate

pip install -e .
```

Install development dependencies when needed:

```bash
pip install -e ".[dev]"
```

## Tests

Full test suite:

```bash
python -m pytest apx/tests -q
```

Useful focused suites from the current project include:

```bash
python -m pytest apx/tests/test_api.py -q
python -m pytest apx/tests/test_persistence.py -q
python -m pytest apx/tests/test_tracing.py -q
```

Use the repository's existing test modules rather than creating parallel test frameworks.

## Linting and typing

Ruff:

```bash
ruff check .
```

mypy:

```bash
mypy apx
```

## Development principles

1. Preserve deterministic financial logic.
2. Keep retrieval, validation, decision, approval, and execution boundaries explicit.
3. Do not bypass guardrails to simplify tests.
4. Do not hard-code credentials.
5. Keep benchmark labels independent from retrieval results.
6. Record limitations rather than manufacturing metrics.
7. Prefer small, reviewable changes.
8. Update active documentation when behavior changes.

## Documentation workflow

New implementation documentation should normally land under `docs/`.

Audits, completed phase reports, diagnostics, and superseded implementation briefs belong under `docs/history/` once they are no longer current guidance.

For repository maintenance, prefer:

```text
maintenance branch
    -> focused commits
    -> pull request
    -> review / verification
    -> merge
```

Do not make unrelated runtime changes in a documentation-maintenance PR.
