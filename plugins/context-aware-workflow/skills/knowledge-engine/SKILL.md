---
name: knowledge-engine
description: Centralized knowledge repository with ADR logging, review checklist generation, and project knowledge management
user-invocable: false
allowed-tools: Read, Write, Glob, Grep
---

# Knowledge Engine

Unified knowledge management combining project knowledge capture, architectural decision records (ADR), and context-aware review checklists.

## Triggers

### Knowledge Capture
1. Agent questions ("How does X work?") → search knowledge first
2. Session completion → auto-capture important findings
3. Explicit request ("Save this information")
4. Domain rules discovered during implementation

### Decision Recording
1. AskUserQuestion response contains decision
2. Architecture choice discussion completed
3. Trade-off analysis completed
4. Explicit request ("Record this decision")

### Review Checklist
1. /cw:review execution
2. Phase completion review
3. Pre-merge review

## Knowledge Categories

| Category | Description | Examples |
|----------|-------------|----------|
| domain/ | Business logic, rules | Order rules, pricing |
| technical/ | Implementation details | API methods, config |
| conventions/ | Project rules | Coding standards |
| gotchas/ | Pitfalls, cautions | Known bugs |
| decisions/ | ADRs | Architecture choices |

## Decision Record (ADR) Format

| Field | Value |
|-------|-------|
| **ID** | ADR-{NNN} |
| **Date** | YYYY-MM-DD |
| **Status** | Proposed / Accepted / Deprecated / Superseded |

Sections: Context, Options Considered, Decision, Rationale, Consequences

## Review Checklist Generation

Generates context-aware checklists from:
- `.caw/patterns/patterns.md` (code patterns)
- `.caw/decisions/*.md` (ADR compliance)
- `.caw/insights/*.md` (gotchas, best practices)
- `.caw/knowledge/` (domain rules)

Priority levels: Critical (security, ADR), Important (patterns, tests), Recommended (style, docs), Info (insights)

## Directory Structure

```
.caw/knowledge/
├── index.json
├── domain/
├── technical/
├── conventions/
├── gotchas/
└── integrations/

.caw/decisions/
├── index.md
├── ADR-001-*.md
└── ADR-002-*.md
```

## Agent Integration

| Agent | Usage |
|-------|-------|
| Planner | Check domain rules, record decisions |
| Builder | Search before implementation |
| Reviewer | Generate review checklist |
| Architect | Record architecture decisions |

## Boundaries

**Will:** Store knowledge, create ADRs, generate checklists, maintain indices
**Won't:** Make decisions, perform reviews, delete without confirmation, store credentials
