# CW Plugin Migration Guide: v2.x → v3.0

## Overview

v3.0 consolidates the plugin from 171 files to ~90 files with an automation-first design.

| Metric | v2.1 | v3.0 | Change |
|---|---|---|---|
| Commands | 25 | 6 | -76% |
| Agents | 20 | 8 | -60% |
| Skills | 21 | 11 | -48% |
| Hook scripts | 13 | 10 | -23% |

---

## Command Migration

v2 commands remain as deprecation stubs through v3.0 and will be removed in v3.1.

### Primary Automation
```
/crew:auto "task"          →  /crew:go "task"
/crew:auto --team          →  /crew:go --team
/crew:auto --continue      →  /crew:go --continue
/crew:start "task"         →  /crew:go "task"
/crew:next                 →  /crew:go --continue
/crew:loop                 →  /crew:go --max-iterations N
/crew:pipeline             →  /crew:go --stages "plan,build,review"
```

### Quality Assurance
```
/crew:review               →  /crew:review (unchanged)
/crew:qaloop               →  /crew:review --loop
/crew:ultraqa              →  /crew:review --build
/crew:check                →  /crew:review --compliance
/crew:fix                  →  /crew:review --fix
```

### Parallel Execution
```
/crew:swarm "t1" "t2"      →  /crew:parallel "t1" "t2"
/crew:team create <name>   →  /crew:parallel --team create <name>
/crew:team assign          →  /crew:parallel --team assign
/crew:team status          →  /crew:parallel --team status
```

### Discovery & Planning
```
/crew:brainstorm           →  /crew:explore
/crew:design               →  /crew:explore --ui
/crew:research "topic"     →  /crew:explore --research "topic"
```

### Utilities
```
/crew:context add ...      →  /crew:manage context add ...
/crew:sync                 →  /crew:manage sync
/crew:merge                →  /crew:manage merge
/crew:worktree create ...  →  /crew:manage worktree create ...
/crew:tidy                 →  /crew:manage tidy
/crew:init                 →  /crew:manage init
/crew:evolve               →  /crew:manage evolve
/crew:reflect              →  /crew:manage reflect
/crew:analytics            →  /crew:dashboard (analytics integrated)
```

---

## Agent Changes

### Model Tier Variants Removed

All `-haiku`, `-sonnet`, `-opus` variants are removed. Each agent now self-assesses task complexity and adapts behavior internally. See `_shared/complexity-hints.md`.

**Deleted files**: `builder-haiku.md`, `builder-sonnet.md`, `builder-opus.md`, `planner-haiku.md`, `planner-opus.md`, `reviewer-haiku.md`, `reviewer-opus.md`, `fixer-haiku.md`, `fixer-sonnet.md`, `fixer-opus.md`

### Agent Mergers

- `designer.md` → absorbed into `architect.md` (UI/UX capabilities added)
- `ideator.md` → absorbed into `planner.md` (brainstorm mode)

### Model Routing Removed

`_shared/model-routing.md` and `schemas/model-routing.schema.json` are deleted. Replaced by `_shared/complexity-hints.md` which provides complexity assessment signals without attempting to control model selection.

---

## Skill Changes

### Merged Skills

| New Skill | Absorbs |
|---|---|
| `knowledge-engine` | knowledge-base + decision-logger + review-assistant |
| `session-manager` | session-persister + context-helper + hud + dashboard |
| `learning-loop` | reflect + evolve + research + serena-sync |

### Inlined Skills

- `quick-fix` → inlined into fixer agent
- `dependency-analyzer` → inlined into `_shared/parallel-execution.md`

---

## Hook Changes

- **Removed**: SessionStart echo banner (unnecessary noise)
- **Merged**: `observe.py post` + `update_hud.py` → `observe_and_hud.py`
- **Enhanced**: Gemini hooks now check for `gemini` CLI availability before running
- **Enhanced**: `check_plan_adherence.py` suggests `/crew:go` when no plan exists

---

## State File Compatibility

`.caw/` state files from v2.x are compatible with v3.0. No migration needed for:
- `task_plan.md`
- `auto-state.json`
- `loop_state.json`
- `learnings.md`
- `insights/`

---

## Timeline

- **v3.0**: Deprecation stubs active, v2 commands still work
- **v3.1**: Deprecation stubs removed, only 6 active commands remain
