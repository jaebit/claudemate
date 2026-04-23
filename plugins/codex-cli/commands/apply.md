---
description: Apply diff from Codex Cloud task to local workspace
argument-hint: "<task_id>"
allowed-tools: ["Bash"]
---

# Codex Apply

## Instructions

1. Get the task ID from arguments
2. Run:
```bash
codex apply <task_id>
```
3. Show applied changes with `git diff --stat` then `git diff`
4. Summarize modified/added files

## Examples

```
/codex:apply task_abc123
/codex:apply 550e8400-e29b-41d4-a716-446655440000
```

### If codex apply fails

- **codex not in PATH**: Run `npm install -g @openai/codex` or `brew install codex` to install, then ensure `codex` is available (`which codex`).
- **Invalid task_id / missing argument**: The task ID must be a valid UUID or alphanumeric string from `codex cloud` output. Re-run `/codex:cloud` to get a valid task ID.
- **Auth failure** (`OPENAI_API_KEY` unset or expired): Set `export OPENAI_API_KEY=<your-key>` in your shell, or run `codex auth login` to authenticate interactively.
