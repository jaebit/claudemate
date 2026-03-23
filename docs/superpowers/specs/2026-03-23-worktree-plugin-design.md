# Worktree Plugin Design

## Overview

A claudemate plugin (`plugins/worktree/`) that provides git worktree lifecycle management via 3 skills. Agent-first design (autopilot, crew Builder), also usable by users directly.

**Problem**: Builder agents need isolation for risky build steps, but hardcoding `isolation: worktree` in the Agent tool causes the orchestrator's post-step commit cycle to miss changes (changes live in a temp branch, not the main working directory).

**Solution**: Explicit worktree lifecycle managed through skills — create worktree, work in it, commit there, then squash-merge back to main. The orchestrator sees the merge commit.

## Plugin Structure

```
plugins/worktree/
├── plugin.json
├── CLAUDE.md
└── skills/
    ├── create/SKILL.md
    ├── merge/SKILL.md
    └── cleanup/SKILL.md
```

### plugin.json

```json
{
  "name": "worktree",
  "version": "0.1.0",
  "description": "Git worktree lifecycle management — create, merge, cleanup"
}
```

### Registration

Plugin must be registered in `.claude-plugin/marketplace.json` per claudemate golden rules.

## Skills

### worktree:create

**Frontmatter:**
```yaml
name: create
description: >
  Create an isolated git worktree for feature work or build step isolation.
  Use when starting feature work, before risky build steps, or when parallel
  isolation is needed. Agent-first: no interactive prompts for directory selection.
argument-hint: "<branch-name> [--base <branch>]"
user_invocable: true
disable-model-invocation: false
```

**Invocation**: `/worktree:create <branch-name> [--base <branch>]`

**Phases:**

1. **Validation**
   - Verify git repository (`git rev-parse --git-dir`)
   - Warn and stop if already inside a worktree (`git rev-parse --git-dir` contains `/worktrees/`)
   - Check branch-name doesn't already exist (`git rev-parse --verify <branch>`)

2. **Directory Selection**
   - Check `.worktrees/` exists → use it
   - Otherwise create `.worktrees/` and add to `.gitignore` (verify with `git check-ignore`)
   - Path: `.worktrees/<branch-name>`

3. **Worktree Creation**
   - `git worktree add -b <branch-name> .worktrees/<branch-name> [base]`
   - Default base: current HEAD

