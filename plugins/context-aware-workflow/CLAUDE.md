# Module Context

**Module:** Context-Aware Workflow (cw)
**Version:** 2.1.0
**Role:** Advanced agentic workflow orchestration with intelligent model routing.
**Tech Stack:** Python 3.x, Pytest, Markdown/YAML.

## Core Capabilities

- Plan Mode integration with automatic task plan generation
- Tiered agent variants (Haiku/Sonnet/Opus) with complexity-based routing
- Ralph Loop continuous improvement cycles
- QA loops (qaloop/ultraqa) for automated quality assurance
- Parallel execution via git worktrees
- HUD (Heads-Up Display) for real-time workflow metrics
- Eco mode for cost-optimized execution (30-50% savings)
- Background task heuristics for automatic async decisions
- Analytics system for token/cost analysis
- Delegation categories for improved agent routing
- Rate limit handling with automatic resume
- Swarm mode for parallel multi-agent execution
- Pipeline mode for explicit sequential stages
- Native worktree integration with Builder auto-isolation (v2.1)
- Agent Teams orchestration for collaborative parallel execution (v2.1)

---

# Operational Commands

```bash
# Run all tests
python -m pytest tests/

# Validate plugin structure
python tests/test_plugin_structure.py

# Workflow commands (in Claude Code)
# Core workflow
/cw:start      # Initialize workflow
/cw:status     # Check progress
/cw:next       # Execute next step
/cw:init       # Project initialization

# Execution modes
/cw:auto       # Autonomous workflow execution (supports --team, --debate)
/cw:loop       # Continuous iteration loop
/cw:swarm      # Parallel agent execution (fire-and-forget)
/cw:team       # Agent Teams orchestration (collaborative parallel)
/cw:pipeline   # Sequential stage execution

# Quality assurance
/cw:review     # Run code review
/cw:qaloop     # Review-Fix cycles
/cw:ultraqa    # Auto QA with diagnosis
/cw:check      # Run compliance checks
/cw:fix        # Apply fixes

# Planning & design
/cw:brainstorm # Ideation session
/cw:design     # UI/UX design workflow
/cw:research   # Research task

# Improvement & analysis
/cw:reflect    # Run Ralph Loop
/cw:evolve     # Self-improvement cycle
/cw:analytics  # Token/cost analysis

# Context & collaboration
/cw:context    # Manage context variables
/cw:sync       # Sync with external tools
/cw:merge      # Merge worktree results
/cw:worktree   # Git worktree management
/cw:tidy       # Cleanup resources

# Magic keywords
# eco/ecomode   - Cost-optimized execution
# deepwork      - Complete all tasks mode
# quickfix      - Minimal changes only
# async         - Force background execution
```

---

# Agent Inventory

## Tiered Agents (Complexity-Based Routing)

### Planner
Plans and structures tasks into executable steps.
- **Haiku** (`planner-haiku.md`): Simple tasks, single-file, quick fixes (complexity <= 0.3)
- **Sonnet** (`planner.md`): Standard development, multi-step features (0.3-0.7)
- **Opus** (`planner-opus.md`): Architecture design, security-critical planning (> 0.7)

### Builder
Implements code following TDD approach. All tiers use `isolation: worktree` for file conflict prevention.
- **Haiku** (`builder-haiku.md`): Boilerplate, simple CRUD, formatting (complexity <= 0.3)
- **Sonnet** (`builder.md`): Standard implementation, pattern-following (0.3-0.7)
- **Opus** (`builder-opus.md`): Complex algorithms, security-critical code (> 0.7)

### Reviewer
Reviews code for quality, bugs, and best practices.
- **Haiku** (`reviewer-haiku.md`): Quick style checks, linting issues (complexity <= 0.3)
- **Sonnet** (`reviewer.md`): Standard code review, quality gates (0.3-0.7)
- **Opus** (`reviewer-opus.md`): Security audits, architecture review, OWASP (> 0.7)

