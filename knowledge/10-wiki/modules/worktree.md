---
title: "worktree"
zone: wiki
module: "worktree"
module_path: "plugins/worktree"
created: "2026-04-11"
last_updated: "2026-04-11"
last_verified_commit: "49d9d1f"
confidence: 1.0
tier: 2
dependencies: []
dependents: []
exports: ["/worktree:cleanup", "/worktree:create", "/worktree:merge"]
tags: [wiki, module]
---

# worktree

## Purpose

<!-- LLM-ZONE -->
Git worktree lifecycle management — create, merge, cleanup

- **Version**: 0.1.0
- **Path**: `plugins/worktree`
<!-- /LLM-ZONE -->

## Architecture

<!-- LLM-ZONE -->
- 3 skill(s) providing user-invocable commands
<!-- /LLM-ZONE -->

## Key Components

<!-- LLM-ZONE -->
### Skills
- `cleanup`
- `create`
- `merge`

<!-- /LLM-ZONE -->

## Dependencies

<!-- LLM-ZONE -->
No inter-plugin dependencies detected.
<!-- /LLM-ZONE -->

## Configuration

<!-- LLM-ZONE -->
- Plugin JSON: `plugins/worktree/.claude-plugin/plugin.json`
- Module docs: `plugins/worktree/CLAUDE.md`
<!-- /LLM-ZONE -->

## Notes

<!-- HUMAN-ZONE -->
*Add human notes here. Agents will not modify this section.*
<!-- /HUMAN-ZONE -->
