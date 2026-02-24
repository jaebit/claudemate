---
description: Run the full CW workflow automatically - from expansion to completion with review and reflection
argument-hint: "<task description>"
---

# /cw:auto - Automated Full Workflow (v2.0)

Execute the complete CW workflow in a single command with enhanced features:
- **Expansion Phase**: Requirements analysis before planning
- **Signal-Based Transitions**: Automatic phase progression
- **Parallel Validation**: 3-architect review (functional/security/quality)
- **Persistence Enforcement**: Auto-resume on interruption

## Usage

```bash
/cw:auto "Add a logout button to the header"
/cw:auto "Fix login validation" --skip-qa
/cw:auto "Simple fix" --no-parallel-validation
/cw:auto "Implement dark mode" --verbose
/cw:auto "Implement auth system" --team
/cw:auto "Large refactor" --team --team-size 3 --debate
```

## Workflow Stages (9-Stage Pipeline)

```
[1/9] expansion → [2/9] init → [3/9] planning → [4/9] execution →
[5/9] qa → [6/9] review → [7/9] fix → [8/9] check → [9/9] reflect
```

## Flags

| Flag | Description |
|------|-------------|
| `--skip-expansion` | Skip expansion phase (well-defined tasks) |
| `--skip-qa` | Skip QA loop stage |
| `--skip-review` | Skip review, fix, and check stages |
| `--skip-reflect` | Skip reflect stage |
| `--no-parallel-validation` | Use single reviewer |
| `--verbose` | Show detailed progress |
| `--no-questions` | Minimize interactive questions |
| `--team` | Use Agent Teams for parallel stages (requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) |
| `--team-size N` | Number of Builder teammates (default: 2) |
| `--debate` | Enable reviewer debate pattern (cross-validation via SendMessage) |

## Signal-Based Phase Transitions

Each phase outputs a completion signal. See [Signal Detection](../_shared/signal-detection.md).

| Phase | Signal |
|-------|--------|
| Expansion | `EXPANSION_COMPLETE` |
| Init | `INIT_COMPLETE` |
| Planning | `PLANNING_COMPLETE` |
| Execution | `EXECUTION_COMPLETE` |
| QA | `QA_COMPLETE` |
| Review | `REVIEW_COMPLETE` |
| Fix | `FIX_COMPLETE` |
| Check | `CHECK_COMPLETE` |
| Reflect | `REFLECT_COMPLETE` |
| Final | `AUTO_COMPLETE` |

## Stage Behaviors

### Stage 1: Expansion
Invoke Analyst Agent to parse task, analyze codebase, extract requirements. Output: `.caw/spec.md`

### Stage 2: Init
Check `.caw/context_manifest.json`. If missing, invoke Bootstrapper Agent.

### Stage 3: Planning
Invoke Planner Agent with spec.md context. Output: `.caw/task_plan.md`

### Stage 4: Execution
Execute pending steps via Builder Agent. Track files created/modified. On error: save state and report.

**Team mode** (`--team`): Independent phases assigned to Builder teammates via Agent Teams. Each member works in an isolated worktree. `TeammateIdle` hook auto-assigns next tasks. Falls back to standard Task-based parallel if `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is not set.

### Stage 5: QA Loop
Invoke `/cw:qaloop` with max_cycles: 2, severity: major.

### Stage 6: Review (Parallel Validation)
Spawn 3 Reviewer agents in parallel:
- **Functional**: Verify spec.md requirements
- **Security**: Check OWASP Top 10
- **Quality**: Check maintainability

Aggregate verdicts. If any REJECTED → proceed to Fix (max 3 rounds).

**Debate mode** (`--debate`): Reviewers exchange findings via SendMessage for cross-validation before producing consensus verdict. See [Team Validation](../_shared/team-validation.md).

### Stage 7: Fix
Parse review issues. Auto-fix via Fixer Agent (Haiku tier). Track in validation-results.json.

### Stage 8: Check
Invoke ComplianceChecker Agent for CLAUDE.md rules and project conventions.

### Stage 9: Reflect
Invoke Ralph Loop: REFLECT → ANALYZE → LEARN → PLAN → HABITUATE.

## State Management

State saved in `.caw/auto-state.json`:
```json
{
  "schema_version": "2.0",
  "phase": "execution",
  "task_description": "Add logout button",
  "config": { "skip_qa": false, "parallel_validation": true, "team_mode": false, "team_size": 2, "debate_mode": false },
  "execution": { "current_step": "2.1", "tasks_completed": 3 },
  "signals": { "detected_signals": [...] }
}
```
Full schema: `../_shared/schemas/auto-state.schema.json`

Stop hook (`hooks/scripts/auto_enforcer.py`) ensures persistence and auto-resume.

## Progress Display

```
🚀 /cw:auto "Add logout button"

[1/9] Expanding...        ✓ (spec.md created)
[2/9] Initializing...     ✓ (already initialized)
[3/9] Planning...         ✓ (2 phases, 5 steps)
[4/9] Executing...        ✓ (5/5 steps complete)
[5/9] QA Loop...          ✓ (build: ✓, tests: ✓)
[6/9] Reviewing...        ✓ (parallel: 3/3 approved)
[7/9] Fixing...           ✓ (2 auto-fixed)
[8/9] Checking...         ✓ (compliant)
[9/9] Reflecting...       ✓

✅ Workflow Complete

📊 Summary:
  • Requirements: 8 extracted
  • Steps executed: 5
  • Issues found: 3 (3 fixed)

---
SIGNAL: AUTO_COMPLETE
---
```

Use `--verbose` for detailed stage-by-stage output.

## Error Handling

On error, state is saved to `.caw/auto-state.json`.

**Resume options:**
- `/cw:next` - Fix manually and continue
- `/cw:auto --continue` - Resume from saved state
- `/cw:status` - Check current status

**Parallel Validation failure:** Auto-proceeds to Fix stage, retries up to 3 rounds.

## Integration

- **Reads**: Task description, .caw/spec.md, .caw/task_plan.md
- **Invokes**: Analyst, Bootstrapper, Planner, Builder, Reviewer (x3), Fixer, ComplianceChecker, Ralph Loop
- **Updates**: .caw/auto-state.json, .caw/task_plan.md, .caw/learnings.md
- **Creates**: .caw/spec.md, .caw/validation-results.json

## Best Practices

1. Use for well-defined tasks (Expansion handles ambiguity)
2. Skip expansion for trivial tasks: `--skip-expansion`
3. Check `.caw/validation-results.json` for review details
4. Use `--verbose` for debugging

## References

- [Signal Detection](../_shared/signal-detection.md)
- [Parallel Validation](../_shared/parallel-validation.md)
- [Auto State Schema](../_shared/schemas/auto-state.schema.json)
