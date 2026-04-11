---
title: Agent Memory
zone: memory
created: 2026-04-11
last_updated: 2026-04-11
---

# Agent Memory (30-memory)

Automatically accumulated agent knowledge using the F-F-D framework.

## Write Ownership

**Memory manager only.** Manual edits are prohibited.

## Sub-zones

### facts/
**Factual memory** — Code invariants, API constraints, module responsibilities, architecture decisions.
These are verified truths about the codebase.

### experiences/
**Experiential memory** — Success/failure patterns, debugging lessons, operational knowledge.
These are learned behaviors from past tasks.

## Working Memory

Working memory (current session state, hypotheses, TODOs) lives outside the Vault
at `.claudemate/runtime/`. It is volatile and not tracked by Git.

## Memory Lifecycle

1. **Formation**: Triggered by task close, PR merge, manual promote, wiki update
2. **Evolution**: Merge by canonical_id, confidence tracking, needs_review flagging
3. **Retrieval**: Task-type classification -> relevant module -> wiki+facts -> experiences top-k
