---
description: "Pre-planning discovery - brainstorm, design, or research"
argument-hint: "<topic> [--arch|--ui|--research|--debate]"
---

# /cw:explore - Discovery & Design

Pre-planning discovery combining brainstorming, architecture design, and research.

## Usage

```bash
# Brainstorm mode (default) - Socratic dialogue, ideation
/cw:explore "notification system"
/cw:explore "notification system" --reset

# Architecture design
/cw:explore --arch "microservice auth"
/cw:explore --ui "dashboard redesign"
/cw:explore --arch --ui "full-stack feature"

# Multi-model debate (requires multi-model-debate plugin)
/cw:explore --debate "REST vs GraphQL for our API"
/cw:explore --arch --debate "microservice auth"

# Research mode
/cw:explore --research "JWT authentication best practices"
/cw:explore --research "React Server Components" --external
/cw:explore --research "how is auth handled" --internal
/cw:explore --research "database pooling" --depth deep
/cw:explore --research "GraphQL" --gemini
```

## Modes

| Mode | Flag | Agent | Output |
|------|------|-------|--------|
| **Brainstorm** | (default) | Planner (brainstorm) | `.caw/brainstorm.md` |
| **Architecture** | `--arch` | Architect | `.caw/design/architecture.md` |
| **UX/UI Design** | `--ui` | Architect (UI focus) | `.caw/design/ux-ui.md` |
| **Research** | `--research` | Planner / Explore | `.caw/research/<topic>.md` |

## Flags

| Flag | Description |
|------|-------------|
| `--arch` | Architecture design mode |
| `--ui` | UX/UI design mode |
| `--research` | Research mode (internal + external) |
| `--internal` | Research: codebase analysis only |
| `--external` | Research: documentation only |
| `--depth` | Research depth: `shallow`, `normal`, `deep` |
| `--gemini` | Research: use Gemini for search grounding |
| `--save <name>` | Save research for later reference |
| `--load <name>` | Load previous research |
| `--debate` | Use multi-model debate for approach evaluation (requires `multi-model-debate` plugin) |
| `--reset` | Start fresh, archive existing |

## Brainstorm Mode (Default)

Interactive Socratic dialogue via Planner agent (brainstorm mode).

**Interaction Rules:**
- One question at a time (prefer multiple-choice)
- 2-3 approach alternatives before recommending
- Section-by-section user approval

**Process:**

```
[1] Clarifying Questions (one at a time, 3-5 rounds)
[2] Approach Exploration:
    - Default: Planner proposes 2-3 alternatives with trade-offs
    - --debate: Invoke /debate:start with topic, feed report into design
[3] Incremental Design (section-by-section approval)
[4] Write .caw/brainstorm.md
[5] Spec Review Loop (subagent, max 3 iterations)
[6] User Review Gate (approve or request changes)
```

See `_shared/spec-review.md` for review loop protocol.

**Output** (`.caw/brainstorm.md`):
- Problem Statement, Target Users
- Requirements (P0/P1/P2)
- Constraints, Risks & Mitigations
- Approaches Considered (2-3 with trade-offs)
- Recommended Direction, Review Status

## Architecture Design (`--arch`)

Creates `.caw/design/architecture.md` via Architect agent with section-by-section approval:
- System component diagrams
- Data models (ERD)
- API specifications
- Technical decision records (2-3 alternatives each)
- Security considerations
- Spec review loop + user approval gate

With `--debate`: Technology and architecture decisions are evaluated via `/debate:start` before the Architect commits to a direction. Debate report is saved to `.debate/` and referenced in the architecture document's Technical Decisions section.

## UX/UI Design (`--ui`)

Creates `.caw/design/ux-ui.md` via Architect agent with section-by-section approval:
- User flow diagrams
- ASCII wireframes
- Component specifications
- Interaction states
- Accessibility requirements
- Spec review loop + user approval gate

With `--debate`: UX approach decisions (e.g. SPA vs MPA, component library choice) are evaluated via `/debate:start` before the Architect commits.

## Research Mode (`--research`)

Combines internal codebase analysis (Serena, Grep/Glob) with external documentation (WebSearch, Context7).

### Research Depth

| Level | Internal | External | Output |
|-------|----------|----------|--------|
| **shallow** | Keyword matches, file list | Top 3-5 results | Brief summary |
| **normal** | Symbol search, 1-level refs | Top 10 results, examples | Detailed report |
| **deep** | Full symbol graph, architecture mapping | Exhaustive search, cross-reference | Comprehensive document |

### Execution Flow

```
Query Analysis → Internal Research (symbols, context, patterns)
             → External Research (search, docs, Context7)
             → Synthesis (organize, compare, recommend)
```

### Agent Selection

| Mode | Standard | Deep (--depth deep) |
|------|----------|---------------------|
| Internal | Task(Explore) Haiku | cw:planner-opus |
| Synthesis | cw:Planner Sonnet | cw:planner-opus |

### Persistence

```bash
/cw:explore --research "GraphQL" --save graphql-schema
/cw:explore --research "GraphQL" --load graphql-schema
```

## Debate Integration (`--debate`)

Requires the `multi-model-debate` plugin. If not installed, warns and falls back to single-agent evaluation.

**Prerequisite check:**
1. Verify `/debate:start` command is available
2. If missing: warn "multi-model-debate plugin not found, falling back to single-agent evaluation"

**When `--debate` is active:**
- Step [2] of brainstorm invokes `/debate:start "<topic>"` instead of single-agent comparison
- Step [4] of `--arch`/`--ui` invokes `/debate:start` for contested technical decisions
- Debate report (`.debate/<id>/report.md`) is referenced in the output document's "Approaches Considered" or "Technical Decisions" section

**Combinable with all modes:**

```bash
/cw:explore --debate "notification system"          # brainstorm + debate
/cw:explore --arch --debate "microservice auth"     # architecture + debate
/cw:explore --arch --ui --debate "full-stack app"   # both + debate
```

## Output

```
Explore Complete

Mode: Brainstorm
Created: .caw/brainstorm.md
Debate: .debate/20260315-143022-notification-system/report.md
Spec Review: ✅ Approved (2 iterations)
User Approval: ✅ Approved

Summary:
- Problem: Real-time notification delivery
- Users: End users, admins
- Must Have: 5 requirements
- Approaches: 3 debated (Claude/Codex/Gemini), WebSocket consensus

Next: /cw:explore --arch | /cw:explore --ui | /cw:go
```

## Directory Structure

```
.caw/
├── brainstorm.md
├── design/
│   ├── ux-ui.md
│   └── architecture.md
└── research/
    └── <topic>.md
```

## Integration

- **Creates**: `.caw/brainstorm.md`, `.caw/design/*.md`, `.caw/research/*.md`
- **Invokes**: Planner (brainstorm mode), Architect, Explore agents
- **Optionally invokes**: `/debate:start` (when `--debate` flag, requires `multi-model-debate` plugin)
- **Uses**: AskUserQuestion, Serena, WebSearch, Context7
- **References**: `_shared/spec-review.md` (review loop protocol)
- **Successor**: `/cw:go`
