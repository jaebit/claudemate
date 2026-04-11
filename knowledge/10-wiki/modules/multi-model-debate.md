---
title: "multi-model-debate"
zone: wiki
module: "multi-model-debate"
module_path: "plugins/multi-model-debate"
created: "2026-04-11"
last_updated: "2026-04-11"
last_verified_commit: "49d9d1f"
confidence: 1.0
tier: 2
dependencies: ["codex-cli", "gemini-cli"]
dependents: []
exports: ["/multi-model-debate:debate-orchestration", "/multi-model-debate:debate-resume", "/multi-model-debate:debate-start"]
tags: [wiki, module]
---

# multi-model-debate

## Purpose

<!-- LLM-ZONE -->
Orchestrate structured multi-agent debates using Claude, Codex, and Gemini for software engineering decision-making

- **Version**: 1.0.0
- **Path**: `plugins/multi-model-debate`
<!-- /LLM-ZONE -->

## Architecture

<!-- LLM-ZONE -->
- 3 skill(s) providing user-invocable commands
<!-- /LLM-ZONE -->

## Key Components

<!-- LLM-ZONE -->
### Skills
- `debate-orchestration`
- `debate-resume`
- `debate-start`

<!-- /LLM-ZONE -->

## Dependencies

<!-- LLM-ZONE -->
Depends on: [[codex-cli]], [[gemini-cli]]
<!-- /LLM-ZONE -->

## Configuration

<!-- LLM-ZONE -->
- Plugin JSON: `plugins/multi-model-debate/.claude-plugin/plugin.json`
- Module docs: `plugins/multi-model-debate/CLAUDE.md`
<!-- /LLM-ZONE -->

## Notes

<!-- HUMAN-ZONE -->
*Add human notes here. Agents will not modify this section.*
<!-- /HUMAN-ZONE -->
