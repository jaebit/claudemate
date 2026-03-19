# Context-Aware Workflow (CAW)

Context-aware workflow orchestration plugin for Claude Code. Acts as a **Context-Aware Project Manager** that enforces structured workflows while collaborating interactively with developers.

## Philosophy

- **Hybrid Automation**: Combines natural language interface with rigorous programmatic logic
- **Human-in-the-Loop**: Propose → Review → Execute pattern
- **Plan Mode Integration**: Seamlessly imports existing Claude Code plans

## Installation

```bash
# Option 1: Use directly
claude --plugin-dir /path/to/context-aware-workflow

# Option 2: Copy to project
cp -r context-aware-workflow /your/project/.claude-plugin/
```

## Quick Start

```bash
# Run the full workflow end-to-end
/cw:go "Implement user authentication with JWT"

# Check current progress
/cw:status
```

## Skills Reference

| Skill | Description |
|-------|-------------|
| `/cw:go` | Run full 9-stage pipeline (plan → build → review → fix) |
| `/cw:status` | Display workflow progress, metrics, and cost analytics |
| `/cw:review` | Unified code review, QA, compliance checking, and auto-fix |
| `/cw:parallel` | Execute tasks in parallel using swarm or Agent Teams |
| `/cw:explore` | Pre-planning discovery — brainstorm, design, or research |
| `/cw:manage` | Workflow utilities — context, sync, worktree, tidy, and more |

## Agents

8 complexity-adaptive agents (no tier variants — agents adapt behavior internally via `_shared/complexity-hints.md`):

| Agent | ID | Purpose |
|-------|----|---------|
| Planner | `cw:planner` | Task decomposition and planning |
| Builder | `cw:builder` | TDD implementation |
| Reviewer | `cw:reviewer` | Code quality and security review |
| Fixer | `cw:fixer` | Auto-fix and remediation |
| Architect | `cw:architect` | System and UX design |
| Analyst | `cw:analyst` | Requirements extraction |
| Bootstrapper | `cw:bootstrapper` | Environment initialization |
| ComplianceChecker | `cw:compliance-checker` | Rule and convention validation |

See `_shared/agent-registry.md` for full details.

## Skills

16 skills (6 user-invocable + 10 auto-triggered):

| Skill | Purpose |
|-------|---------|
| go | Full 9-stage automated workflow pipeline |
| status | Workflow progress, metrics, and cost analytics |
| review | Unified code review, QA, compliance, and auto-fix |
| parallel | Parallel execution via swarm or Agent Teams |
| explore | Pre-planning discovery — brainstorm, design, research |
| manage | Workflow utilities — context, sync, worktree, tidy |
| progress-tracker | Tracks completion percentage and step status |
| plan-detector | Detects Plan Mode completion, suggests CAW workflow |
| quality-gate | Validates quality criteria before step completion |
| commit-discipline | Enforces Tidy First commit separation |
| insight-collector | Captures insights and learns behavioral patterns |
| pattern-learner | Learns project-specific code style and conventions |
| knowledge-engine | ADR logging and project knowledge management |
| session-manager | Session state, context prioritization, HUD metrics |
| learning-loop | Continuous improvement via reflection and memory sync |
| structured-research | 4-stage deep research: decompose → investigate → cross-validate → synthesize |

## Hooks

Defined in `hooks/hooks.json`:

| Event | Hook | Purpose |
|-------|------|---------|
| SessionStart | `rate_limit_handler.py` | Automatic rate limit handling |
| Stop | `auto_enforcer.py` | Post-session enforcement |
| PreToolUse (`*`) | `observe.py` | Insight collection observation |
| PreToolUse (`Edit\|Write`) | `check_plan_adherence.py` | Plan compliance check |
| PreToolUse (`Edit\|Write`) | `gemini_edit_review.py` | Gemini CLI edit review |
| PreToolUse (`Bash`) | `validate_commit_discipline.py` | Tidy First commit validation |
| PreToolUse (`Bash`) | `gemini_commit_review.py` | Gemini CLI commit review |
| PostToolUse (`*`) | `observe_and_hud.py` | HUD metrics and observation |
| SessionEnd | `session_end.py` | Session cleanup |

## Tidy First Methodology

Kent Beck's **Tidy First** methodology for code quality:

> "Never mix structural changes with behavioral changes in the same commit.
> When both are needed, always do structural changes first."

The `commit-discipline` skill enforces this via the `validate_commit_discipline.py` hook, blocking mixed commits automatically.

## Generated Artifacts

| File | Purpose |
|------|---------|
| `.caw/task_plan.md` | Current task plan |
| `.caw/context_manifest.json` | Active/Packed/Ignored file tracking |
| `.caw/session.json` | Current session state |
| `.caw/learnings.md` | Accumulated improvement insights |
| `.caw/archives/` | Completed/abandoned plans |

## License

MIT
