---
name: create
description: >
  Create an isolated git worktree for feature work or build step isolation.
  Use when starting feature work, before risky build steps, or when parallel
  isolation is needed. Agent-first: no interactive prompts for directory selection.
argument-hint: "<branch-name> [--base <branch>]"
disable-model-invocation: false
allowed-tools: Bash, Read
---

# worktree:create

Create an isolated git worktree for the branch specified in `$ARGUMENTS`.

## Arguments

**Invoked as**: $ARGUMENTS

## Current context

- **Git dir**: !`git rev-parse --git-dir 2>/dev/null || echo "NOT_A_GIT_REPO"`
- **Working tree root**: !`git rev-parse --show-toplevel 2>/dev/null || echo "unknown"`
- **Existing worktrees**: !`git worktree list 2>/dev/null || echo "(none)"`

## Phase 1 — Validation

1. Run `git rev-parse --git-dir`. If it fails or returns `NOT_A_GIT_REPO`, stop with: "Not a git repository. Aborting."
2. Check if the output of `git rev-parse --git-dir` contains `/worktrees/`. If it does, stop with: "Already inside a worktree. Run worktree:create from the main repository root."
3. Parse `$ARGUMENTS`:
   - First positional token is `<branch-name>`.
   - If `--base <branch>` is present, capture `<base>`.
   - If `<branch-name>` is empty, stop with: "Usage: /worktree:create <branch-name> [--base <branch>]"
4. Run `git rev-parse --verify <branch-name> 2>/dev/null`. If it succeeds (exit 0), stop with: "Branch '<branch-name>' already exists. Choose a different name or delete the existing branch first."

## Phase 2 — Directory Selection

1. Run `git check-ignore -q .worktrees 2>/dev/null`. Note the exit code (0 = ignored, non-zero = not ignored).
2. If `.worktrees/` does not exist, create it: `mkdir -p .worktrees`.
3. Check if `.worktrees/` is gitignored (exit code 0 from step 1). If it is NOT already ignored:
   - Check if `.gitignore` exists: `test -f .gitignore`.
   - If `.gitignore` exists, check if it already contains `.worktrees`: `grep -q '\.worktrees' .gitignore`.
   - If not present (or `.gitignore` doesn't exist), append `.worktrees/` to `.gitignore`: `echo '.worktrees/' >> .gitignore`.
4. Verify: `git check-ignore -q .worktrees && echo "ignored" || echo "warning: .worktrees not ignored"`. If not ignored, print a warning but continue.

## Phase 3 — Worktree Creation

1. Create the worktree:
   - If `--base <base>` was provided: `git worktree add -b <branch-name> .worktrees/<branch-name> <base>`
   - Otherwise: `git worktree add -b <branch-name> .worktrees/<branch-name>`
2. If the command fails, stop with: "Failed to create worktree. See git error above."
3. Verify creation: `ls .worktrees/<branch-name>/`. If the directory is missing or empty, stop with: "Worktree directory not found after creation."

## Phase 4 — Project Setup

Run all dependency installs inside `.worktrees/<branch-name>/`. Check for lockfiles/manifests in order and run the corresponding install command. If an install command fails, print a warning and continue — do NOT abort.

Check in this order:
- `pnpm-lock.yaml` exists → run `pnpm install` (in worktree dir)
- `yarn.lock` exists → run `yarn install` (in worktree dir)
- `package-lock.json` exists → run `npm install` (in worktree dir)
- `package.json` exists (and none of the above lockfiles) → run `npm install` (in worktree dir)
- `Cargo.toml` exists → run `cargo build` (in worktree dir)
- `poetry.lock` exists → run `poetry install` (in worktree dir)
- `requirements.txt` exists → run `pip install -r requirements.txt` (in worktree dir)
- `go.mod` exists → run `go mod download` (in worktree dir)

Run each applicable install as: `(cd .worktrees/<branch-name> && <install-command>) && echo "OK: <install-command>" || echo "WARN: <install-command> failed (continuing)"`

After dependency setup, check if `.caw/` exists at the repo root: `test -d .caw && echo "exists" || echo "not found"`. If it exists, copy it to the worktree: `cp -r .caw/ .worktrees/<branch-name>/.caw/`. Note: `.caw/` is copied one-directionally at creation time. Observations added inside the worktree are not synced back. Only code changes are merged via `worktree:merge`.

## Phase 5 — Report

Print the final summary in this exact format:

```
Worktree ready at .worktrees/<branch-name> (branch: <branch-name>)

Details:
  Path:   .worktrees/<branch-name>
  Branch: <branch-name>
  Base:   <base branch or "HEAD">
  Deps:   <summary of install results, or "none detected">
  .caw/:  <"copied" or "not present">
```

If any warnings occurred during Phase 2 or Phase 4, list them after the summary block.
