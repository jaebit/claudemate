# Module Context

**Module:** Worktree
**Version:** 0.1.0
**Role:** Git worktree lifecycle management for agent isolation and user feature branches.

Worktrees are created under `.worktrees/` by default. This directory is auto-added to `.gitignore`.

---

## Skills

```bash
/worktree:create    # Create a new git worktree (branch + directory)
/worktree:merge     # Merge a worktree branch back to the base branch
/worktree:cleanup   # Remove worktree directory and prune git metadata
```

---

## Quick Usage

### `worktree:create`

```
/worktree:create --branch feat/my-feature
# Creates .worktrees/feat-my-feature linked to branch feat/my-feature
```

Agent invocation:
```
Skill("worktree:create", args="--branch feat/my-feature")
```

### `worktree:merge`

```
/worktree:merge --branch feat/my-feature --into main
# Merges feat/my-feature into main, then removes the worktree
```

Agent invocation:
```
Skill("worktree:merge", args="--branch feat/my-feature --into main")
```

### `worktree:cleanup`

```
/worktree:cleanup --branch feat/my-feature
# Removes .worktrees/feat-my-feature and prunes git worktree metadata
```

Agent invocation:
```
Skill("worktree:cleanup", args="--branch feat/my-feature")
```

---

## Notes

- Default worktree root: `.worktrees/` (auto-added to `.gitignore`)
- Each worktree is a full git checkout — agents can work in isolation without cross-contamination
- Always run `worktree:cleanup` after merging to avoid stale worktree entries
