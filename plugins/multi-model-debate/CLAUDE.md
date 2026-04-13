# Multi-Model Debate

Structured 3-model debate orchestration (Claude + Codex + Gemini) for software engineering decisions.

## Prerequisites

- **codex-cli** plugin installed (provides `mcp__plugin_codex-cli_codex__codex`)
- **gemini-cli** installed and authenticated (`which gemini` must succeed)

## Skills

- `/debate:start <topic>` — Start and orchestrate a debate: round dispatch inline (MCP accessible), synthesis via fork
- `/debate:resume [debate-dir]` — Resume an interrupted debate (same inline dispatch pattern)
- `debate-orchestration` — Synthesis & consensus only (`user-invocable: false`, `context: fork`, no MCP needed)

## Architecture (Hybrid)

Round dispatch (Codex MCP, Claude Agent, Gemini Agent) runs **inline** in `debate-start`/`debate-resume`.
Synthesis and final consensus run in **fork** via `debate-orchestration` (no MCP tools required).
This ensures Codex MCP access on all platforms including Windows.

## Constraints

- **Parallel dispatch**: Always dispatch 3 agents in the same message (3 tool calls) — done in debate-start (inline)
- **Codex**: Use `mcp__plugin_codex-cli_codex__codex` with `sandbox: read-only` (CLI fallback for Windows/MCP-unavailable sessions)
- **Gemini**: Use Agent tool → sub-agent runs `gemini -p "..."` via Bash
- **Claude**: Use Agent tool (sub-agent with Read/Glob/Grep)
- **Output**: All debate artifacts go to `.debate/<debate-id>/`
- **Round limit**: If more than 3 rounds needed, ask user for confirmation before proceeding
- **State**: `state.json` tracks progress for resume capability
- **Fork boundary**: `debate-orchestration` MUST NOT call MCP tools or dispatch agents — only Read/Write/Bash/Glob/Grep
