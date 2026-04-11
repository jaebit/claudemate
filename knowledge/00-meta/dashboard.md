---
title: Vault Dashboard
zone: meta
created: 2026-04-11
last_updated: 2026-04-11
---

# Knowledge Vault Dashboard

> [!note]
> This dashboard requires the **Dataview** Obsidian plugin to render live queries.

## Wiki Pages

### Module Coverage

```dataview
TABLE module, confidence, last_verified_commit, last_updated
FROM "10-wiki/modules"
SORT confidence ASC
```

### Cross-Cutting Topics

```dataview
TABLE topic, confidence, last_updated
FROM "10-wiki/cross-cutting"
SORT last_updated DESC
```

### Stale Pages (confidence < 0.5)

```dataview
TABLE module, confidence, last_verified_commit
FROM "10-wiki"
WHERE confidence < 0.5
SORT confidence ASC
```

## Memory Entries

### Factual Memory

```dataview
TABLE canonical_id, confidence, needs_review, related_modules
FROM "30-memory/facts"
SORT last_updated DESC
```

### Experiential Memory

```dataview
TABLE canonical_id, outcome, task_type, confidence
FROM "30-memory/experiences"
SORT last_updated DESC
```

### Entries Needing Review

```dataview
TABLE canonical_id, memory_type, source_task
FROM "30-memory"
WHERE needs_review = true
SORT last_updated ASC
```

## Health Summary

```dataview
TABLE length(rows) as Count
FROM "knowledge"
GROUP BY zone
```
