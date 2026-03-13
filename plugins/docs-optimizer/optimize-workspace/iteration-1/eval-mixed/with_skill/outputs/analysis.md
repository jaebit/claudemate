# Optimization Analysis: mixed-CLAUDE.md

## Step 1: SCAN

- **Total lines:** 86
- **Sections:** 9

| Section | Line Range | Lines |
|---------|-----------|-------|
| Build & Test | 3-19 | 17 |
| Architecture | 21-28 | 8 |
| Project Context | 30-32 | 3 |
| Key Files | 34-43 | 10 |
| Constraints | 45-51 | 7 |
| Dependencies | 53-60 | 8 |
| REST API Conventions | 62-69 | 8 |
| CI/CD | 71-79 | 9 |
| Monitoring | 81-86 | 6 |

## Step 2: CLASSIFY

| Section | Lines | Classification | Reason |
|---------|-------|----------------|--------|
| Build & Test | 17 | HIGH-VALUE | Exact CLI invocations the agent cannot infer (cargo flags, features, env vars) |
| Architecture | 8 | NEUTRAL | High-level pipeline overview; duplicates what's discoverable from src/ directory structure |
| Project Context | 3 | NEUTRAL | Background narrative; no actionable rules for the agent |
| Key Files | 10 | HARMFUL | Detailed file inventory; agent discovers via Glob/Read; goes stale on refactor |
| Constraints | 7 | HIGH-VALUE | Repo-specific immutable rules (latency targets, batch sizes, derive requirements, error handling policy) |
| Dependencies | 8 | NEUTRAL | Tech stack list; discoverable from Cargo.toml |
| REST API Conventions | 8 | HARMFUL | General coding patterns the LLM already knows (standard REST, HTTP methods, JSON, pagination) |
| CI/CD | 9 | HIGH-VALUE | Exact CI pipeline steps the agent needs to replicate locally before pushing |
| Monitoring | 6 | NEUTRAL | Operational info (URLs, integrations); useful but partially aspirational |

## Step 3: PLAN

| Section | Strategy | Target | Expected Lines |
|---------|----------|--------|----------------|
| Build & Test | Keep | (verbatim) | 17 |
| Architecture | Merge | Compress into 2-line summary in a Context section | 2 |
| Project Context | Delete | Background narrative, not actionable | 0 |
| Key Files | Delete | Auto-discoverable via Glob; stale inventory | 0 |
| Constraints | Keep | (verbatim) | 7 |
| Dependencies | Pointer | Reference Cargo.toml | 1 |
| REST API Conventions | Delete | General knowledge the LLM already has | 0 |
| CI/CD | Keep | (verbatim) | 9 |
| Monitoring | Merge | Compress to key URLs only | 2 |

**Expected final line count:** ~38 lines (from 86)
**Expected reduction:** ~56%

## Step 5: VERIFY

**Pointer targets:**
- `Cargo.toml` -- standard Rust project file; exists in any Rust repo

**Before/After:**
```
Before: 86 lines | After: 50 lines | Reduction: 42%
```

**Sections removed (HARMFUL):**
- Key Files (detailed file inventory, auto-discoverable)
- REST API Conventions (general LLM knowledge)

**Sections removed (NEUTRAL):**
- Project Context (background narrative, not actionable)

**Sections compressed:**
- Architecture: 8 lines -> 1 line summary
- Dependencies: 8 lines -> 1 line pointer to Cargo.toml
- Monitoring: 6 lines -> 2 lines (kept actionable URLs only)
