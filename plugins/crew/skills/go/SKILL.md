---
name: go
description: "Run the full CW workflow automatically - plan, build, review, and reflect in one command"
argument-hint: "<task description> [flags]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Agent, AskUserQuestion
---

# /crew:go - Automated Workflow

Execute the complete CW workflow in a single command with a 9-stage pipeline.

## Arguments

**Invoked as**: $ARGUMENTS

## Current State

- **Auto state**: !`cat .caw/auto-state.json 2>/dev/null | head -10 || echo "(no saved state)"`
- **Task plan**: !`cat .caw/task_plan.md 2>/dev/null | head -5 || echo "(no task plan)"`

## Usage

```bash
/crew:go "Add a logout button to the header"
/crew:go --from-plan                          # Start from existing plan
/crew:go --continue                           # Resume from saved state
/crew:go "Fix login validation" --skip-qa
/crew:go "Implement auth" --team --team-size 3
/crew:go --codex "task1" "task2"              # Offload to Codex harness
```

## 9-Stage Pipeline

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
| `--team` | Use Agent Teams for parallel stages (requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) |
| `--team-size N` | Number of Builder teammates (default: 2) |
| `--codex` | Offload tasks to Codex harness |
| `--max-iterations N` | Maximum iterations for execution loop (default: 20) |
| `--continue` | Resume from saved state |
| `--from-plan` | Start from existing task_plan.md |
| `--verbose` | Show detailed progress |
| `--no-questions` | Minimize interactive questions |
| `--worktree` | Isolate each build step in a git worktree (create → build → merge back) |

## Signal-Based Phase Transitions

Each phase outputs a completion signal. See [Signal Detection](../../_shared/signal-detection.md).

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

**CRITICAL**: Steps MUST be executed **one at a time** in a loop. Each step runs individually so the Post-Step Cycle (commit + simplify) executes between steps.

**Execution loop:**
```
for each pending step in task_plan:
    1. Execute step (Codex or Builder — see below)
    2. Run Post-Step Cycle (MANDATORY — see below)
    3. Update state, proceed to next step
```

On error: 5-level recovery: retry → Fixer-Haiku → Planner-Haiku alternative → skip non-blocking → abort. Exit on completion promise, all steps complete, max iterations, 3+ consecutive failures, or critical error.

#### Step Execution: Codex Mode (`--codex`)

When `codex_mode` is true, use the Codex MCP tool as the primary builder for each step.

**1. Build the step prompt:**
Read the step description, notes, and context files from task_plan.md. Construct a prompt:
```
Implement Step {N}: {step description}

Project directory: {cwd}
Context: {relevant file contents or summaries}

Instructions:
- Follow existing project patterns and code style
- Create or modify only the files needed for this step
- Run tests if a test framework is configured
- Do NOT make git commits — the orchestrator handles commits after you complete
```

**2. Run Codex via Bash:**
```bash
codex -q --approval-policy never "<constructed prompt>"
```

**3. On failure** (codex not installed, timeout, auth error):
- Log: `Codex unavailable for Step {N}, falling back to Builder`
- Use Builder Agent (Sonnet) for THIS step only
- Continue trying Codex for subsequent steps (per-step fallback, not per-pipeline)

#### Step Execution: Default Mode (no `--codex`)

Spawn Builder Agent for THIS step only (current behavior). Wait for Builder to complete.

#### Worktree Mode (`--worktree`)

When `--worktree` flag is set, wrap each step execution with worktree isolation:

**Before step execution:**
```
Skill("worktree:create", "step-{N}")
```
This creates `.worktrees/step-{N}` with a branch `step-{N}`.

**Step execution:** Use Codex or Builder as normal, but instruct them to work in `.worktrees/step-{N}/`:
- Add to the step prompt: `"IMPORTANT: Work in directory .worktrees/step-{N}/ — all file reads/writes must be relative to that directory. When done, commit your changes with: cd .worktrees/step-{N} && git add -A && git commit -m '[feat] Step {N}: {step description}'"`

**After step execution (replaces Post-Step Cycle commit step):**
Merge the worktree branch back to main:
```bash
BRANCH="step-{N}"
git merge --squash "$BRANCH"
git commit -m "[feat] Step {N}: {step description}"
```
Then run Simplify + Tidy as normal (Post-Step Cycle steps 2-3).

