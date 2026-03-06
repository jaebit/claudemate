# Module Context

**Module:** Context-Aware Workflow (cw)
**Version:** 2.1.0
**Role:** Advanced agentic workflow orchestration with intelligent model routing.

---

# Operational Commands

```bash
# Run all tests
python -m pytest tests/

# Validate plugin structure
python tests/test_plugin_structure.py
```

## Slash Commands

```bash
# Core workflow
/cw:start      # Initialize workflow
/cw:status     # Check progress
/cw:next       # Execute next step
/cw:init       # Project initialization

# Execution modes
/cw:auto       # Autonomous execution
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
/cw:evolve     # Self-improvement cycle
/cw:analytics  # Token/cost analysis

# Context & collaboration
/cw:context    # Manage context variables
/cw:sync       # Sync with external tools
/cw:tidy       # Cleanup resources

# Magic keywords: eco/ecomode, deepwork, quickfix, async
```

---

# Agents & Skills

18 agents (4 tiered x 3 tiers + 6 specialized). See `_shared/agent-registry.md` for full inventory.
Model routing: `_shared/model-routing.md`. Authoring patterns: `skills/plugin-authoring/SKILL.md`.

18 skills: context-manager, progress-tracker, plan-detector, quality-gate, review-assistant, commit-discipline, quick-fix, insight-collector, pattern-learner, knowledge-base, decision-logger, hud, dashboard, dependency-analyzer, context-helper, evolve, research, serena-sync.

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
