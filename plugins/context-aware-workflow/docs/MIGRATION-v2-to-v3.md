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
/cw:auto "task"          →  /cw:go "task"
/cw:auto --team          →  /cw:go --team
/cw:auto --continue      →  /cw:go --continue
/cw:start "task"         →  /cw:go "task"
/cw:next                 →  /cw:go --continue
/cw:loop                 →  /cw:go --max-iterations N
/cw:pipeline             →  /cw:go --stages "plan,build,review"
```

### Quality Assurance
```
/cw:review               →  /cw:review (unchanged)
/cw:qaloop               →  /cw:review --loop
/cw:ultraqa              →  /cw:review --build
/cw:check                →  /cw:review --compliance
/cw:fix                  →  /cw:review --fix
```

### Parallel Execution
```
/cw:swarm "t1" "t2"      →  /cw:parallel "t1" "t2"
/cw:team create <name>   →  /cw:parallel --team create <name>
/cw:team assign          →  /cw:parallel --team assign
/cw:team status          →  /cw:parallel --team status
```

### Discovery & Planning
```
/cw:brainstorm           →  /cw:explore
/cw:design               →  /cw:explore --ui
/cw:research "topic"     →  /cw:explore --research "topic"
```

### Utilities
```
/cw:context add ...      →  /cw:manage context add ...
/cw:sync                 →  /cw:manage sync
/cw:merge                →  /cw:manage merge
/cw:worktree create ...  →  /cw:manage worktree create ...
/cw:tidy                 →  /cw:manage tidy
/cw:init                 →  /cw:manage init
/cw:evolve               →  /cw:manage evolve
/cw:reflect              →  /cw:manage reflect
/cw:analytics            →  /cw:status (analytics integrated)
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
- **Enhanced**: `check_plan_adherence.py` suggests `/cw:go` when no plan exists

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
- **v3.1**: Deprecation stubs removed, v2 commands stop working
