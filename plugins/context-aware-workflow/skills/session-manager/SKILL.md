---
name: session-manager
description: Unified session state management, context prioritization, HUD metrics, and analytics dashboard
allowed-tools: Read, Write, Glob, Grep, Bash
---

# Session Manager

Combines session persistence, intelligent context management, real-time HUD metrics, and analytics dashboard.

## Components

### Session Persistence
- Save/restore workflow state across sessions
- State file: `.caw/session.json`
- Fields: session_id, workflow, progress, context, metrics
- Recovery: recent (<24h) → offer restore, old → fresh start

### Context Management
- Intelligent context prioritization for agents
- Context tiers: Active (modifying), Project (reference), Packed (interface-only), Archived
- Priority scoring: direct_reference (1.0), dependency_output (0.8), same_directory (0.6), pattern_match (0.4)
- Memory optimization: completed steps → summarize, large files → extract relevant sections

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
5. **Explicit request**: /cw:status, /cw:manage context

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
