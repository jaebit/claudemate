# worktree

Git worktree lifecycle management for Claude Code. Create isolated worktrees for agent-driven development, merge them back, and clean up afterward.

## Version

| Component | Version |
|-----------|---------|
| plugin.json | 0.1.0 |
| marketplace.json | 0.1.0 |

## Installation

```bash
claude plugins add github:jaebit/claudemate
claude plugins install worktree
```

## Skills

| Skill | Description |
|-------|-------------|
| `/worktree:create` | Create a new git worktree (branch + directory) |
| `/worktree:merge` | Merge a worktree branch back to the base branch |
| `/worktree:cleanup` | Remove worktree directory and prune git metadata |

## Usage

### Create a worktree

```bash
/worktree:create feat/my-feature
# Creates .worktrees/feat-my-feature linked to branch feat/my-feature

/worktree:create feat/my-feature --base main
# Create worktree branching from main instead of HEAD
```

### Merge back

```bash
/worktree:merge
# Auto-detects target branch (origin/HEAD, main, or master)

/worktree:merge main
# Explicitly merge into main
```

### Clean up

```bash
/worktree:cleanup
# Remove merged worktrees only

/worktree:cleanup --all
# Remove all worktrees (prompts before deleting unmerged ones)
```

## Agent Invocation

Skills can be invoked programmatically from other agents:

```
Skill("worktree:create", args="feat/my-feature")
Skill("worktree:merge", args="main")
Skill("worktree:cleanup", args="")
```

## Notes

- Worktrees are created under `.worktrees/` (auto-added to `.gitignore`)
- Each worktree is a full git checkout — agents work in complete isolation
- The `autopilot` plugin uses worktrees for per-step build isolation via `--worktree` flag
- Always run `worktree:cleanup` after merging to avoid stale entries
