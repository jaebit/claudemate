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
