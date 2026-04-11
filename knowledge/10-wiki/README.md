---
title: Code Wiki
zone: wiki
created: 2026-04-11
last_updated: 2026-04-11
---

# Code Wiki (10-wiki)

Module-centric code knowledge base. Each module/package gets a Tier 2 page.
Cross-cutting concerns (ADRs, architecture patterns) get Tier 3 pages.

## Write Ownership

**Wiki CLI only.** Do not edit these files manually.
Use `wiki init` or `wiki update` commands.

## Structure

- `modules/` — One page per module/package
- `cross-cutting/` — Architecture decisions, workflows, patterns
- `graph.json` — Machine-readable dependency graph and symbol index
