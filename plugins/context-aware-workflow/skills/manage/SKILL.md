---
name: manage
description: "Workflow utilities - context, sync, worktree, tidy, and more"
argument-hint: "<subcommand> [options]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Agent, AskUserQuestion, Glob, Grep
---

# /cw:manage - Workflow Utilities

Manage workflow context, worktrees, synchronization, and improvement tools.

## Arguments

**Invoked as**: $ARGUMENTS

## Current State

- **Context manifest**: !`cat .caw/context_manifest.json 2>/dev/null | head -10 || echo "(no manifest)"`
- **Learnings**: !`cat .caw/learnings.md 2>/dev/null | head -5 || echo "(no learnings yet)"`

## Usage

```bash
/cw:manage context show|add|remove|pack|prune
/cw:manage sync [--to-serena|--from-serena]
/cw:manage merge [phase N] [--all] [--dry-run]
/cw:manage worktree create|list|clean
/cw:manage tidy [--scope <path>] [--apply]
/cw:manage init [--reset] [--deep]
/cw:manage evolve [--preview|--create <type>]
/cw:manage reflect [--task N.M] [--full]
```

## Subcommands

---

### context

Manage context files tracked by the workflow.

```bash
/cw:manage context show                    # Display current context
/cw:manage context add src/auth/*.ts       # Add files
/cw:manage context remove src/old.ts       # Remove files
/cw:manage context pack src/utils/         # Compress to interface-only
/cw:manage context prune                   # Remove stale files
/cw:manage context budget                  # Show token usage
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
/cw:manage sync                        # Bidirectional (default)
/cw:manage sync --to-serena            # Upload to Serena
/cw:manage sync --from-serena          # Restore from Serena
/cw:manage sync --status               # Check sync status
/cw:manage sync --force                # Overwrite without merge
/cw:manage sync --category domain_knowledge
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
/cw:manage merge                     # Auto-detect and merge completed
/cw:manage merge --all               # Merge all (dependency order)
/cw:manage merge phase 2             # Merge specific phase
/cw:manage merge phase 2,3           # Merge multiple phases
/cw:manage merge --dry-run           # Preview without executing
/cw:manage merge --abort             # Abort current merge
/cw:manage merge --continue          # Continue after conflict
```

**Workflow**: Scan worktrees → Check completion → Order by Phase Deps → Merge sequentially → Sync task_plan.md → Suggest cleanup.

**Conflict Handling:**

| Scenario | Action |
|----------|--------|
| Auto-resolvable | Resolved automatically |
| Manual required | Lists files, waits for resolution |
| After resolution | `git add <files>` then `/cw:manage merge --continue` |

---

### worktree

Manage git worktrees for parallel execution.

```bash
/cw:manage worktree create phase 2       # Create phase worktree
/cw:manage worktree create phase 2,3,4   # Multiple phases
/cw:manage worktree list                 # Show status
/cw:manage worktree clean                # Remove completed
/cw:manage worktree clean --all          # Remove all (confirmation required)
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
/cw:manage tidy                    # Analyze current step target
/cw:manage tidy --scope src/auth/  # Specific directory
/cw:manage tidy --preview          # Show suggestions only
/cw:manage tidy --apply            # Apply changes
/cw:manage tidy --add-step         # Add tidy step to plan
/cw:manage tidy --commit           # Commit with [tidy] prefix
/cw:manage tidy --split            # Separate tidy/build commits
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
/cw:manage init                          # Basic initialization
/cw:manage init --reset                  # Force reset and reinitialize
/cw:manage init --type nodejs            # Hint project type
/cw:manage init --with-guidelines        # Generate GUIDELINES.md
/cw:manage init --deep                   # Generate hierarchical AGENTS.md files
/cw:manage init --serena-sync            # Save onboarding to Serena memory
/cw:manage init --from-serena            # Restore context from Serena
```

**Workflow**: Invoke Bootstrapper Agent → Create `.caw/` structure → Detect project → Generate `context_manifest.json`.

**Deep Init**: Creates `AGENTS.md` in each significant directory. Processes bottom-up. Preserves content below `<!-- MANUAL: -->` marker.

---

### evolve

Transform learned instincts into reusable commands, skills, or agents.

```bash
/cw:manage evolve                    # Interactive: preview and select
/cw:manage evolve --preview          # Preview candidates only
/cw:manage evolve --create command   # Create command from selected
/cw:manage evolve --create skill     # Create skill from selected
/cw:manage evolve --create agent     # Create agent from selected
/cw:manage evolve --id <instinct-id> # Evolve specific instinct
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
/cw:manage reflect              # Reflect on last completed task
/cw:manage reflect --task 2.3   # Reflect on specific step
/cw:manage reflect --full       # Full workflow retrospective
/cw:manage reflect --no-memory  # Skip Serena memory creation
/cw:manage reflect --quiet      # Minimal output
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