### Fixer
Applies fixes based on review feedback.
- **Haiku** (`fixer-haiku.md`): Auto-fix lint, imports, formatting (complexity <= 0.3)
- **Sonnet** (`fixer.md`): Multi-file refactoring, pattern extraction (0.3-0.7)
- **Opus** (`fixer-opus.md`): Security fixes, architectural refactoring (> 0.7)

## Specialized Agents (Single Tier)

- **Analyst** (`analyst.md`, Sonnet): Requirements extraction, task specification for auto workflow
- **Bootstrapper** (`bootstrapper.md`, Haiku): Environment initialization, project detection
- **Architect** (`architect.md`, Sonnet): System design, component architecture
- **Designer** (`designer.md`, Sonnet): UX/UI design, wireframes, user flows
- **Ideator** (`ideator.md`, Sonnet): Requirements discovery, Socratic dialogue
- **ComplianceChecker** (`compliance-checker.md`, Haiku): Guideline validation

---

# Skills Inventory

## Workflow Management
- **context-manager**: Workflow context variable management
- **progress-tracker**: Task progress tracking and reporting
- **session-persister**: Session state persistence across restarts
- **plan-detector**: Automatic plan detection from user input

## Quality & Review
- **quality-gate**: Quality checkpoint validation
- **review-assistant**: Code review assistance and feedback
- **commit-discipline**: Commit message and discipline enforcement
- **quick-fix**: Rapid fix suggestions

## Learning & Insights
- **insight-collector**: Collect insights from workflow execution
- **pattern-learner**: Learn patterns from codebase
- **knowledge-base**: Store and retrieve project knowledge
- **decision-logger**: Log architectural decisions

## Analysis & Monitoring
- **hud**: Real-time workflow metrics (HUD)
- **dashboard**: Workflow dashboard display
- **dependency-analyzer**: Dependency analysis

## Utilities
- **context-helper**: Context management helpers
- **reflect**: Self-reflection and improvement
- **evolve**: Self-evolution capabilities
- **research**: Research task execution
- **serena-sync**: Serena MCP synchronization

---

# Implementation Patterns

## Agent Definition (agents/*.md)

```yaml
---
name: agent-name                 # REQUIRED: lowercase-with-hyphens only (Claude Code spec)
description: "What the agent does"  # REQUIRED: when to delegate to this agent
model: sonnet                    # haiku, sonnet, opus, or inherit (default: inherit)
tools:                           # Optional: tools available to the agent
  - Read
  - Write
  - Glob
mcp_servers:                     # Optional: MCP servers (omit for haiku tier)
  - serena
skills: skill1, skill2           # Optional: skills to preload at startup
# Plugin Extensions (not in official Claude Code spec):
tier: sonnet                     # Extension: explicit complexity tier indicator
whenToUse: |                     # Extension: usage guidance with examples
  When to use this agent...
color: blue                      # Extension: UI display color
---
# Agent system prompt here
```

### Official vs Extension Fields

| Field | Official | Required | Notes |
|-------|:--------:|:--------:|-------|
| `name` | ✅ | **Yes** | lowercase-with-hyphens only |
| `description` | ✅ | **Yes** | Guides delegation decisions |
| `model` | ✅ | No | sonnet/opus/haiku/inherit |
| `tools` | ✅ | No | Inherits all if omitted |
| `mcp_servers` | ❌ | No | Plugin extension, optional for haiku |
| `skills` | ✅ | No | Preloaded at agent startup |
| `tier` | ❌ | No | Plugin extension for complexity indicator |
| `whenToUse` | ❌ | No | Plugin extension for selection guidance |
| `isolation` | ✅ | No | `worktree` for automatic worktree isolation |
| `color` | ❌ | No | Plugin extension for UI |

## Tiered Agent Naming Convention

- **Base tier (Sonnet)**: `<agent>.md` (e.g., `planner.md`, `builder.md`, `fixer.md`)
- **Fast tier (Haiku)**: `<agent>-haiku.md` (e.g., `planner-haiku.md`)
- **Complex tier (Opus)**: `<agent>-opus.md` (e.g., `planner-opus.md`, `builder-opus.md`)

