# Context-Aware Workflow (CAW)

Context-aware workflow orchestration plugin for Claude Code. Acts as a **Context-Aware Project Manager** that enforces structured workflows while collaborating interactively with developers.

## Philosophy

- **Hybrid Automation**: Combines natural language interface with rigorous programmatic logic
- **Human-in-the-Loop**: Propose → Review → Execute pattern
- **Context Engineering**: Active/Project/Archived tiered context management
- **Plan Mode Integration**: Seamlessly imports existing Claude Code plans

## Features

### v2.0.0 (Current)

- **Pipeline Mode** - Explicit sequential stages with `/cw:pipeline`
- **Analytics System** - Token/cost analysis with `/cw:analytics`
- **HUD (Heads-Up Display)** - Real-time workflow metrics during execution
- **Eco Mode** - Cost-optimized execution (30-50% savings) via `eco` keyword
- **Tiered Agents** - Complexity-based model routing (Haiku/Sonnet/Opus)
- **Background Heuristics** - Automatic async/foreground decision
- **Rate Limit Handling** - Automatic wait-and-resume for rate limits
- **Delegation Categories** - Category-based agent routing

### v1.9.0

- **GUIDELINES.md Generation** - Auto-generate workflow guidelines with `--with-guidelines`
- **Deep Initialization** - Hierarchical AGENTS.md generation with `--deep`
- **Enhanced /cw:init** - New flags for comprehensive project documentation setup

### v1.8.0

- **`/cw:qaloop`** - QA Loop: Build → Review → Fix cycle until quality gates pass
- **`/cw:ultraqa`** - Advanced auto QA with intelligent diagnosis (build/test/lint)
- **`/cw:research`** - Integrated research mode (internal codebase + external docs)
- **Enhanced Parallel Execution** - Automatic background agent parallel execution

### v1.7.0

- **Gemini CLI Review Integration** - Edit and commit review via Gemini CLI hooks
- Full workflow automation with `/cw:auto`
- Tidy First methodology with `/cw:tidy` command
- Serena MCP memory synchronization

## Installation

```bash
# Option 1: Use directly
claude --plugin-dir /path/to/context-aware-workflow

# Option 2: Copy to project
cp -r context-aware-workflow /your/project/.claude-plugin/
```

## Quick Start

```bash
# Initialize and start a new workflow
/cw:start "Implement user authentication with JWT"

# Or run full workflow automatically
/cw:auto "Add a logout button to the header"
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `/cw:auto` | **Run full workflow automatically** - init → start → next → review → fix → check |
| `/cw:init` | Initialize CAW environment (creates `.caw/` directory) |
| `/cw:start` | Start a new workflow with task description or import Plan Mode plans |
| `/cw:status` | Display current workflow status with visual progress bar |
| `/cw:next` | Execute the next pending step from task plan (supports auto-parallel execution) |
| `/cw:review` | Run code review with configurable depth (--haiku/--sonnet/--opus) |
| `/cw:fix` | Apply fixes from review results (auto-fix or manual) |
| `/cw:tidy` | Analyze and apply structural improvements (Tidy First methodology) |
| `/cw:check` | Validate compliance with project rules and conventions |
| `/cw:context` | Manage context files (add, remove, pack, view) |
| `/cw:brainstorm` | Interactive requirements discovery through Socratic dialogue |
| `/cw:design` | Create UX/UI or architecture design documents |
| `/cw:sync` | Synchronize CAW state with Serena memory (cross-session persistence) |
| `/cw:qaloop` | **QA Loop** - Build → Review → Fix cycle until quality passes |
| `/cw:ultraqa` | **UltraQA** - Intelligent auto QA for build/test/lint issues |
| `/cw:research` | **Research Mode** - Internal codebase + external docs research |
| `/cw:pipeline` | **Pipeline Mode** - Sequential stages with checkpoints (NEW) |
| `/cw:analytics` | **Analytics** - Token/cost analysis and optimization insights (NEW) |
| `/cw:evolve` | **Evolve** - Self-improvement and evolution cycle (NEW) |

## Enhanced Initialization (v1.9.0)

### GUIDELINES.md Generation

Generate workflow guidelines customized to your project:

```bash
/cw:init --with-guidelines
```

Creates `.caw/GUIDELINES.md` with:
- CAW workflow rules and best practices
- Agent usage recommendations
- Model routing guidance
- Project-specific context (frameworks, conventions)
- Quality gate criteria

### Deep Initialization (AGENTS.md Hierarchy)

Generate hierarchical documentation for AI agents:

```bash
/cw:init --deep
```

Creates `AGENTS.md` in each significant directory:
```
project/
├── AGENTS.md                    # Root overview
├── src/
│   ├── AGENTS.md               # <!-- Parent: ../AGENTS.md -->
│   ├── components/
│   │   └── AGENTS.md           # <!-- Parent: ../AGENTS.md -->
│   └── utils/
│       └── AGENTS.md           # <!-- Parent: ../AGENTS.md -->
└── tests/
    └── AGENTS.md               # <!-- Parent: ../AGENTS.md -->
