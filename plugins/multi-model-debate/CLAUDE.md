# Multi-Model Debate

Structured 3-model debate orchestration (Claude + Codex + Gemini) for software engineering decisions.

## Prerequisites

- **codex** CLI installed and authenticated (`which codex` must succeed — use `openai/codex-plugin-cc` or `npm i -g @openai/codex`)
- **gemini-cli** installed and authenticated (`which gemini` must succeed)

## Skills

- `/debate:start <topic>` — Start a new multi-model debate (`disable-model-invocation`: user-only)
- `/debate:resume [debate-dir]` — Resume an interrupted debate (`disable-model-invocation`: user-only)
- `debate-orchestration` — Internal orchestration logic (`user-invocable: false`, `context: fork`)

## Constraints

- **Parallel dispatch**: Always dispatch 3 agents in the same message (3 tool calls)
- **Codex**: Use Bash tool: `codex -q "<prompt>"` (read-only by default)
- **Gemini**: Use Agent tool → sub-agent runs `gemini -p "..."` via Bash
- **Claude**: Use Agent tool (sub-agent with Read/Glob/Grep)
- **Output**: All debate artifacts go to `.debate/<debate-id>/`
- **Round limit**: If more than 3 rounds needed, ask user for confirmation before proceeding
- **State**: `state.json` tracks progress for resume capability
