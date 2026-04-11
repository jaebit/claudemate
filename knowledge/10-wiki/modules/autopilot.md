---
title: "autopilot"
zone: wiki
module: "autopilot"
module_path: "plugins/autopilot"
created: "2026-04-11"
last_updated: "2026-04-11"
last_verified_commit: "49d9d1f"
confidence: 1.0
tier: 2
dependencies: ["codex-cli", "crew", "multi-model-debate", "arch-guard"]
dependents: []
exports: ["/autopilot:autopilot"]
tags: [wiki, module]
---

# autopilot

## Purpose

<!-- LLM-ZONE -->
End-to-end autonomous coding pipeline — orchestrates cw, multi-model-debate, codex CLI, and arch-guard into a single /autopilot command

- **Version**: 0.4.0
- **Path**: `plugins/autopilot`
<!-- /LLM-ZONE -->

## Architecture

<!-- LLM-ZONE -->
- 1 skill(s) providing user-invocable commands
- Hook-based event automation
<!-- /LLM-ZONE -->

## Key Components

<!-- LLM-ZONE -->
### Skills
- `autopilot`

### Hooks
- Hook definitions in `hooks/` directory

### Shared Resources
- Shared protocols and schemas in `_shared/` directory

<!-- /LLM-ZONE -->

## Dependencies

<!-- LLM-ZONE -->
Depends on: [[codex-cli]], [[crew]], [[multi-model-debate]], [[arch-guard]]
<!-- /LLM-ZONE -->

## Configuration

<!-- LLM-ZONE -->
- Plugin JSON: `plugins/autopilot/.claude-plugin/plugin.json`
- Module docs: `plugins/autopilot/CLAUDE.md`
<!-- /LLM-ZONE -->

## Notes

<!-- HUMAN-ZONE -->
*Add human notes here. Agents will not modify this section.*
<!-- /HUMAN-ZONE -->
