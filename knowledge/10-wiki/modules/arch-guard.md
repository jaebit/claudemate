---
title: "arch-guard"
zone: wiki
module: "arch-guard"
module_path: "plugins/arch-guard"
created: "2026-04-11"
last_updated: "2026-04-11"
last_verified_commit: "49d9d1f"
confidence: 1.0
tier: 2
dependencies: []
dependents: []
exports: ["/arch-guard:adr", "/arch-guard:arch-check", "/arch-guard:contract-first", "/arch-guard:impl-review", "/arch-guard:implement"]
tags: [wiki, module]
---

# arch-guard

## Purpose

<!-- LLM-ZONE -->
Architecture compliance enforcement for layered projects — config-driven layer boundary checks, contract-first development, and design decision records

- **Version**: 0.2.2
- **Path**: `plugins/arch-guard`
<!-- /LLM-ZONE -->

## Architecture

<!-- LLM-ZONE -->
- 1 agent(s) for task execution
- 12 skill(s) providing user-invocable commands
- Hook-based event automation
<!-- /LLM-ZONE -->

## Key Components

<!-- LLM-ZONE -->
### Skills
- `adr`
- `arch-check`
- `contract-first`
- `impl-review`
- `implement`
- `integration-map`
- `scaffold`
- `setup`
- `spec-sync`
- `tdd`
- `test-gen`
- `track`

### Agents
- `arch-reviewer`

### Hooks
- Hook definitions in `hooks/` directory

### Shared Resources
- Shared protocols and schemas in `_shared/` directory

<!-- /LLM-ZONE -->

## Dependencies

<!-- LLM-ZONE -->
No inter-plugin dependencies detected.
<!-- /LLM-ZONE -->

## Configuration

<!-- LLM-ZONE -->
- Plugin JSON: `plugins/arch-guard/.claude-plugin/plugin.json`

<!-- /LLM-ZONE -->

## Notes

<!-- HUMAN-ZONE -->
*Add human notes here. Agents will not modify this section.*
<!-- /HUMAN-ZONE -->
