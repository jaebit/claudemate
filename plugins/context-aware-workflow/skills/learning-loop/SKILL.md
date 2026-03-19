---
name: learning-loop
description: Continuous improvement through Ralph Loop reflection, instinct evolution, integrated research, and cross-session memory sync
context: fork
agent: general-purpose
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash, WebSearch, WebFetch
---

# Learning Loop

Combines Ralph Loop continuous improvement, instinct evolution, integrated research, and Serena memory synchronization. Cooperates with Claude Code's auto memory system.

## Current State

- **Learnings**: !`cat .caw/learnings.md 2>/dev/null | head -20 || echo "(no learnings yet)"`
- **Instincts**: !`cat .caw/instincts/index.json 2>/dev/null | head -10 || echo "(no instincts yet)"`
- **Serena sync**: !`python3 "${CLAUDE_SKILL_DIR}/../../../hooks/scripts/sync-check.sh" 2>/dev/null || echo "(sync check unavailable)"`

## MCP Servers

- `serena` — Semantic code analysis, symbol search, memory sync
- `context7` — Library documentation lookup

## Components

### Ralph Loop
REFLECT → ANALYZE → LEARN → PLAN → HABITUATE cycle.
- Reflect: Task summary, outcome, duration, blockers
- Analyze: What worked/didn't, root causes, patterns
- Learn: Key insights, skills improved, knowledge gaps
- Plan: Action items by priority, process changes
- Habituate: Update .caw/learnings.md, create Serena memories

### Instinct Evolution
Transform high-confidence instincts (>=0.6) into reusable components.
- Types: command (multi-step workflows), skill (auto-activated), agent (complex reasoning)
- Output: `.caw/evolved/{commands,skills,agents}/`
- State: `.caw/instincts/index.json`

### Integrated Research
Combines internal codebase analysis with external documentation research.
- Internal: Serena symbol search, pattern search, reference analysis
- External: WebSearch, WebFetch, Context7 library docs
- Synthesis: Compare current vs recommended, priority-ordered recommendations

### Memory Sync
Bidirectional sync between CAW workflow state and Serena memory.
- To Serena: knowledge, insights, learnings, lessons
- From Serena: domain_knowledge, workflow_patterns, session backup
- Conflict resolution: newer_wins (default), merge, manual

## Auto Memory Integration

Learning Loop cooperates with Claude Code's built-in auto memory:
- Writes significant learnings to project MEMORY.md (via Claude Code's system)
- Also maintains .caw/learnings.md for CW-specific state
- Does NOT create a parallel memory system - extends the existing one
- Agent prompts reference MEMORY.md as context source

## Usage

```bash
/cw:manage reflect              # Run Ralph Loop
/cw:manage reflect --full       # Full workflow retrospective
/cw:manage evolve               # Show evolution candidates
/cw:manage evolve --create      # Generate evolution
/cw:manage sync                 # Bidirectional Serena sync
/cw:manage sync --to-serena     # Upload to Serena
/cw:explore --research "topic"  # Integrated research
```

## Boundaries

**Will:** Run RALPH cycle, evolve instincts, research topics, sync memory
**Won't:** Evolve low-confidence (<0.6), auto-overwrite, delete memories without confirmation
