---
name: progress-tracker
user_invocable: false
description: Tracks workflow progress metrics including completion percentage, time spent, and step status
context: fork
agent: general-purpose
user-invocable: false
allowed-tools: Read, Write, Bash
---

# Progress Tracker

Track and visualize workflow progress with detailed metrics.

## Current Plan State

- **Task plan**: !`cat .caw/task_plan.md 2>/dev/null | head -20 || echo "(no task plan)"`
- **Metrics**: !`cat .caw/metrics.json 2>/dev/null | head -10 || echo "(no metrics yet)"`

## Forked Context Returns

```yaml
progress: Progress %
current: { phase: N, step: X.Y }
eta: Estimated completion time
visualization: Compact progress bar
```

## Event Hooks

| Event | Action |
|-------|--------|
| StepStarted | record_start |
| StepCompleted | record_completion |
| PhaseCompleted | generate_summary |

## Triggers

Activates on: step status changes, phase transitions, `/crew:dashboard`, periodic updates (10 min)

## Metrics Data (`.caw/metrics.json`)

```json
{
  "task_id": "auth-jwt",
  "started": "2026-01-04T10:00:00Z",
  "phases": {
    "phase_1": { "name": "Setup", "status": "completed", "steps": { "total": 3, "completed": 3 } },
    "phase_2": { "name": "Implementation", "status": "in_progress", "steps": { "total": 5, "completed": 2 } }
  },
  "totals": { "phases_total": 3, "steps_total": 11, "steps_completed": 5, "progress_percentage": 45.5 },
  "performance": { "avg_step_duration_minutes": 15, "quality_gate_pass_rate": 0.85 },
  "parallel_execution": { "enabled": true, "time_saved_minutes": 25, "speedup_factor": 2.0 },
  "worktrees": { "active": [...], "total_created": 4, "total_merged": 2 }
}
```

## Behavior

| Event | Updates |
|-------|---------|
| Step Start | Set `in_progress`, record timestamp, add timeline |
| Step Complete | Set `completed`, calculate duration, update totals, check phase |
| Phase Complete | Set phase `completed`, start next, update ETA |

## Progress Calculation

```python
# Overall: completed + (in_progress * 0.5)
effective = completed_steps + (in_progress * 0.5)
progress = (effective / total_steps) * 100

# ETA: avg_duration * remaining_steps
```

## Visualization

```
📊 Workflow Progress
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░ 45%

  ✅ Phase 1: Setup (3/3)         30m
  🔄 Phase 2: Implementation (2/5) 45m+
  ⏳ Phase 3: Testing (0/3)       --

Current: Step 2.3 | ETA: 14:00

Compact: [45%] Phase 2/3 | Step 5/11 | ETA: 14:00
```

## Parallel & Worktree Tracking

| Action | Updates |
|--------|---------|
| Batch Start | Record batch, log parallel IDs, increment totals |
| Batch Complete | Calculate time saved, update efficiency/speedup |
| Worktree Status | Scan `.worktrees/caw-step-*`, aggregate status |
| Post-Merge | Mark merged, combine timelines, recalculate progress |

```
Parallel Efficiency = (sequential_time / parallel_time) / max_concurrent
```

## Integration

- **`/crew:dashboard`**: Provides progress bar, phase/step breakdown, ETA
- **Session Persister**: Exports current_progress, phase, step, elapsed_time
- **Quality Gate**: Records pass/fail, updates retry stats

## Notifications

| Trigger | Message |
|---------|---------|
| Phase complete | 🎉 Phase {n} completed in {duration}! |
| 50% progress | 📊 Halfway there! |
| 90% progress | 🏁 Almost done! |
| Workflow complete | ✅ Completed in {total_duration}! |
| Step slow (2x avg) | ⏰ Step taking longer than usual |
| No progress (30m) | 📌 No progress in 30 minutes |

## Boundaries

**Will:** Track transitions, calculate metrics, estimate time, store performance data
**Won't:** Modify task_plan.md, make decisions, alert externally, store indefinitely
