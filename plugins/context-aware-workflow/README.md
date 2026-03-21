# Context-Aware Workflow (cw)

Workflow orchestration plugin for Claude Code. Structured 9-stage pipeline from task planning to review, with complexity-adaptive agents and parallel execution.

## Installation

```bash
claude plugins add github:jaebit/claudemate
claude plugins install cw
```

## Quick Start

```bash
/cw:go "Implement JWT authentication"   # Full 9-stage pipeline
/cw:explore --arch "microservice auth"   # Architecture design
/cw:review --all                         # Unified code review
/cw:status                               # Progress + analytics
```

## Skills

| Skill | Description |
|-------|-------------|
| `/cw:go` | Full 9-stage pipeline (plan → build → review → fix) |
| `/cw:status` | Workflow progress, metrics, and cost analytics |
| `/cw:review` | Unified code review, QA, compliance, and auto-fix |
| `/cw:parallel` | Parallel execution via swarm or Agent Teams |
| `/cw:explore` | Discovery — brainstorm, architecture, research, debate |
| `/cw:manage` | Utilities — context, sync, worktree, tidy, init |

10 additional auto-triggered skills: progress-tracker, plan-detector, quality-gate, commit-discipline, insight-collector, pattern-learner, knowledge-engine, session-manager, learning-loop, structured-research.

## Agents

8 complexity-adaptive agents (adapt behavior internally via `_shared/complexity-hints.md`):

| Agent | Purpose |
|-------|---------|
| Planner | Task decomposition and planning |
| Builder | TDD implementation |
| Reviewer | Code quality and security review |
| Fixer | Auto-fix and remediation |
| Architect | System and UX design |
| Analyst | Requirements extraction |
| Bootstrapper | Environment initialization |
| ComplianceChecker | Rule and convention validation |

## Pipeline

```
[1/9] expansion → [2/9] init → [3/9] planning → [4/9] execution →
[5/9] qa → [6/9] review → [7/9] fix → [8/9] check → [9/9] reflect
```

## Artifacts

| File | Purpose |
|------|---------|
| `.caw/task_plan.md` | Current task plan |
| `.caw/context_manifest.json` | Active/Packed/Ignored file tracking |
| `.caw/session.json` | Current session state |
| `.caw/learnings.md` | Accumulated improvement insights |
| `.caw/archives/` | Completed/abandoned plans |

## License

MIT
