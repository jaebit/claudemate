---
title: Frontmatter Schema Definitions
zone: meta
created: 2026-04-11
last_updated: 2026-04-11
---

# Frontmatter Schema Definitions

## Base Schema (all files)

```yaml
title: string          # Required. Human-readable page title
zone: enum             # Required. One of: meta, wiki, notes, memory
created: date          # Required. ISO date (YYYY-MM-DD)
last_updated: date     # Required. ISO date of last modification
tags: list[string]     # Optional. Obsidian tags for filtering
aliases: list[string]  # Optional. Alternative names for Obsidian linking
```

## Wiki Module Page (`10-wiki/modules/`)

```yaml
title: string
zone: wiki
module: string                  # Module/package directory name
module_path: string             # Relative path from repo root
created: date
last_updated: date
last_verified_commit: string    # Short SHA of last verification
confidence: float               # 0.0-1.0 freshness confidence
tier: integer                   # 2 = module, 3 = cross-cutting
dependencies: list[string]      # Other module names this depends on
dependents: list[string]        # Modules that depend on this
exports: list[string]           # Key public symbols/APIs
tags: list[string]
```

## Wiki Cross-Cutting Page (`10-wiki/cross-cutting/`)

```yaml
title: string
zone: wiki
topic: string                   # ADR ID or pattern name
created: date
last_updated: date
last_verified_commit: string
confidence: float
tier: 3
related_modules: list[string]   # Modules involved
tags: list[string]
```

## Memory Factual Entry (`30-memory/facts/`)

```yaml
title: string
zone: memory
memory_type: factual
canonical_id: string            # Stable unique ID (e.g., "fact-crew-dispatch-invariant")
confidence: float               # 0.0-1.0
source_task: string             # Task/session that produced this
source_commit: string           # Commit SHA where fact was verified
related_modules: list[string]   # Modules this fact applies to
created: date
last_updated: date
needs_review: boolean           # True if source path mismatch detected
tags: list[string]
```

## Memory Experiential Entry (`30-memory/experiences/`)

```yaml
title: string
zone: memory
memory_type: experiential
canonical_id: string            # Stable unique ID (e.g., "exp-crew-test-flaky-fix")
confidence: float               # 0.0-1.0
source_task: string             # Task/session that produced this
outcome: enum                   # success | failure | partial
task_type: enum                 # explore | locate | edit | validate
related_modules: list[string]
created: date
last_updated: date
tags: list[string]
```

## Working Memory (`.claudemate/runtime/` — not in Vault)

Working memory uses JSON/JSONL format, not Markdown.
It is volatile and not tracked by Git.

```json
{
  "session_id": "string",
  "hypotheses": [],
  "active_todos": [],
  "context_snapshot": {},
  "created_at": "ISO-datetime",
  "expires_at": "ISO-datetime"
}
```

## Staleness Metadata

The `last_verified_commit` + `confidence` pair forms the staleness system:

- **confidence >= 0.8**: Fresh — safe to use without re-verification
- **confidence 0.5-0.79**: Aging — usable but should be re-verified soon
- **confidence < 0.5**: Stale — must re-verify before relying on content
- **needs_review: true**: Source path mismatch detected — manual review required

Confidence decays when:
1. Source files change without wiki/memory update
2. Time passes without re-verification
3. Dependent modules are updated
