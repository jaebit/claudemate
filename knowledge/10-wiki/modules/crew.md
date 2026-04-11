---
title: "crew"
zone: wiki
module: "crew"
module_path: "plugins/crew"
created: "2026-04-11"
last_updated: "2026-04-11"
last_verified_commit: "49d9d1f"
confidence: 1.0
tier: 2
dependencies: ["worktree"]
dependents: []
exports: ["/crew:commit-discipline", "/crew:dashboard", "/crew:explore", "/crew:go", "/crew:insight-collector"]
tags: [wiki, module]
---

# crew

## Purpose

<!-- LLM-ZONE -->
Agent-orchestrated development pipeline — 9-stage automation with 8 adaptive agents, parallel execution, research, and review

- **Version**: 4.1.1
- **Path**: `plugins/crew`
<!-- /LLM-ZONE -->

## Architecture

<!-- LLM-ZONE -->
- 8 agent(s) for task execution
- 16 skill(s) providing user-invocable commands
- Hook-based event automation
- Test suite in `tests/` directory
<!-- /LLM-ZONE -->

## Key Components

<!-- LLM-ZONE -->
### Skills
- `commit-discipline`
- `dashboard`
- `explore`
- `go`
- `insight-collector`
- `knowledge-engine`
- `learning-loop`
- `manage`
- `parallel`
- `pattern-learner`
- `plan-detector`
- `progress-tracker`
- `quality-gate`
- `review`
- `session-manager`
- `structured-research`

### Agents
- `analyst`
- `architect`
- `bootstrapper`
- `builder`
- `compliance-checker`
- `fixer`
- `planner`
- `reviewer`

### Hooks
- Hook definitions in `hooks/` directory

### Shared Resources
- Shared protocols and schemas in `_shared/` directory

<!-- /LLM-ZONE -->

## Dependencies

<!-- LLM-ZONE -->
Depends on: [[worktree]]
<!-- /LLM-ZONE -->

## Configuration

<!-- LLM-ZONE -->
- Plugin JSON: `plugins/crew/.claude-plugin/plugin.json`
- Module docs: `plugins/crew/CLAUDE.md`
<!-- /LLM-ZONE -->

## Notes

<!-- HUMAN-ZONE -->
*Add human notes here. Agents will not modify this section.*
<!-- /HUMAN-ZONE -->
