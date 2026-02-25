# Module Context

**Module:** Codex Harness
**Version:** 1.0.0
**Role:** MCP-native Codex integration for Claude Code.
**Tech Stack:** MCP server (codex mcp-server), Markdown commands, YAML frontmatter.

## Prerequisites

- Codex CLI installed and authenticated
- `codex mcp-server` support (Codex App Server version)

---

# Architecture

## MCP Server

The plugin declares `codex mcp-server` in `plugin.json`. Claude Code auto-starts the server on plugin load, exposing two MCP tools:

- **`codex`**: Start a new Codex session (prompt, model, approval-policy, sandbox, reasoning-effort)
- **`codex-reply`**: Continue an existing session (thread_id, message)

## CLI Commands (2)

Only cloud features that are not exposed via MCP:

- **cloud** (`commands/cloud.md`): `codex cloud --env <id> "<task>"`
- **apply** (`commands/apply.md`): `codex apply <task_id>`

---

# MCP Tool Parameters

## `codex` tool

| Parameter | Type | Default | Values |
|-----------|------|---------|--------|
| `prompt` | string | (required) | Any text prompt |
| `model` | string | gpt-5.2 | gpt-5.2, gpt-5.2-codex |
| `approval-policy` | string | on-request | untrusted, on-request, on-failure, never |
| `sandbox` | string | read-only | read-only, workspace-write, full-access |
| `reasoning-effort` | string | medium | low, medium, high |

## `codex-reply` tool

| Parameter | Type | Default | Values |
|-----------|------|---------|--------|
| `thread_id` | string | (required) | Thread ID from previous `codex` call |
| `message` | string | (required) | Follow-up message |

---

# Directory Structure

```
codex-harness/
  .claude-plugin/plugin.json   # MCP server declaration
  README.md
  CLAUDE.md
  commands/
    cloud.md                   # CLI: codex cloud
    apply.md                   # CLI: codex apply
```

---

# Local Golden Rules

## Do's

- **DO** rely on MCP tools (`codex`, `codex-reply`) for all standard Codex operations.
- **DO** use `codex-reply` with thread IDs for session continuity.
- **DO** keep CLI commands only for features not available via MCP.

## Don'ts

- **DON'T** wrap `codex exec` in Bash when the MCP `codex` tool can do the same.
- **DON'T** add CLI wrapper commands for features the MCP server already exposes.
- **DON'T** use write sandbox without explicit user request.
