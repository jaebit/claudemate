---
name: review
user_invocable: false
description: "Unified code review, QA, compliance checking, and auto-fix"
argument-hint: "[path] [flags]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Agent
---

# /crew:review - Code Review & QA

Unified code review, QA loop, compliance checking, and auto-fix.

## Arguments

**Invoked as**: $ARGUMENTS

## Current State

- **Last review**: !`cat .caw/last_review.json 2>/dev/null | head -8 || echo "(no previous review)"`
- **Task plan**: !`cat .caw/task_plan.md 2>/dev/null | head -10 || echo "(no task plan)"`

## Usage

```bash
# Standard review
/crew:review                        # Review current phase
/crew:review src/auth/              # Review directory
/crew:review src/auth/jwt.ts        # Review file
/crew:review --phase 2              # Review phase 2
/crew:review --step 2.3             # Review specific step
/crew:review --deep                 # Deep analysis (Opus)
/crew:review --focus security       # Focused review

# QA loop mode
/crew:review --loop                 # Build-Review-Fix cycles
/crew:review --loop --max-cycles 5  # Custom max cycles
/crew:review --loop --deep          # QA with Opus diagnosis

# Build/test verification
/crew:review --build                # Verify build and tests pass
/crew:review --build --target test  # Test failures only

# Compliance checking
/crew:review --compliance           # CLAUDE.md rules + conventions
/crew:review --compliance --rules   # Only CLAUDE.md rules
/crew:review --compliance --docs    # Only documentation

# Auto-fix
/crew:review --fix                  # Auto-fix simple issues
/crew:review --fix --deep           # Use Fixer agent for complex issues
/crew:review --fix --interactive    # Review each fix

# Combined
/crew:review --all                  # Full review + compliance + build
/crew:review --gemini               # Cross-model review via Gemini
```

## Modes

| Mode | Flag | Description |
|------|------|-------------|
| **Standard** | (default) | Code quality review via Reviewer agent |
| **Deep** | `--deep` | Thorough analysis via Opus |
| **Loop** | `--loop` | Automated Build → Review → Fix cycles |
| **Build** | `--build` | Verify build/tests pass, diagnose failures |
| **Compliance** | `--compliance` | CLAUDE.md rules and project conventions |
| **Fix** | `--fix` | Auto-fix issues from review |
| **All** | `--all` | Everything combined |
| **Gemini** | `--gemini` | Cross-model review |

## Flags

| Flag | Description |
|------|-------------|
| `--phase N` | Review specific phase |
| `--step N.M` | Review specific step |
| `--deep` | Deep analysis (Opus) |
| `--focus <area>` | Focused: security, performance, correctness |
| `--loop` | QA loop mode (Build → Review → Fix) |
| `--max-cycles N` | Max QA iterations (default: 3) |
| `--severity <level>` | Min severity to fix: minor, major, critical |
| `--build` | Verify build and tests |
| `--target <type>` | Build target: build, test, lint, all |
| `--compliance` | Compliance checking |
| `--rules` | Only CLAUDE.md rules (with --compliance) |
| `--docs` | Only documentation (with --compliance) |
| `--conventions` | Only code patterns (with --compliance) |
| `--fix` | Auto-fix issues |
| `--interactive` | Review each fix (with --fix) |
| `--dry-run` | Preview fixes only |
| `--all` | Full review + compliance + build |
| `--gemini` | Cross-model review |

## Scope Detection

| Argument | Scope |
|----------|-------|
| (none) | Files from most recent completed phase |
| `path` | Specific file or directory |
| `--phase N` | All files modified in phase N |
| `--step N.M` | Files from specific step |
| `--all` | All files in task_plan.md |

## Review Categories

| Category | Checks |
|----------|--------|
| **Correctness** | Logic errors, edge cases, test coverage |
| **Code Quality** | Naming, organization, readability |
| **Best Practices** | Idioms, patterns, error handling |
| **Security** | Input validation, auth checks, sanitization |
| **Performance** | Algorithm efficiency, resource usage |

## Severity Levels

| Level | Meaning |
|-------|---------|
| Critical | Must fix - bugs, security |
| Major | Should fix - significant |
| Minor | Consider - improvements |
| Suggestion | Optional - nice to have |

## QA Loop Mode (`--loop`)

Automated Build → Review → Fix cycle that continues until quality criteria met.

```
BUILD → REVIEW → FIX → EXIT CHECK → (loop or exit)

Exit Conditions:
  No critical/major issues
  Max cycles reached
  Same issues 3 times (stalled)
  Build failure persists
```

**Agent Selection:**

| Phase | Standard | Deep (--deep) |
|-------|----------|---------------|
| Build | crew:Builder (Sonnet) | crew:Builder (Sonnet) |
| Diagnose | crew:Reviewer (Sonnet) | crew:reviewer-opus |
| Fix | crew:Fixer (Sonnet) | crew:Fixer (Opus) |

**Stall Detection**: Issues hashed (`file_path + line_range + issue_type + severity`). Same hashes 3 cycles in a row triggers stall, requiring manual intervention.

## Build Verification (`--build`)

Detects and diagnoses build/test/lint failures with targeted fixes.

```
DETECT → DIAGNOSE → FIX → VERIFY → (loop or exit)
```

| Target | Detection |
|--------|-----------|
| Build | `npm run build`, `cargo build`, etc. |
| Test | `npm test`, `pytest`, etc. |
| Lint | `eslint`, `pylint`, etc. |

## Compliance Mode (`--compliance`)

| Check | Focus |
|-------|-------|
| (default) | Workflow structure + CLAUDE.md rules |
| `--rules` | CLAUDE.md: naming, structure, forbidden patterns |
| `--docs` | JSDoc, README, changelog |
| `--conventions` | Imports, error handling, logging, tests |

## Fix Mode (`--fix`)

| Category | Auto-Fix | Notes |
|----------|----------|-------|
| constants | Yes | Magic numbers → NAMED_CONSTANTS |
| docs | Yes | Generate JSDoc templates |
| style | Yes | Run linter auto-fix |
| imports | Yes | Organize imports |
| naming | Semi | Suggest + confirm |
| logic | `--deep` | Algorithm improvements via Fixer agent |
| performance | `--deep` | Query optimization via Fixer agent |
| security | `--deep` | Vulnerability fixes via Fixer agent |

## Output

```
Code Review Complete

Files reviewed: 3 | Time: 15s

| Category | Score | Issues |
|----------|-------|--------|
| Correctness | Good | 0 |
| Code Quality | Fair | 2 |
| Security | Good | 0 |

Overall: Approved with suggestions

src/auth/jwt.ts
  Clean token generation logic
  Line 45: Extract magic number
  Line 78: Batch DB queries

Next: /crew:review --fix or /crew:go --continue
```

## State Files

- Standard review: `.caw/last_review.json`
- QA loop: `.caw/qaloop_state.json`
- Build verification: `.caw/ultraqa_state.json`

## Boundaries

**Will:**
- Read `.caw/task_plan.md`, source files, config files
- Invoke Reviewer, Fixer, ComplianceChecker, Builder agents
- Update `.caw/task_plan.md` with review notes

**Won't:**
- Modify source code without `--fix` flag
- Skip user confirmation for destructive fixes