4. **Project Setup**
   - Auto-detect and install dependencies (all detected ecosystems, in order):
     - `pnpm-lock.yaml` → `pnpm install`
     - `yarn.lock` → `yarn install`
     - `package-lock.json` or `package.json` → `npm install`
     - `Cargo.toml` → `cargo build`
     - `poetry.lock` → `poetry install`
     - `requirements.txt` → `pip install -r requirements.txt`
     - `go.mod` → `go mod download`
   - If install fails: warn and continue (don't abort worktree creation)
   - Copy `.caw/` directory to worktree if present (crew compatibility)
   - Note: `.caw/` copy is one-directional. Observations added in the worktree are not automatically synced back — only code changes are merged.

5. **Report**
   - Worktree path, branch name, setup result

**Agent behavior**: No user prompts for directory selection — always uses `.worktrees/`. Minimal output.

### worktree:merge

**Frontmatter:**
```yaml
name: merge
description: >
  Squash-merge the current worktree branch into the main branch. Analyzes
  git history and source code to craft a comprehensive commit message.
  Must be run from inside a worktree.
argument-hint: "[target-branch]"
user_invocable: true
disable-model-invocation: false
```

**Invocation**: `/worktree:merge [target-branch]`

**Phases:**

1. **Validation**
   - Verify running inside a worktree (`git rev-parse --git-dir` contains `/worktrees/`)
   - Stop if not in a worktree
   - Stop if worktree has uncommitted changes (`git status --porcelain`)
   - **Check original repo status**: resolve original repo via `git rev-parse --git-common-dir`, then check `git -C <repo> diff-index --quiet HEAD --`. If original repo has uncommitted changes, stop with: "Original repo has uncommitted changes. Commit or stash them before merging."

2. **Research**
   - `git log --oneline <target>..HEAD` — commit history
   - `git diff <target>...HEAD --stat` — changed files summary
   - `git diff <target>...HEAD` — full diff for analysis
   - Categorize changes: feat/fix/refactor/test/docs/chore
   - Identify dominant conventional commit type

3. **Target Branch Preparation**
   - Resolve original repo path via `git rev-parse --git-common-dir` (parent of result)
   - Resolve target branch:
     1. Use argument if provided
     2. Check `git symbolic-ref refs/remotes/origin/HEAD` for default branch
     3. Fall back to `main`, then `master`
     4. If none exist, stop and ask user
   - Fetch latest from remote if available (`git -C <repo> fetch origin <target> 2>/dev/null`)
   - Detect and warn about stray WIP commits on target

4. **Squash Merge**
   - Checkout target in original repo: `git -C <repo> checkout <target>`
   - Merge: `git -C <repo> merge --squash <worktree-branch>`
   - On conflict: `git -C <repo> merge --abort`, report conflicting files, stop
   - Never auto-resolve conflicts

5. **Commit**
   - Generate conventional commit message from Phase 2 analysis:
     ```
     <type>: <summary, imperative mood, max 72 chars>

     <2-4 sentence paragraph: what and why>

     Changes:
     - <grouped bullet points>

     Co-Authored-By: Claude <model> <noreply@anthropic.com>
     ```
   - Commit via heredoc in original repo
   - **Error recovery**: if commit fails (e.g., pre-commit hook), run `git -C <repo> reset HEAD` to unstage, report failure with guidance

6. **Verification**
   - Show `git log --oneline -3` from original repo
   - Report: commit hash, summary, target branch
   - Note: worktree still exists, use `worktree:cleanup` to remove

**Agent behavior**: Phase 2 diff analysis runs automatically without user confirmation. Commit message generated and applied without review prompt.

### worktree:cleanup

**Frontmatter:**
```yaml
name: cleanup
description: >
  Remove completed or stale git worktrees. Without --all, only removes
  worktrees whose branches are already merged. With --all, removes all
  worktrees but always requires user confirmation for unmerged ones.
argument-hint: "[--all]"
user_invocable: true
disable-model-invocation: false
```

**Invocation**: `/worktree:cleanup [--all]`

**Phases:**

1. **Scan**
   - `git worktree list` — active worktrees
   - Scan `.worktrees/` directory
   - Check each worktree branch merge status against target (`git branch --merged <target>`)

2. **Classify**
   - **merged**: branch already merged into target → safe to delete
   - **unmerged**: not yet merged → skip unless `--all`
   - **stale**: worktree reference with no directory → prune target

3. **Execute**
   - `git worktree prune` (stale cleanup)
   - Merged: `git worktree remove <path>` → `git branch -d <branch>`
   - `--all` with unmerged: use `AskUserQuestion` to confirm deletion, listing each unmerged branch. **Always requires user confirmation**, even from agents.

4. **Report**
   - Deleted worktrees/branches
   - Remaining worktrees

**Safety**: Unmerged worktree deletion always requires explicit user confirmation via `AskUserQuestion`. This is a hard rule, not overridable by agents.

## Integration Points

### Autopilot

Autopilot's build phase can use worktree isolation per step:
1. `Skill("worktree:create", "step-N")` before risky build steps
2. Builder agent works in `.worktrees/step-N/`
3. Builder commits in worktree
4. `Skill("worktree:merge")` to squash-merge back
5. Orchestrator sees merge commit, continues post-step cycle

Both `/worktree:create step-N` (user) and `Skill("worktree:create", "step-N")` (agent) invoke the same skill — the `disable-model-invocation: false` setting enables both paths.

### Crew

`crew:go` Builder can invoke worktree skills instead of `isolation: worktree` on Agent tool. Same lifecycle as autopilot integration.

### User

Direct `/worktree:create feature-auth`, work manually, `/worktree:merge` when done.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Deployment | claudemate plugin | Marketplace distribution, usable by autopilot/crew/user |
| Implementation | Pure skills (no MCP) | Git commands only, no runtime dependency, easy to debug |
| Worktree dir | `.worktrees/` | Hidden, consistent, auto-gitignored |
| Merge strategy | squash-merge | Clean history, single commit per step |
| Conflict resolution | Never auto-resolve | Safety — always report to user/orchestrator |
| Unmerged deletion | Always confirm | Prevent data loss, even from agent context |
| .caw/ handling | Copy on create, one-directional | Crew compatibility — observations carry over but don't sync back |
| Dependency install failure | Warn and continue | Don't abort worktree creation for optional setup |
| Original repo dirty check | Block merge | Prevent checkout failures and state corruption |
| Commit failure recovery | `git reset HEAD` + report | Don't leave repo in dirty squash-merge state |

## References

- kimoring-ai-skills `merge-worktree` — Phase structure for merge skill
- oh-my-claudecode `git-worktree.ts` + `merge-coordinator.ts` — Metadata tracking, conflict detection patterns
- superpowers `using-git-worktrees` — Directory selection, gitignore verification
- Memory: `project_worktree_skill_plan.md` — Original problem and plan
