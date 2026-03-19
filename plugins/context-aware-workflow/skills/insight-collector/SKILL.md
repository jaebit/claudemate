---
name: insight-collector
description: Hybrid learning system that captures insights and automatically learns behavioral patterns from tool usage
user-invocable: false
allowed-tools: Read, Write, Glob, Bash
---

# Insight Collector

Hybrid learning system: manual insights + automatic pattern learning.

## System Overview

```
Manual Insights (★ blocks) → .caw/insights/
Automatic Instincts (patterns) → .caw/instincts/
Evolution (≥0.6 confidence) → .caw/evolved/
```

## Part 1: Manual Insight Capture

### Protocol

1. **Generate**: Display `★ Insight` block with 2-3 key points
2. **Save**: Immediately write to `.caw/insights/{YYYYMMDD}-{slug}.md`
3. **Confirm**: `💡 Insight saved: [title]`

### When to Generate

- Implementation discovery (useful patterns)
- Problem solution (lessons learned)
- Best practice (project-specific)
- Gotcha/Pitfall (traps to avoid)
- Architecture decision (design rationale)

## Part 2: Automatic Pattern Learning

### How It Works

```
Tool Usage → Observation (hooks/observe.py) → Pattern Detection → Instinct
```

### Detected Patterns

| Pattern | Example | Instinct |
|---------|---------|----------|
| Tool Sequence | Grep → Edit → Grep | "Verify with Grep after Edit" |
| Error Recovery | Edit fails → retry | "Adjust parameters on retry" |
| Tool Preference | 80% Grep over search | "Prefer Grep for code search" |
| Workflow | Same 3-tool sequence | "Standard modification workflow" |

### Confidence Scoring

| Evidence | Confidence |
|----------|------------|
| 1-2 obs | 0.3 |
| 3-5 obs | 0.5 |
| 6-10 obs | 0.7 |
| 11+ obs | 0.9 max |

Changes: Confirming +0.05, Contradicting -0.10, Weekly decay -0.02

### CLI Commands

```bash
python3 scripts/instinct-cli.py analyze [--incremental|--full]
python3 scripts/instinct-cli.py list|show|promote|demote|decay|stats
python3 scripts/instinct-cli.py export|import
python3 scripts/instinct-cli.py dashboard
```

## Part 3: Evolution

| Condition | Evolution |
|-----------|-----------|
| Confidence ≥0.6 | Eligible |
| User-triggered (3+ steps) | → Command |
| Auto-applicable | → Skill |
| Complex reasoning | → Agent |

Use `/cw:manage evolve` to preview and generate.

## Directory Structure

```
.caw/
├── insights/        # Manual (Part 1)
├── instincts/       # Automatic (Part 2)
│   ├── index.json
│   └── personal/
├── observations/    # Raw data
└── evolved/         # Part 3: commands/skills/agents
```

## Tag Generation

| Content Pattern | Tag |
|-----------------|-----|
| auth, jwt, login | #authentication |
| security, xss | #security |
| performance, cache | #performance |
| test, mock | #testing |
| api, endpoint | #api |

## Boundaries

**Will:** Save insights immediately, observe patterns, generate instincts, auto-tag
**Won't:** Modify content arbitrarily, overwrite without confirmation, auto-evolve low-confidence
