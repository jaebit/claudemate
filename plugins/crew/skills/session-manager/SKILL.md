---
name: session-manager
user_invocable: false
description: Unified session state management, context prioritization, HUD metrics, and analytics dashboard
user-invocable: false
allowed-tools: Read, Write, Glob, Grep, Bash
---

# Session Manager

Combines session persistence, subagent context curation, real-time HUD metrics, and analytics dashboard.

## Scope Note (post-1M context)

With the primary model's 1M context window, this skill is **not** in the business of compressing the main conversation to survive token limits. Its two load-bearing jobs are:

- **Durable session handoff**: persist enough state between sessions that `/crew:go --continue` or `/crew:dashboard` can resume cleanly the next day.
- **Subagent context curation**: decide which files and summaries to pass to each spawned Agent — subagents still run with smaller contexts than the main executor, so prioritization matters there even when it no longer matters for the main thread.

The HUD and dashboard components are independent and unaffected by the context-window shift.

## Current Session

- **Session state**: !`cat .caw/session.json 2>/dev/null | head -15 || echo "(no active session)"`

## Components

### Session Persistence
- Save/restore workflow state across sessions
- State file: `.caw/session.json`
- Fields: session_id, workflow, progress, context, metrics
- Recovery: recent (<24h) → offer restore, old → fresh start

### Subagent Context Curation
- Picks which files each spawned Agent sees; the main executor's 1M context is not the bottleneck here — subagent context budgets are.
- Context tiers: Active (modifying), Project (reference), Packed (interface-only), Archived
- Priority scoring: direct_reference (1.0), dependency_output (0.8), same_directory (0.6), pattern_match (0.4)
- For subagent dispatch: completed steps → summarize, large files → extract relevant sections. The main conversation keeps full fidelity.

### HUD Metrics
- Real-time progress display during execution
- Display: Phase/Step progress, tokens, cost, model, mode, elapsed time
- Modes: full, minimal, disabled (CAW_HUD env var)
- Cost calculation with model pricing

### Dashboard
- HTML analytics dashboard generation
- Stats: observations, instincts, evolutions, confidence
- Tool usage heatmap, instinct registry, evolution timeline

## Triggers

1. **SessionStart**: Check for existing session, offer restore
2. **Step/Phase completion**: Auto-save session, update metrics
3. **Agent starts step**: Provide prioritized context
4. **PostToolUse**: Update HUD metrics
5. **Explicit request**: /crew:dashboard, /crew:manage context

## State Files

| File | Content |
|------|---------|
| `.caw/session.json` | Session state, progress |
| `.caw/hud.json` | HUD metrics |
| `.caw/metrics.json` | Token/cost analytics |
| `.caw/context_manifest.json` | File context registry |
| `.caw/dashboard.html` | Generated dashboard |

## Boundaries

**Will:** Save/restore sessions, prioritize context, track metrics, generate dashboards
**Won't:** Save credentials, auto-restore without confirmation, keep >30 days
