---
description: Create Codex Cloud task (requires --env)
argument-hint: "--env <env_id> <task>"
allowed-tools: ["Bash"]
---

# Codex Cloud

## Instructions

1. Parse arguments: `--env <env_id>` (required) + remaining text as task description
2. Run:
```bash
codex cloud --env <env_id> "<task>"
```
3. Display result:

| Field   | Value       |
|---------|-------------|
| Task ID | `<task_id>` |
| Status  | `<status>`  |
| Env     | `<env_id>`  |

4. Mention `/codex:apply <task_id>` for applying results once complete

## Examples

```
/codex:cloud --env env123 Review this PR
/codex:cloud --env dev-env Fix the failing CI pipeline
```

### If codex cloud fails

- **codex not in PATH**: Run `npm install -g @openai/codex` or `brew install codex`, then verify with `which codex`.
- **Missing `--env` flag**: The `--env <env_id>` argument is required. Obtain a valid environment ID from the Codex Cloud dashboard and re-run.
- **Auth failure** (`OPENAI_API_KEY` unset): Set `export OPENAI_API_KEY=<your-key>` or run `codex auth login`.
- **Network / API quota errors** (429, 503, or timeout): Check your internet connection and OpenAI API quota at https://platform.openai.com/usage. Retry after a brief wait.
