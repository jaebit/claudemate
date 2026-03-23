---
name: cleanup
description: >
  Remove completed or stale git worktrees. Without --all, only removes
  worktrees whose branches are already merged. With --all, removes all
  worktrees but always requires user confirmation for unmerged ones.
argument-hint: "[--all]"
disable-model-invocation: false
allowed-tools: Bash, AskUserQuestion
---

# worktree:cleanup

Remove completed or stale git worktrees and their branches.

## Arguments

**Invoked as**: $ARGUMENTS

## Current context

- **Git dir**: !`git rev-parse --git-dir 2>/dev/null || echo "NOT_A_GIT_REPO"`
- **Worktrees**: !`git worktree list 2>/dev/null || echo "(none)"`
- **.worktrees/ contents**: !`ls .worktrees/ 2>/dev/null || echo "(empty or missing)"`

## Phase 1 — Scan

1. Run `git rev-parse --git-dir`. If it fails, stop with: "Not a git repository. Aborting."
2. Parse `$ARGUMENTS`: if `--all` is present, set `ALL_MODE=true`. Otherwise `ALL_MODE=false`.
3. List all worktrees: `git worktree list --porcelain`. Parse each entry for `worktree <path>` and `branch refs/heads/<name>`. Exclude the main worktree (the first entry, which is the repo root).
4. Also scan `.worktrees/` if it exists: `ls .worktrees/ 2>/dev/null`. Cross-reference with git's worktree list.
5. Detect target branch for merge status checks:
   - Try `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null` → extract branch name.
   - Fall back: check if `main` exists (`git rev-parse --verify main 2>/dev/null`), then `master`.
   - If none found, use current branch: `git branch --show-current`.
   - Save as `TARGET`.
6. For each worktree branch, check merge status: `git branch --merged $TARGET`. If the branch appears in the output, it is merged.

## Phase 2 — Classify

Group all discovered worktrees into 3 categories:

- **merged**: branch appears in `git branch --merged $TARGET` → safe to delete
- **unmerged**: branch does NOT appear in merged list → skip unless `ALL_MODE=true`
- **stale**: listed by `git worktree list` but directory does not exist on disk

Display a classification table:

```
Worktree Status:

| Path | Branch | Status |
|------|--------|--------|
| .worktrees/step-1 | step-1 | merged |
| .worktrees/feat-x | feat-x | unmerged |
| (missing dir)      | old-wt | stale |

Target branch: <TARGET>
Mode: <default or --all>
```

If no worktrees are found at all, print: "No worktrees found. Nothing to clean up." and stop.

## Phase 3 — Execute

Follow these steps exactly, in order:

### 3a. Prune stale worktrees

Run `git worktree prune` to clean up stale entries. Report how many were pruned.

### 3b. Remove merged worktrees

For each **merged** worktree:
1. `git worktree remove <path>`
2. `git branch -d <branch>`
3. Report: "Removed: <path> (branch: <branch>)"

If a removal fails, print a warning and continue with the next one.

### 3c. Handle unmerged worktrees (only with --all)

If `ALL_MODE=true` AND there are **unmerged** worktrees:

**HARD RULE: ALWAYS use `AskUserQuestion` before deleting unmerged worktrees. This applies even when called by agents. No exceptions.**

Use `AskUserQuestion` with:
- Question: "These worktrees have unmerged changes that will be lost. Delete them? This cannot be undone."
- List each unmerged worktree: path and branch name
- Options: "Delete all unmerged" / "Keep unmerged"

If user confirms deletion:
1. `git worktree remove --force <path>`
2. `git branch -D <branch>`
3. Report: "Force removed: <path> (branch: <branch>)"

If user declines, print: "Kept unmerged worktrees." and skip them.

## Phase 4 — Report

Print a final summary:

```
Cleanup complete.

Removed:
  - <path> (<branch>) [merged]
  - <path> (<branch>) [force-removed]

Remaining:
  - <path> (<branch>) [unmerged]

Stale entries pruned: <N>
```

If `.worktrees/` directory is now empty, note: ".worktrees/ directory is now empty. You can remove it with `rmdir .worktrees`."

If no worktrees were removed, print: "No worktrees were removed."
