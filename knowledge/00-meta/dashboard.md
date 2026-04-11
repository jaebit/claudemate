---
title: Vault Dashboard
zone: meta
created: 2026-04-11
last_updated: 2026-04-11
---

# Knowledge Vault Dashboard

> [!note]
> This dashboard requires the **Dataview** Obsidian plugin to render live queries.

## Module Coverage

### Wiki Pages Status

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

### Module Count Summary

```dataview
TABLE length(rows) as "Module Count"
FROM "10-wiki/modules"
WHERE file.name != "README"
```

## Memory Statistics

### Factual Memory Overview

```dataview
TABLE canonical_id, confidence, needs_review, related_modules, last_updated
FROM "30-memory/facts"
SORT last_updated DESC
LIMIT 10
```

### Experiential Memory Overview

```dataview
TABLE canonical_id, outcome, task_type, confidence, last_updated
FROM "30-memory/experiences"
SORT last_updated DESC
LIMIT 10
```

### Memory Statistics Summary

```dataview
TABLE length(rows) as "Count"
FROM "30-memory"
GROUP BY contains(file.path, "facts") ? "Facts" : "Experiences"
```

## Staleness Report

### Low Confidence Pages (< 0.5)

```dataview
TABLE module, confidence, last_verified_commit, last_updated
FROM "10-wiki"
WHERE confidence < 0.5
SORT confidence ASC
```

### Entries Needing Review

```dataview
TABLE canonical_id, memory_type, source_task, confidence, last_updated
FROM "30-memory"
WHERE needs_review = true
SORT last_updated ASC
```

### Outdated Wiki Modules

```dataview
TABLE module, confidence, last_verified_commit, 
  date(now) - date(last_updated) as "Days Since Update"
FROM "10-wiki/modules"
WHERE confidence < 0.7 OR date(now) - date(last_updated) > dur(30 days)
SORT confidence ASC
```

## Recent Activity

### Recently Updated Memory

```dataview
TABLE canonical_id, memory_type, confidence, last_updated
FROM "30-memory"
WHERE last_updated >= date(today) - dur(7 days)
SORT last_updated DESC
LIMIT 15
```

### Recently Modified Wiki Pages

```dataview
TABLE module, confidence, last_updated, 
  date(now) - date(last_updated) as "Age"
FROM "10-wiki"
WHERE last_updated >= date(today) - dur(7 days)
SORT last_updated DESC
```

## MCP Server Status

### Knowledge Tools Health

```dataview
TABLE file.name as "Tool", 
  choice(contains(file.name, "knowledge_mcp"), "✅ MCP Server", 
         contains(file.name, "memory_cli"), "✅ CLI Tool",
         contains(file.name, "integration_test"), "🧪 Test Suite", "❓ Unknown") as "Status",
  file.mtime as "Last Modified"
FROM "00-meta/tools"
WHERE file.extension = "py"
SORT file.name
```

### Tool Integration Status

```dataview
TABLE 
  choice(file(link("00-meta/tools/knowledge_mcp.py")), "✅ Available", "❌ Missing") as "MCP Server",
  choice(file(link("00-meta/tools/memory_cli.py")), "✅ Available", "❌ Missing") as "Memory CLI",
  choice(file(link("00-meta/tools/integration_test.py")), "✅ Available", "❌ Missing") as "Integration Tests",
  choice(file(link("graph.json")), "✅ Available", "❌ Missing") as "Graph Config"
FROM ""
WHERE file.name = "dashboard"
```

## Health Summary

### Zone Statistics

```dataview
TABLE length(rows) as Count
FROM "knowledge"
GROUP BY zone
SORT zone
```

### Overall Vault Health

```dataview
TABLE 
  length(filter(file.fromfolders("10-wiki"), (f) => f.confidence >= 0.8)) as "High Confidence Wiki",
  length(filter(file.fromfolders("10-wiki"), (f) => f.confidence < 0.5)) as "Low Confidence Wiki",
  length(filter(file.fromfolders("30-memory"), (f) => f.needs_review = true)) as "Needs Review",
  length(file.fromfolders("30-memory/facts")) as "Total Facts",
  length(file.fromfolders("30-memory/experiences")) as "Total Experiences"
FROM ""
WHERE file.name = "dashboard"
```