---
name: tdd
description: >
  This skill should be used when the user asks "start TDD", "tdd", "RED-GREEN-REFACTOR",
  "implement stubs", "make tests pass", "Tidy First", or wants to fill implementation stubs
  using architecture-aware TDD with Tidy First commit discipline.
  Does not write code — provides architecture-aware guidance only.
argument-hint: "<project-name> <class-name> e.g. MyApp.Execution.Workflow StepExecutor"
user_invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# /tdd — Architecture-Aware TDD Guide + Tidy First Commit Discipline

Provides architecture-rule-aware implementation guidance for RED→GREEN→REFACTOR cycles with Tidy First commit separation. **Does not write code directly** — the user or external tools implement.

## Usage

```
/tdd MyApp.Execution.Workflow StepExecutor
```

## Reference

Read `arch-guard.json` from the project root before starting. This is the single source of truth for all rules.

## Procedure

### Step 1: Context Loading + RED Verification

1. Read `arch-guard.json`
2. Locate the implementation stub: `{source_root}/{project}/Services/{class}.cs`
3. Locate the RED test file: `{test_root}/{project}.Tests.Unit/{class}Tests.cs`
4. Locate the Contract interface in the Contracts project
5. Run tests: `dotnet test --filter {class}Tests` → confirm all FAIL (RED state)
6. If no RED tests exist: "Run `/implement {project} {interface}` to generate RED tests first."

### Step 2: Method Priority

1. Extract methods with `NotImplementedException` from the stub
2. Sort by dependency order (methods called by other methods first)
3. Confirm order with user

### Step 3: Per-Method GREEN Guide

For each method, repeat this cycle. `/tdd` does not write code — it provides architecture-aware guidance. The user or external tools implement.

**3a. RED Confirmation**

Run the specific test, confirm FAIL.

**3b. Implementation Guide**

Present the architecture rules applicable to this method from `arch-guard.json`:

```
## {MethodName} Implementation Guide
- Allowed references: {from config.references}
- Forbidden references: {from config.references.forbidden}
- Responsibility scope: {from architecture docs if available}

Implement using these constraints. Or use external tools:
superpowers `/test-driven-development` | CAW `/go`
```

**3c. GREEN Confirmation**

After user implements, run the test again → confirm PASS.

**3d. Tidy First Commit Message Suggestion**

```
## Suggested Commit Messages
- `refactor({layer}): add {class} dependencies` (structural — if applicable)
- `feat({layer}): implement {method}` (behavioral)
```

### Step 4: REFACTOR

After all tests are GREEN, review the class:

1. Extract duplicate code
2. Improve naming
3. Check against `config.forbidden_patterns[]`
4. Re-run tests after each refactoring
5. Each refactoring = separate structural commit

### Step 5: Architecture Verification

1. Run all class tests → confirm GREEN
2. Verify reference rules from `arch-guard.json`
3. Verify responsibility boundaries (from architecture docs if available)

### Step 6: Result Report + Next Steps

```
## /tdd Complete

### Implementation Result
| Method | Tests | Status |
|--------|-------|--------|
| {method} | {passed}/{total} | GREEN |

### Tidy First Commit Log
| # | Type | Message |
|---|------|---------|
| 1 | structural | refactor: add dependencies |
| 2 | behavioral | feat: implement {method} |
```

Recommend next steps using slash command format:

| Situation | Recommendation |
|-----------|---------------|
| Architecture violation scan needed | `/arch-check` |
| Architecture guard-rail tests needed | `/test-gen` |
| Design compliance review | `/impl-review {project}` |
| More interfaces to implement | `/implement {project} {next-interface}` |
| Next class in same project | `/tdd {project} {next-class}` |

## Notes

- **No RED tests = blocked** — suggest `/implement` first
- **Does not write code** — provides architecture-aware guidance only (inform, don't block)
- **Tidy First commits are suggestions** — structural/behavioral separation, user decides
- **Generic TDD discipline from external tools** — arch-guard TDD adds architecture rule awareness
