---
description: "Pre-planning discovery - brainstorm, design, or research"
argument-hint: "<topic> [--arch|--ui|--research]"
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
| **Brainstorm** | (default) | Ideator | `.caw/brainstorm.md` |
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
| `--reset` | Start fresh, archive existing |

## Brainstorm Mode (Default)

Interactive Socratic dialogue via Ideator agent.

**Process:**

| Round | Focus | Sample Questions |
|-------|-------|------------------|
| 1 | Problem | "What types of notifications?" (Email/Push/In-app/SMS) |
| 2 | Scope | "What triggers? What volume?" (Low/Med/High) |
| 3 | Success | "How to measure success? Acceptable false positive rate?" |

**Output** (`.caw/brainstorm.md`):
- Problem Statement, Target Users
- Requirements (P0/P1/P2)
- Constraints, Open Questions
- Risks & Mitigations, Recommended Direction

## Architecture Design (`--arch`)

Creates `.caw/design/architecture.md`:
- System component diagrams
- Data models (ERD)
- API specifications
- Technical decision records
- Security considerations

## UX/UI Design (`--ui`)

Creates `.caw/design/ux-ui.md`:
- User flow diagrams
- ASCII wireframes
- Component specifications
- Interaction states
- Accessibility requirements

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

## Output

```
Explore Complete

Mode: Brainstorm
Created: .caw/brainstorm.md
Confidence: High

Summary:
- Problem: Real-time notification delivery
- Users: End users, admins
- Must Have: 5 requirements

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
- **Invokes**: Ideator, Architect, Planner agents
- **Uses**: AskUserQuestion, Serena, WebSearch, Context7
- **Successor**: `/cw:go`
