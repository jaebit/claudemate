# Optimization Analysis — minimal-CLAUDE.md

## Step 1: SCAN

- **Total lines:** 13
- **Sections:**
  - `## Commands` — 7 lines (lines 3–9)
  - `## Rules` — 3 lines (lines 11–13)

## Step 2: CLASSIFY

| Section | Lines | Classification | Reason |
|---------|-------|----------------|--------|
| Commands | 7 | HIGH-VALUE | Exact CLI invocations (pytest, mypy, ruff) — agent cannot infer these |
| Rules | 3 | HIGH-VALUE | Repo-specific constraints: Python version, type-hint policy, structlog requirement |

**Result:** 100% of content is HIGH-VALUE. No harmful or neutral content detected.

## Step 3: PLAN

| Section | Strategy | Target | Expected Lines |
|---------|----------|--------|----------------|
| Commands | Keep verbatim | — | 7 |
| Rules | Keep verbatim | — | 3 |

No migration needed. All content meets HIGH-VALUE criteria.

## Step 4: REWRITE

No changes applied. The file is already minimal and well-structured:
- Commands section contains only exact CLI invocations
- Rules section contains only actionable, repo-specific constraints
- No filler text, no duplicated information, no stale content

## Step 5: VERIFY

- No pointers created (nothing to verify)
- No content removed (all HIGH-VALUE)

```
Before: 13 lines | After: 13 lines | Reduction: 0%
```

**Conclusion:** This file is already optimally structured. It contains only high-value content with zero bloat.