```

Each AGENTS.md contains:
- Directory purpose
- Key files with descriptions
- Subdirectory links
- AI agent instructions
- Internal/external dependencies

### Full Setup

```bash
# Initialize with all documentation
/cw:init --with-guidelines --deep

# Or reset and regenerate
/cw:init --reset --with-guidelines --deep
```

## Workflow Loop

1. **Bootstrap**: Bootstrapper initializes `.caw/` environment (auto on first run)
2. **Discovery**: Planner Agent asks clarifying questions
3. **Planning**: Generates `task_plan.md` in `.caw/`
4. **Execution**: Code with plan-aware hooks (warnings if no plan exists)
5. **Review**: Manual review of implementation

## Auto Mode (`/cw:auto`)

For end-to-end feature development:

```bash
/cw:auto "Add a logout button to the header"
```

### Workflow Stages

```
[1/6] init     → Initialize .caw/ if needed
[2/6] start    → Generate task plan (minimal questions)
[3/6] next     → Execute all steps
[4/6] review   → Code review
[5/6] fix      → Auto-fix issues
[6/6] check    → Compliance validation
```

## Generated Artifacts

| File | Purpose |
|------|---------|
| `.caw/task_plan.md` | Current task plan |
| `.caw/context_manifest.json` | Active/Packed/Ignored file tracking |
| `.caw/GUIDELINES.md` | Workflow guidelines (`--with-guidelines`) (NEW) |
| `.caw/mode.json` | Active mode state (DEEP_WORK, NORMAL, etc.) |
| `.caw/session.json` | Current session state |
| `.caw/learnings.md` | Accumulated improvement insights |
| `.caw/archives/` | Completed/abandoned plans |
| `*/AGENTS.md` | Directory documentation (`--deep`) (NEW) |

## Model Routing System

CAW automatically selects the optimal model tier based on task complexity:

| Complexity | Tier | Use Case |
|------------|------|----------|
| ≤ 0.3 | Haiku | Fast, simple tasks, boilerplate |
| 0.3 - 0.7 | Sonnet | Standard development, TDD |
| > 0.7 | Opus | Architecture, security audits |

### User Overrides

```bash
/cw:review --haiku     # Quick review
/cw:review --sonnet    # Standard review
/cw:review --security  # Auto-selects Opus
```

## Hooks

### PreToolUse Hooks

**Edit/Write tools**:
1. Plan Adherence Check - Verify plan compliance
2. Gemini Edit Review - Review edits via Gemini CLI (NEW)

**Bash tool (git commit)**:
1. Tidy First Commit Validation - Block mixed structural/behavioral changes
2. Gemini Commit Review - Review commit via Gemini CLI (NEW)

## Magic Keywords

Activate special modes by including keywords in your prompt:

| Keyword | Mode | Behavior |
|---------|------|----------|
| `deepwork`, `fullwork`, `ultrawork` | DEEP WORK | Complete ALL tasks without stopping |
| `thinkhard`, `ultrathink` | DEEP ANALYSIS | Extended reasoning, validate before acting |
| `quickfix`, `quick`, `fast` | MINIMAL CHANGE | Essential changes only, speed priority |
| `research`, `investigate` | RESEARCH | Comprehensive information gathering first |
| `eco`, `ecomode` | ECO MODE | Cost-optimized execution, forces Haiku tier |
| `async` | ASYNC | Force background execution |

## Pipeline Mode (`/cw:pipeline`)

Define explicit sequential stages with checkpoints:

```bash
/cw:pipeline --stages "plan,build,review,deploy"
```

Supports stage dependencies, rollback on failure, and progress checkpoints.

## Analytics (`/cw:analytics`)

View token usage and cost analysis:

```bash
/cw:analytics              # Current session
/cw:analytics --history    # Historical trends
```

## HUD (Heads-Up Display)

Real-time workflow metrics during execution:

- Enable: Set `CAW_HUD=enabled` environment variable
- Displays: Current step, progress, token usage, estimated cost

## Tidy First Methodology

Kent Beck's **Tidy First** methodology for code quality:

> "Never mix structural changes with behavioral changes in the same commit.
> When both are needed, always do structural changes first."

### Step Types

| Icon | Type | Description | Commit Prefix |
|------|------|-------------|---------------|
| 🧹 | Tidy | Structural change (no behavior change) | `[tidy]` |
| 🔨 | Build | Behavioral change (new feature, bug fix) | `[feat]`, `[fix]` |

### Usage

```bash
/cw:tidy                  # Analyze current step target
/cw:tidy --scope src/     # Analyze specific directory
/cw:tidy --apply          # Apply changes
/cw:tidy --add-step       # Add Tidy step to plan
```

## Schema Reference

| Schema | Location | Purpose |
|--------|----------|---------|
| `mode.schema.json` | `schemas/` | Mode state tracking |
| `model-routing.schema.json` | `schemas/` | Model tier selection |
| `last_review.schema.json` | `schemas/` | Reviewer output format |
| `metrics.schema.json` | `schemas/` | Analytics metrics format |
| `task-plan.schema.md` | `_shared/schemas/` | Task plan document format |

## Roadmap

### Completed (v2.0.0)
- [x] **Pipeline Mode** - Sequential stages with `/cw:pipeline`
- [x] **Analytics System** - Token/cost analysis with `/cw:analytics`
- [x] **HUD** - Real-time workflow metrics during execution
- [x] **Eco Mode** - Cost-optimized execution (30-50% savings)
- [x] **Tiered Agents** - Full Haiku/Sonnet/Opus variants for all core agents
- [x] **Background Heuristics** - Automatic async/foreground decisions
- [x] **Rate Limit Handling** - Automatic wait-and-resume
- [x] **Delegation Categories** - Category-based agent routing

### Completed (v1.9.0)
- [x] **GUIDELINES.md Generation** - Workflow guidelines with `--with-guidelines` flag
- [x] **Deep Initialization** - Hierarchical AGENTS.md with `--deep` flag
- [x] Template system for generated documentation
- [x] Incremental updates and manual content preservation

### Completed (v1.8.0)
- [x] **`/cw:qaloop`** - QA Loop: Build → Review → Fix cycle until quality passes
- [x] **`/cw:ultraqa`** - UltraQA: Intelligent auto QA for build/test/lint
- [x] **`/cw:research`** - Integrated research mode (internal + external)
- [x] Enhanced parallel execution with automatic background agents

### Completed (v1.7.0)
- [x] Gemini CLI integration for edit and commit review hooks

### Completed (v1.6.0)
- [x] Tidy First methodology with `/cw:tidy` command
- [x] `/cw:sync` for Serena MCP memory synchronization
- [x] PreToolUse hook for automatic Tidy First commit validation

### Completed (v1.5.0)
- [x] Learnings persistence (`.caw/learnings.md`, Serena memories)

### Completed (v1.4.0)
- [x] Model Routing System with complexity-based tier selection
- [x] Tiered Agent variants (Haiku, Sonnet, Opus)
- [x] `/cw:auto` command for full workflow automation

### Planned
- [ ] VS Code extension integration
- [ ] GitHub Actions integration
- [ ] Multi-project support

## License

MIT
