# CLAUDE.md

## Commands

```bash
python -m pytest tests/
python -m mypy src/
python -m ruff check src/
```

## Rules

- Use Python 3.12+ features
- Type hints on all public functions
- No print() in production code — use structlog
