# Spec Review Protocol

Shared review loop for design documents produced by Planner (brainstorm) and Architect agents.

## When to Use

After writing any spec or design document:
- `.caw/brainstorm.md` (Planner brainstorm mode)
- `.caw/design/architecture.md` (Architect --arch)
- `.caw/design/ux-ui.md` (Architect --ui)

## Review Criteria

| # | Category | What to Look For |
|---|----------|------------------|
| 1 | **Completeness** | TODOs, placeholders, "TBD", incomplete sections |
| 2 | **Coverage** | Missing error handling, edge cases, integration points |
| 3 | **Consistency** | Internal contradictions, conflicting requirements |
| 4 | **Clarity** | Ambiguous requirements, vague language |
| 5 | **YAGNI** | Unrequested features, over-engineering, speculative abstractions |
| 6 | **Scope** | Focused on single concern — not covering multiple independent subsystems |
| 7 | **Architecture** | Clear unit boundaries, well-defined interfaces, independently testable |

## Subagent Dispatch Template

```
Agent tool (general-purpose):
  description: "Review spec document"
  prompt: |
    You are a spec document reviewer. Verify this document is complete and ready for planning.

    **Document to review:** [SPEC_FILE_PATH]

    ## Check These Categories

    | Category | What to Look For |
    |----------|------------------|
    | Completeness | TODOs, placeholders, "TBD", incomplete sections |
    | Coverage | Missing error handling, edge cases, integration points |
    | Consistency | Internal contradictions, conflicting requirements |
    | Clarity | Ambiguous requirements, vague language |
    | YAGNI | Unrequested features, over-engineering |
    | Scope | Focused on single concern, not multiple independent subsystems |
    | Architecture | Clear boundaries, well-defined interfaces, independently testable |

    ## Critical Focus

    - Any TODO markers or placeholder text
    - Sections saying "to be defined later"
    - Sections noticeably less detailed than others
    - Units that lack clear boundaries or interfaces

    ## Output

    **Status:** APPROVED | ISSUES_FOUND

    **Issues (if any):**
    - [Section]: [specific issue] — [why it matters]

    **Recommendations (advisory, non-blocking):**
    - [suggestion]
```

## Review Loop Protocol

```
[1] Agent writes spec/design document to disk
[2] Dispatch spec-reviewer subagent (template above)
[3] If APPROVED → proceed to User Review Gate
[4] If ISSUES_FOUND:
    a. Fix issues in document
    b. Re-dispatch reviewer
    c. Repeat (max 3 iterations)
    d. If still failing after 3 → present issues to user, ask for guidance
[5] User Review Gate:
    a. Present document summary to user
    b. Ask: "Review the spec at [path]. Approve, or request changes?"
    c. If changes requested → apply changes, return to [2]
    d. If approved → proceed to next workflow step
```

## Integration

- **Complements**: `quality-gate` skill (which validates code, not design documents)
- **Used by**: Planner (brainstorm mode), Architect (--arch, --ui)
- **Referenced from**: `commands/explore.md`
