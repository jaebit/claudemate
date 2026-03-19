# Module Context

**Module:** docs-optimizer
**Version:** 1.0.0
**Role:** Research-backed CLAUDE.md/AGENTS.md optimization (arxiv 2602.11988v1).

# Skills

- `/docs-optimizer:optimize [path] [--dry-run] [--report-only]` — Optimize target files (`disable-model-invocation`: user-only, `context: fork`)

# Constraints

- **DO** preserve test/build commands and repo-specific constraints.
- **DO** verify pointer targets exist before creating references.
- **DO** show before/after line counts for every optimization.
- **DON'T** delete content without identifying its source of truth.
- **DON'T** modify files outside the target scope without confirmation.
- **DON'T** remove sections classified as HIGH-VALUE.
