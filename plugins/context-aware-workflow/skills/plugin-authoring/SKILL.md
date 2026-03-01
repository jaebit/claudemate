---
name: plugin-authoring
description: Agent and skill authoring patterns for this plugin. Use when creating or modifying agents/*.md or skills/*/SKILL.md files.
allowed-tools: Read, Write, Glob, Grep
context: fork
---

# Plugin Authoring Patterns

## Agent Definition (agents/*.md)

```yaml
---
name: agent-name                 # REQUIRED: lowercase-with-hyphens only
description: "What the agent does"  # REQUIRED: guides delegation decisions
model: sonnet                    # haiku | sonnet | opus | inherit
tools:                           # Optional: tools available to the agent
  - Read
  - Write
  - Glob
mcp_servers:                     # Optional: MCP servers (omit for haiku tier)
  - serena
skills: skill1, skill2           # Optional: preloaded at startup
tier: sonnet                     # Extension: complexity tier indicator
whenToUse: |                     # Extension: usage guidance
  When to use this agent...
color: blue                      # Extension: UI display color
isolation: worktree              # Official: automatic worktree isolation
---
# Agent system prompt here
```

### Official vs Extension Fields

| Field | Official | Required | Notes |
|-------|:--------:|:--------:|-------|
| `name` | Yes | **Yes** | lowercase-with-hyphens only |
| `description` | Yes | **Yes** | Guides delegation decisions |
| `model` | Yes | No | sonnet/opus/haiku/inherit |
| `tools` | Yes | No | Inherits all if omitted |
| `skills` | Yes | No | Preloaded at agent startup |
| `isolation` | Yes | No | `worktree` for auto-isolation |
| `mcp_servers` | No | No | Plugin extension |
| `tier` | No | No | Plugin extension |
| `whenToUse` | No | No | Plugin extension |
| `color` | No | No | Plugin extension |

## Tiered Agent Naming

- **Base (Sonnet)**: `<agent>.md` (e.g., `planner.md`)
- **Fast (Haiku)**: `<agent>-haiku.md` (e.g., `planner-haiku.md`)
- **Complex (Opus)**: `<agent>-opus.md` (e.g., `planner-opus.md`)

## Skill Definition (skills/*/SKILL.md)

```yaml
---
name: skill-name
description: What the skill does
allowed-tools: Read, Glob, Grep
context: fork           # Runs in isolated context
---
# Skill behavior instructions
```
