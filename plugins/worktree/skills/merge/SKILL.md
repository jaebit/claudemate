---
name: merge
description: >
  Squash-merge the current worktree branch into the main branch. Analyzes
  git history and source code to craft a comprehensive commit message.
  Must be run from inside a worktree.
argument-hint: "[target-branch]"
disable-model-invocation: false
allowed-tools: Bash, Read
---

# worktree:merge

Squash-merge the current worktree branch into the target branch, crafting a comprehensive commit message from git history and source analysis.

## Arguments

**Invoked as**: $ARGUMENTS

## Current context

- **Git dir**: !`git rev-parse --git-dir 2>/dev/null || echo "NOT_A_GIT_REPO"`
- **Current branch**: !`git branch --show-current 2>/dev/null || echo "unknown"`
- **Working tree status**: !`git status --porcelain 2>/dev/null || echo "(error)"`

## Phase 1 — Validation

1. Run `git rev-parse --git-dir`. If the output does NOT contain `/worktrees/`, stop with: "This skill must be run from inside a git worktree. Use /worktree:create to create one first."
2. Run `git branch --show-current` and save the result as WORKTREE_BRANCH.
3. Run `git status --porcelain`. If the output is non-empty, stop with: "Uncommitted changes in worktree. Commit or stash them first."
4. Run `git rev-parse --git-common-dir` and resolve the parent directory as ORIGINAL_REPO (e.g., strip the trailing `/.git` component from the result if present, or use the directory containing the `.git` folder).
5. Run `git -C $ORIGINAL_REPO diff-index --quiet HEAD --`. If this fails (exit code non-zero), stop with: "Original repo has uncommitted changes. Commit or stash them before merging."

## Phase 2 — Target Branch Resolution

1. If `$ARGUMENTS` is provided and non-empty, use it as TARGET.
2. Otherwise, try to detect the default branch:
   - Run `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null` and extract the short branch name (strip `refs/remotes/origin/` prefix).
3. If that returns nothing, check if `main` exists: `git rev-parse --verify main 2>/dev/null`.
4. If not, check if `master` exists: `git rev-parse --verify master 2>/dev/null`.
5. If neither exists, stop and ask: "Could not determine target branch. Please specify one: /worktree:merge <branch>"
6. Fetch from remote (ignore failure if no remote): `git -C $ORIGINAL_REPO fetch origin $TARGET 2>/dev/null || true`
7. Run `git -C $ORIGINAL_REPO log --oneline -10 $TARGET` and check commit messages. If any start with `wip:`, `auto-commit`, or `WIP`, print a warning: "Warning: target branch appears to have WIP commits. Verify before merging."

## Phase 3 — Research

1. Run `git log --oneline $TARGET..HEAD` to list all commits on this branch since it diverged from TARGET.
2. Run `git diff $TARGET...HEAD --stat` to get the file change summary.
3. Run `git diff $TARGET...HEAD` to get the full diff. Read it carefully.
4. Use the Read tool to read the most significantly changed files for full context. Prioritize files with the most lines changed or those that are central to the feature.
5. Categorize all changes into conventional commit types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.
6. Identify the dominant type — the one that best characterizes the overall contribution. This will be used as the commit type.

## Phase 4 — Squash Merge

1. Run `git -C $ORIGINAL_REPO checkout $TARGET`
2. Run `git -C $ORIGINAL_REPO merge --squash $WORKTREE_BRANCH`
3. If the merge command fails (conflict or other error):
   - Run `git -C $ORIGINAL_REPO merge --abort`
   - List the conflicting files from the merge error output
   - Stop with: "Merge conflict detected. Resolve the following files manually and then commit:\n<conflicting files>\n\nDo NOT auto-resolve conflicts."

## Phase 5 — Commit

1. Craft a commit message using the Phase 3 analysis. Use this exact format:

   ```
   <type>: <concise summary in imperative mood, under 72 chars, no trailing period>

   <2-4 sentence paragraph explaining what changed and why>

   Changes:
   - <grouped bullet points by category>

   Co-Authored-By: Claude <model> <noreply@anthropic.com>
   ```

2. Commit using a heredoc to preserve formatting exactly:

   ```bash
   git -C $ORIGINAL_REPO commit -m "$(cat <<'EOF'
   <crafted message here>
   EOF
   )"
   ```

3. Error recovery: if the commit fails for any reason (e.g., pre-commit hook rejection), run `git -C $ORIGINAL_REPO reset HEAD` to unstage all changes, then report the failure with: "Commit failed. Staged changes have been unstaged. Reason: <error output>. Fix the issue and re-run /worktree:merge."

## Phase 6 — Verification

1. Run `git -C $ORIGINAL_REPO log --oneline -3` to confirm the commit landed.
2. Report in this format:

   ```
   Merged: <commit-hash> — <summary line>
   Target: <TARGET>
   Branch: <WORKTREE_BRANCH>

   Note: Worktree still exists. Run /worktree:cleanup to remove it, or:
     git worktree remove <worktree-path>
   ```
