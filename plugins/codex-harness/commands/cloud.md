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
