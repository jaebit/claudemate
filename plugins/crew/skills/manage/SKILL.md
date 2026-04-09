---
name: manage
user_invocable: false
description: "Workflow utilities - context, sync, worktree, tidy, and more"
argument-hint: "<subcommand> [options]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Agent, AskUserQuestion, Glob, Grep
---

# /crew:manage - Workflow Utilities

Manage workflow context, worktrees, synchronization, and improvement tools.

## Arguments

**Invoked as**: $ARGUMENTS

## Current State

- **Context manifest**: !`cat .caw/context_manifest.json 2>/dev/null | head -10 || echo "(no manifest)"`
- **Learnings**: !`cat .caw/learnings.md 2>/dev/null | head -5 || echo "(no learnings yet)"`

## Usage

```bash
/crew:manage context show|add|remove|pack|prune
/crew:manage sync [--to-serena|--from-serena]
/crew:manage merge [phase N] [--all] [--dry-run]
/crew:manage worktree create|list|clean
/crew:manage tidy [--scope <path>] [--apply]
/crew:manage init [--reset] [--deep]
/crew:manage evolve [--preview|--create <type>]
/crew:manage reflect [--task N.M] [--full]
```

## Subcommands

---

### context

Manage context files tracked by the workflow.

```bash
/crew:manage context show                    # Display current context
/crew:manage context add src/auth/*.ts       # Add files
/crew:manage context remove src/old.ts       # Remove files
/crew:manage context pack src/utils/         # Compress to interface-only
/crew:manage context prune                   # Remove stale files
/crew:manage context budget                  # Show token usage
```

**Context Tiers:**

| Tier | Description | Token Impact |
|------|-------------|--------------|
| **Active** | Files being modified | High (full content) |
| **Project** | Reference (read-only) | Medium |
| **Packed** | Interface summaries | Low |
| **Archived** | Stored but not loaded | None |

**Manifest**: `.caw/context_manifest.json`

---

### sync

Synchronize CAW workflow state with Serena memory for cross-session persistence.

```bash
/crew:manage sync                        # Bidirectional (default)
/crew:manage sync --to-serena            # Upload to Serena
/crew:manage sync --from-serena          # Restore from Serena
/crew:manage sync --status               # Check sync status
/crew:manage sync --force                # Overwrite without merge
/crew:manage sync --category domain_knowledge
```

**Memory Categories:**

| Category | CAW Source | Serena Memory |
|----------|------------|---------------|
| Domain Knowledge | `.caw/knowledge/**` | `domain_knowledge` |
| Lessons Learned | `.caw/learnings.md` | `lessons_learned` |
| Workflow Patterns | `.caw/knowledge/patterns.md` | `workflow_patterns` |
| Project Context | `context_manifest.json` | `project_onboarding` |
| Insights | `.caw/insights/**` | `caw_insights` |

**Behavior**: Bidirectional uses `newer_wins` strategy. Upload with `--to-serena`, restore with `--from-serena`.

---

### merge

Merge completed worktree branches back to main and synchronize task plan state.

```bash
/crew:manage merge                     # Auto-detect and merge completed
/crew:manage merge --all               # Merge all (dependency order)
/crew:manage merge phase 2             # Merge specific phase
/crew:manage merge phase 2,3           # Merge multiple phases
/crew:manage merge --dry-run           # Preview without executing
/crew:manage merge --abort             # Abort current merge
/crew:manage merge --continue          # Continue after conflict
```

**Workflow**: Scan worktrees → Check completion → Order by Phase Deps → Merge sequentially → Sync task_plan.md → Suggest cleanup.

**Conflict Handling:**

| Scenario | Action |
|----------|--------|
| Auto-resolvable | Resolved automatically |
| Manual required | Lists files, waits for resolution |
| After resolution | `git add <files>` then `/crew:manage merge --continue` |

---

### worktree

Manage git worktrees for parallel execution.

```bash
/crew:manage worktree create phase 2       # Create phase worktree
/crew:manage worktree create phase 2,3,4   # Multiple phases
/crew:manage worktree list                 # Show status
/crew:manage worktree clean                # Remove completed
/crew:manage worktree clean --all          # Remove all (confirmation required)
```

**Native Integration (v2.1+):**
- CLI: `claude -w <name>` creates `.claude/worktrees/<name>/`
- Builder agents use `isolation: worktree` for automatic isolation
- `WorktreeCreate` hook copies `.caw/` files to new worktrees

