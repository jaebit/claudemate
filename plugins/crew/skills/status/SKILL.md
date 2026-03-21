---
name: status
description: "Display workflow progress, metrics, and cost analytics"
argument-hint: "[--verbose] [--cost] [--tokens] [--all]"
disable-model-invocation: true
allowed-tools: Read, Bash
---

# /crew:status - Workflow Status & Analytics

Display current workflow state, progress, and cost/token analytics.

## Arguments

**Invoked as**: $ARGUMENTS

## Current State

- **Task plan**: !`cat .caw/task_plan.md 2>/dev/null | head -20 || echo "(no task plan)"`
- **Metrics**: !`cat .caw/metrics.json 2>/dev/null | head -10 || echo "(no metrics yet)"`
- **Mode**: !`cat .caw/mode.json 2>/dev/null || echo "(default mode)"`

## Usage

```bash
/crew:status             # Standard status
/crew:status --verbose   # Detailed with file lists
/crew:status --cost      # Cost breakdown by model tier
/crew:status --tokens    # Token usage analysis
/crew:status --sessions  # Multi-session comparison
/crew:status --worktrees # Show active worktree status
/crew:status --agents    # Show background agent status
/crew:status --export    # Export metrics to JSON
/crew:status --all       # Everything
```

## Flags

| Flag | Description |
|------|-------------|
| `--verbose` | Context files and recent activity |
| `--cost` | Cost breakdown: current, weekly, monthly, top drivers |
| `--tokens` | Token analysis: I/O ratio, category breakdown, tips |
| `--sessions` | Compare last 5 sessions: tokens, cost, steps |
| `--worktrees` | Active worktree status and progress |
| `--agents` | Background agent status and duration |
| `--export` | Export to `.caw/analytics_export_[date].json` |
| `--all` | All of the above |

## Behavior

### Step 1: Check Task Plan
Look for `.caw/task_plan.md`. Show help if not found.

### Step 2: Parse & Calculate Progress
```
progress_percent = (completed / total) * 100
progress_bar = "█" * filled + "░" * empty
```

### Step 3: Check Active Mode
Read `.caw/mode.json` for DEEP_WORK or NORMAL mode.

### Step 4: Display Status

**Standard Output:**
```
Workflow Status

Task: [Title]
Status: [status]
Mode: [DEEP WORK | NORMAL]

Phase [N]: [Phase Name]
|- [N.1] [Step]    Complete
|- [N.2] [Step]    In Progress  <- current
|- [N.3] [Step]    Pending

Progress: [X]% ([completed]/[total])
```

## Analytics (--cost, --tokens)

```
WORKFLOW ANALYTICS
Session: abc123 | Duration: 1h 30m

TOKEN USAGE
  Input: 45,000 (79%) | Output: 12,000 (21%) | Total: 57,000

COST BREAKDOWN
  Haiku: 15K/$0.02 (4%) | Sonnet: 35K/$0.15 (29%) | Opus: 7K/$0.35 (67%)
  TOTAL: $0.52

OPTIMIZATION INSIGHTS
  Opus 13% of tokens drove 67% of cost
  Eco mode would save ~$0.18 (35%)
```

## Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| Done | Complete | Finished |
| Working | In Progress | Working |
| Pending | Pending | Not started |
| Blocked | Blocked | Cannot proceed |
| Skipped | Skipped | Bypassed |

## Current Step Detection
1. First In Progress step
2. If none, first Pending step
3. If all complete, show completion message

## Worktrees (--worktrees)
Shows phase-based and step-based worktrees with branch, directory, status, and progress.

## Agents (--agents)
Shows background agents with task ID, step, status, duration.

## Edge Cases

- **All Complete**: Shows success message with suggested actions
- **All Blocked**: Lists blocked steps with resolution hints

## Boundaries

**Will:**
- Read `.caw/task_plan.md`, `.caw/metrics.json`, `.caw/sessions/*.json`, `.caw/mode.json`
- Write `.caw/analytics_export_*.json` (with --export)
- Use `dependency-analyzer` for parallel opportunities

**Won't:**
- Modify task plan or workflow state
- Invoke other commands or agents
