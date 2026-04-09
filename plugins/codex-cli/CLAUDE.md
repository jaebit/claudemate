# Codex CLI

MCP-native Codex integration. Requires Codex CLI with `codex mcp-server` support.

## MCP Tools

**`codex`** — Start session

| Parameter | Type | Default | Values |
|-----------|------|---------|--------|
| `prompt` | string | (required) | Any text prompt |
| `model` | string | gpt-5.2 | gpt-5.2, gpt-5.2-codex |
| `approval-policy` | string | on-request | untrusted, on-request, on-failure, never |
| `sandbox` | string | read-only | read-only, workspace-write, full-access |
| `reasoning-effort` | string | medium | low, medium, high |

**`codex-reply`** — Continue session

| Parameter | Type | Default | Values |
|-----------|------|---------|--------|
| `thread_id` | string | (required) | Thread ID from previous `codex` call |
| `message` | string | (required) | Follow-up message |

## CLI Commands

Only for features not exposed via MCP:

- **cloud**: `codex cloud --env <id> "<task>"`
- **apply**: `codex apply <task_id>`

## Constraints

**MCP-First**: Always use MCP tools over Bash `codex exec` — even if user asks for Bash. MCP preserves thread IDs and structured error handling.

**Session Continuity**: Use `codex-reply` with `thread_id` for follow-ups. Never make separate `codex` calls for the same conversation.

**Sandbox Safety**: Default `read-only`. Escalating to `workspace-write` or `full-access` requires explicit user confirmation before proceeding.
