---
name: commit-discipline
description: "Classifies staged git changes as structural (tidy) or behavioral (build) per Kent Beck's Tidy First principles, and detects when both are mixed in a single commit. Invoke before committing to check: should I split this commit? Are my renames/refactors mixed with new features? Is this a valid [tidy] or [feat] commit? Also handles commit prefix selection, hotfix exceptions, and staged diff readiness review."
context: fork
agent: general-purpose
disable-model-invocation: true
allowed-tools: Bash, Read, Grep
---

# Commit Discipline

Enforces Tidy First: separate structural and behavioral changes.

## Staged Changes

- **Staged files**: !`git diff --cached --stat 2>/dev/null || echo "(no staged changes)"`
- **Changed file list**: !`git diff --cached --name-only 2>/dev/null || echo "(none)"`

## Forked Context Returns

```yaml
status: VALID | INVALID | MIXED_CHANGE_DETECTED
change_type: tidy | build | mixed
suggestion: [commit split recommendation if mixed]
```

> "Never mix structural and behavioral changes in the same commit."
> — Kent Beck, Tidy First

## Triggers

1. Before commit execution (hook)
2. Builder about to commit
3. Manual validation request
4. During `/crew:review`

## Commit Types

| Prefix | Type | Allowed Changes |
|--------|------|-----------------|
| `[tidy]` | Structural | Rename, extract, reorganize, dead code |
| `[feat]` | Behavioral | New functions, features |
| `[fix]` | Behavioral | Logic corrections |
| `[test]` | Behavioral | New/updated tests |
| `[docs]` | Neutral | Comments, README |

## Change Classification

### Structural (Tidy)
No behavior change: rename, extract method, move code, remove dead code, formatting
**Verify**: Tests pass before AND after

### Behavioral (Build)
Alters behavior: new function, logic change, new tests, new deps
**Verify**: New tests written, all pass

## Detection Algorithm

```yaml
structural_indicators: rename, similar_line_count (±5%), no_new_exports/functions/logic
behavioral_indicators: new_exports, new_functions, logic_additions, new_tests, new_deps

classification:
  all_structural → tidy
  all_behavioral → build
  mixed → SPLIT_REQUIRED
```

## Validation Workflow

```
1. Read git diff --staged
2. Classify each file
3. Aggregate:
   - All tidy → ✅ [tidy] prefix
   - All build → ✅ [feat]/[fix] prefix
   - Mixed → ❌ Block, suggest split
```

## Mixed Change Response

```
⚠️ Mixed Change Detected

Structural: jwt.ts rename, helpers.ts extract
Behavioral: jwt.ts new function, modified logic

Recommendation:
1. [tidy] Improve naming in auth module
2. [feat] Add token refresh functionality
```

## Edge Cases

| Case | Approach |
|------|----------|
| Large refactor | Multiple small [tidy] commits |
| Emergency fix | [hotfix] allowed, document why |

## Boundaries

**Will:** Analyze staged changes, block mixed commits, suggest splitting
**Won't:** Auto-split (requires user), modify staged, force without consent