All base agents use Sonnet model for balanced cost/capability.

## Skill Definition (skills/*/SKILL.md)

```yaml
---
name: skill-name
description: What the skill does
allowed-tools: Read, Glob, Grep
context: fork           # Runs in isolated context
---
# Skill behavior instructions
```

---

# Local Golden Rules

## Do's

- **DO** add tests in `tests/` for every new agent or skill.
- **DO** ensure YAML frontmatter is valid before committing.
- **DO** clear context variables when workflows finish.
- **DO** create tier variants when agents need different complexity handling.
- **DO** use Model Routing System for automatic tier selection.

## Don'ts

- **DON'T** rely on global state across agent executions.
- **DON'T** use complex logic in Markdown; delegate to Python scripts.
- **DON'T** hardcode model selection; use the routing system.

---

# Key Features

## HUD (Heads-Up Display)
Real-time workflow metrics during execution.
- Enable: `CAW_HUD=enabled`
- Location: `skills/hud/SKILL.md`

## Eco Mode
Cost-optimized execution (30-50% savings).
- Activation: Use `eco` or `ecomode` keyword
- Effects: Forces Haiku, skips optional phases

## Background Heuristics
Automatic async/foreground decision based on task patterns.
- Location: `_shared/background-heuristics.md`
- Patterns: lint, format, gemini → async; security, critical → foreground

## Analytics
Token/cost analysis and optimization insights.
- Command: `/cw:analytics`
- Schema: `schemas/metrics.schema.json`

## Swarm Mode
Parallel multi-agent execution.
- Command: `/cw:swarm "task1" "task2"`
- Location: `commands/swarm.md`

## Pipeline Mode
Explicit sequential stages with checkpoints.
- Command: `/cw:pipeline --stages "plan,build,review"`
- Location: `commands/pipeline.md`

## Delegation Categories
Category-based agent routing (research, implementation, review, design, maintenance).
- Location: `_shared/agent-resolver.md`

## Rate Limit Handling
Automatic wait-and-resume for rate limit errors.
- Location: `hooks/scripts/rate_limit_handler.py`

## Native Worktree Integration (v2.1)
Automatic worktree isolation for Builder agents.
- Builder agents have `isolation: worktree` for automatic file conflict prevention
- `WorktreeCreate` hook copies `.caw/` context files to new worktrees
- `WorktreeRemove` hook cleans up metadata
- CLI: `claude -w <name>` for manual worktree sessions
- Location: `hooks/scripts/worktree_setup.py`

## Agent Teams (v2.1)
Multi-session collaborative execution with inter-agent communication.
- Command: `/cw:team create <name> [--roles ...] [--size N]`
- Requires: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Features: Direct messaging (SendMessage), shared task list, quality gates
- Debate pattern: Reviewer cross-validation for high-stakes reviews
- Hooks: `TeammateIdle` (auto-assign), `TaskCompleted` (quality gate)
- Location: `commands/team.md`, `hooks/scripts/team_hooks.py`
- Schema: `_shared/schemas/team-state.schema.json`

---

# Context Map

- **[Agents](./agents/)** — 18 agents (4 tiered × 3 tiers + 6 specialized).
- **[Commands](./commands/)** — 25 slash commands for workflow control.
- **[Skills](./skills/)** — 20 composable skills for workflow capabilities.
- **[Hooks](./hooks/)** — Lifecycle hooks (SessionStart, Stop, PreToolUse, PostToolUse, SessionEnd, WorktreeCreate, WorktreeRemove, TeammateIdle, TaskCompleted).
- **[Schemas](./schemas/)** — JSON schemas (metrics, mode, model-routing, last_review).
- **[Shared Resources](./_shared/)** — Model routing, agent registry, templates, skill composition, background heuristics.
- **[Tests](./tests/)** — Plugin structure validation, unit tests.
