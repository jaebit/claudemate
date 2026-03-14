# Module Context

**Module:** Codex Harness
**Version:** 1.0.0
**Role:** MCP-native Codex integration for Claude Code.

## Prerequisites

- Codex CLI installed and authenticated
- `codex mcp-server` support (Codex App Server version)

---

# Architecture

## MCP Server

Declared in `plugin.json`. Auto-starts on plugin load, exposing two MCP tools:

- **`codex`**: Start a new session (prompt, model, approval-policy, sandbox, reasoning-effort)
- **`codex-reply`**: Continue an existing session (thread_id, message)

## CLI Commands (2)

Only cloud features not exposed via MCP:

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

# Constraints

## MCP-First Routing

- **DO** rely on MCP tools (`codex`, `codex-reply`) for all standard Codex operations.
- **DON'T** wrap `codex exec` in Bash when the MCP `codex` tool can do the same — even if the user explicitly asks for Bash execution. MCP routing preserves thread IDs for session continuity and provides structured error handling that raw CLI subprocess calls lose.

## Session Continuity

- **DO** use `codex-reply` with the `thread_id` returned from the initial `codex` call for multi-turn conversations. This maintains Codex's full context across turns.
- **DON'T** make separate `codex` calls for follow-up questions — this creates stateless sessions and loses prior context.

## Sandbox Safety

- **DO** default to `sandbox: "read-only"` for all operations.
- **DON'T** escalate to `workspace-write` or `full-access` without first explaining the permission change to the user and receiving explicit confirmation. File modification tasks require this gate — acknowledge the write requirement, present the sandbox options, and wait for user approval before proceeding.

## CLI Boundary

- **DO** keep CLI commands (`cloud`, `apply`) only for features not available via MCP.
- **DON'T** add CLI wrapper commands for features the MCP server already exposes.