**Lifecycle**: CREATE → WORK → COMPLETE → MERGE → CLEAN

---

### tidy

Analyze and apply structural improvements following Kent Beck's Tidy First methodology.

```bash
/crew:manage tidy                    # Analyze current step target
/crew:manage tidy --scope src/auth/  # Specific directory
/crew:manage tidy --preview          # Show suggestions only
/crew:manage tidy --apply            # Apply changes
/crew:manage tidy --add-step         # Add tidy step to plan
/crew:manage tidy --commit           # Commit with [tidy] prefix
/crew:manage tidy --split            # Separate tidy/build commits
```

**Analysis Categories:**

| Category | Detection | Suggestions |
|----------|-----------|-------------|
| **Naming** | Single letters, abbreviations | Domain-specific, full words |
| **Duplication** | Identical blocks, similar patterns | Extract to shared function |
| **Dead Code** | Unused functions, unreachable code | Remove |
| **Structure** | Large functions, deep nesting | Extract methods, flatten |

**Serena Integration**: Uses `get_symbols_overview`, `find_referencing_symbols`, `rename_symbol`, `replace_symbol_body` for precise analysis.

---

### init

Initialize CAW environment without starting a task.

```bash
/crew:manage init                          # Basic initialization
/crew:manage init --reset                  # Force reset and reinitialize
/crew:manage init --type nodejs            # Hint project type
/crew:manage init --with-guidelines        # Generate GUIDELINES.md
/crew:manage init --deep                   # Generate hierarchical AGENTS.md files
/crew:manage init --serena-sync            # Save onboarding to Serena memory
/crew:manage init --from-serena            # Restore context from Serena
```

**Workflow**: Invoke Bootstrapper Agent → Create `.caw/` structure → Detect project → Generate `context_manifest.json`.

**Deep Init**: Creates `AGENTS.md` in each significant directory. Processes bottom-up. Preserves content below `<!-- MANUAL: -->` marker.

---

### evolve

Transform learned instincts into reusable commands, skills, or agents.

```bash
/crew:manage evolve                    # Interactive: preview and select
/crew:manage evolve --preview          # Preview candidates only
/crew:manage evolve --create command   # Create command from selected
/crew:manage evolve --create skill     # Create skill from selected
/crew:manage evolve --create agent     # Create agent from selected
/crew:manage evolve --id <instinct-id> # Evolve specific instinct
```

**Classification:**

| Pattern | Evolution Type |
|---------|---------------|
| User-triggered + 3+ steps | **Command** |
| Context-triggered + auto-apply | **Skill** |
| Complex reasoning + decision points | **Agent** |
| Simple preference | **None** (keep as instinct) |

**Output**: Generated to `.caw/evolved/{type}/{name}.md` with origin metadata.

**Threshold**: Confidence >= 0.6 required.

---

### reflect

Run Ralph Loop continuous improvement cycle after task completion.

```bash
/crew:manage reflect              # Reflect on last completed task
/crew:manage reflect --task 2.3   # Reflect on specific step
/crew:manage reflect --full       # Full workflow retrospective
/crew:manage reflect --no-memory  # Skip Serena memory creation
/crew:manage reflect --quiet      # Minimal output
```

**RALPH Phases:**

| Phase | Action |
|-------|--------|
| **R - Reflect** | Review task: outcome, duration, blockers, tools used |
| **A - Analyze** | Identify: what worked, what didn't, root causes, patterns |
| **L - Learn** | Extract: key insights, skills improved, knowledge gaps |
| **P - Plan** | Plan improvements with priority (High/Medium/Low) |
| **H - Habituate** | Apply: update learnings.md, checklists, Serena memories |

**Output**: Improvement score (0.0-1.0), insights saved to `.caw/learnings.md`.

---

## Boundaries

**Will:**
- Read `.caw/context_manifest.json`, `.caw/task_plan.md`, `.caw/learnings.md`
- Invoke Bootstrapper, Architect agents; Serena MCP tools
- Update `.caw/context_manifest.json`, `.caw/task_plan.md`, `.caw/learnings.md`

**Won't:**
- Delete files outside `.caw/` without confirmation
- Force-push or modify remote branches
- Overwrite Serena memories without `--force`
