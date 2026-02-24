---
description: Manage git worktrees for parallel step execution in isolated environments
argument-hint: "<subcommand> [options]"
---

# /cw:worktree - Git Worktree Management

Manage git worktrees for parallel execution of CAW phases/steps in isolated environments.

## Usage

```bash
# Native worktree (recommended, v2.1+)
claude -w <name>                  # Start Claude in worktree
/cw:worktree list                 # Show status
/cw:worktree clean                # Remove completed

# Phase-based creation
/cw:worktree create phase 2       # Single phase
/cw:worktree create phase 2,3,4   # Multiple phases
```

## Native Worktree Integration (v2.1+)

Claude Code v2.1.49+ provides native worktree support:

- **CLI**: `claude -w <name>` creates `.claude/worktrees/<name>/` with branch `worktree-<name>`
- **Agent isolation**: Builder agents use `isolation: worktree` in frontmatter for automatic isolation
- **Hooks**: `WorktreeCreate` automatically copies `.caw/` files to new worktrees
- **Auto-cleanup**: Worktrees with no changes are automatically removed

### Builder Auto-Isolation

All Builder agent tiers (haiku/sonnet/opus) have `isolation: worktree` set, meaning:
- When spawned as subagents, they automatically get their own worktree
- Source code modifications are isolated from the main working tree
- Results are merged back when the subagent completes

## Subcommands

### create phase N

Creates isolated git worktree for a phase.

**Workflow**:
1. Validate Phase Deps are satisfied
2. Create `.claude/worktrees/phase-N/` (native path)
3. Create `worktree-phase-N` branch from HEAD
4. WorktreeCreate hook copies `.caw/` files automatically

**Output**:
```
Creating Worktree for Phase 2

Directory: .claude/worktrees/phase-2/
Branch: worktree-phase-2
Copied: .caw/ files (via WorktreeCreate hook)

Execute:
  claude -w phase-2
  /cw:next phase 2

After complete: /cw:merge
```

**Multiple Phases**:
```bash
/cw:worktree create phase 2,3,4
# Creates 3 worktrees, outputs commands for each
```

### list

Shows status of all CAW worktrees:

```
CAW Worktrees

| Path | Branch | Status | Progress |
|------|--------|--------|----------|
| .claude/worktrees/phase-2 | worktree-phase-2 | In Progress | 3/5 |
| .claude/worktrees/phase-3 | worktree-phase-3 | Complete | 4/4 |

Tip: /cw:merge phase 3 | /cw:worktree clean
```

### clean

Removes worktrees and branches:
- Default: Only completed/merged worktrees
- `--all`: All CAW worktrees (requires confirmation)

## Directory Structure

```
project/
├── .caw/task_plan.md              # Master plan
├── .claude/worktrees/
│   ├── phase-2/                   # Phase 2 worktree
│   │   └── .caw/task_plan.md      # Copied by WorktreeCreate hook
│   └── phase-3/                   # Phase 3 worktree
└── src/
```

## Lifecycle

```
CREATE → WORK → COMPLETE → MERGE → CLEAN
```

1. `claude -w <name>` or `/cw:worktree create phase N` - Creates worktree
2. Work in worktree (Builder auto-isolates via `isolation: worktree`)
3. All steps marked complete
4. `/cw:merge` in main directory
5. `/cw:worktree clean` removes worktree

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Deps not met | Shows missing deps, suggests alternatives |
| Already exists | Shows status, offers recreate option |
| Uncommitted changes | Requires stash first |
| Conflicting deps | Cannot create both, suggests order |
| No changes in worktree | Auto-removed by Claude Code |

## Integration

- Builder agents: Auto-isolated via `isolation: worktree`
- `/cw:next --worktree phase N` - Shortcut for create
- `/cw:merge` - Merges completed worktrees
- `/cw:status --worktrees` - Shows worktree status
- `/cw:team` - Teams use worktrees for member isolation

## Legacy Reference

Previous versions used `.worktrees/phase-N/` paths and `caw/phase-N` branches.
These are superseded by native `.claude/worktrees/<name>/` and `worktree-<name>` branches.

## .gitignore

```
.claude/worktrees/
```