**After simplify/tidy:** Cleanup the worktree:
```bash
git worktree remove .worktrees/step-{N} 2>/dev/null
git branch -d step-{N} 2>/dev/null
```

When `--worktree` is NOT set, the existing flow (direct execution + Post-Step Cycle) is unchanged.

#### Team Mode (`--team`)

Independent phases assigned to Builder teammates via Agent Teams. Each member works in an isolated worktree. `TeammateIdle` hook auto-assigns next tasks. Falls back to standard Task-based parallel if `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is not set. Post-Step Cycle runs in the orchestrator after each teammate reports completion.

#### Post-Step Cycle (MANDATORY — orchestrator executes directly)

After each step completes (Codex or Builder), YOU (the crew:go orchestrator) MUST run these Bash commands directly. Do NOT delegate. Do NOT skip.

**Step 1 — Commit:**
```bash
git status --porcelain
```
If output is non-empty:
```bash
git add -A
git commit -m "[feat] Step <N>: <step description from task_plan>"
```
If output is empty: skip (no changes).

**Step 2 — Simplify:**
Spawn `Agent(subagent_type="code-simplifier:code-simplifier")` on modified files.

**Step 3 — Tidy commit (only if Step 2 ran):**
```bash
git status --porcelain
```
If output is non-empty:
```bash
git add -A
git commit -m "[tidy] Simplify Step <N>"
```

**Step 4**: Proceed to next pending step.

### Stage 5: QA Loop
Invoke QA loop with max_cycles: 2, severity: major. Build → Review → Fix cycle until quality criteria met. Stall detection via issue hashing.

### Stage 6: Review (Parallel Validation)
Spawn 3 Reviewer agents in parallel:
- **Functional**: Verify spec.md requirements
- **Security**: Check OWASP Top 10
- **Quality**: Check maintainability

Aggregate verdicts. If any REJECTED, proceed to Fix (max 3 rounds).

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
  "config": { "skip_qa": false, "parallel_validation": true, "team_mode": false, "team_size": 2, "codex_mode": false, "max_iterations": 20 },
  "execution": { "current_step": "2.1", "tasks_completed": 3, "consecutive_failures": 0 },
  "signals": { "detected_signals": [] }
}
```

Stop hook (`hooks/scripts/auto_enforcer.py`) ensures persistence and auto-resume.

## Progress Display

```
/crew:go "Add logout button"

[1/9] Expanding...        done (spec.md created)
[2/9] Initializing...     done (already initialized)
[3/9] Planning...         done (2 phases, 5 steps)
[4/9] Executing...        done (5/5 steps complete)
[5/9] QA Loop...          done (build: pass, tests: pass)
[6/9] Reviewing...        done (parallel: 3/3 approved)
[7/9] Fixing...           done (2 auto-fixed)
[8/9] Checking...         done (compliant)
[9/9] Reflecting...       done

Workflow Complete

Summary:
  Requirements: 8 extracted
  Steps executed: 5
  Issues found: 3 (3 fixed)

---
SIGNAL: AUTO_COMPLETE
---
```

## Error Handling

On error, state is saved to `.caw/auto-state.json`.

**Resume options:**
- `/crew:go --continue` - Resume from saved state
- `/crew:dashboard` - Check current status

**Parallel Validation failure:** Auto-proceeds to Fix stage, retries up to 3 rounds.

## Boundaries

**Will:**
- Read task description, .caw/spec.md, .caw/task_plan.md
- Invoke Analyst, Bootstrapper, Planner, Builder, Reviewer (x3), Fixer, ComplianceChecker, Ralph Loop
- Update .caw/auto-state.json, .caw/task_plan.md, .caw/learnings.md
- Create .caw/spec.md, .caw/validation-results.json

**Won't:**
- Skip stages without explicit `--skip-*` flags
- Continue past 3 consecutive failures without user input
- Push to remote or create PRs automatically

## References

- [Signal Detection](../../_shared/signal-detection.md)
- [Parallel Validation](../../_shared/parallel-validation.md)
- [Auto State Schema](../../_shared/schemas/auto-state.schema.json)
