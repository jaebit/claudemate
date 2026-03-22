# Module Context

**Module:** Crew
**Version:** 4.0.0
**Role:** Agent-orchestrated development pipeline with 8 adaptive agents.

---

# Operational Commands

```bash
# Run all tests
python -m pytest tests/

# Validate plugin structure
python tests/test_plugin_structure.py
```

## Skills (User-Invocable)

```bash
# Primary automation
/crew:go         # Full 9-stage pipeline (plan → build → review → fix)
/crew:dashboard     # Progress + cost/token analytics

# Quality assurance
/crew:review     # Unified QA (--loop, --build, --compliance, --fix, --gemini)

# Parallel execution
/crew:parallel   # Swarm (default) or Agent Teams (--team)

# Discovery & planning
/crew:explore    # Brainstorm (--arch, --ui, --research, --debate)

# Utilities
/crew:manage     # context, sync, merge, worktree, tidy, init, evolve, reflect
```

---

# Agents & Skills

8 agents (complexity-adaptive, no tier variants). See `_shared/agent-registry.md` for inventory.
Complexity signals: `_shared/complexity-hints.md`.

16 skills: go, status, review, parallel, explore, manage, progress-tracker, plan-detector, quality-gate, commit-discipline, insight-collector, pattern-learner, knowledge-engine, session-manager, learning-loop, structured-research.

---

# Local Golden Rules

## Do's

- **DO** add tests in `tests/` for every new agent or skill.
- **DO** ensure YAML frontmatter is valid before committing.
- **DO** clear context variables when workflows finish.
- **DO** let agents self-assess complexity using `_shared/complexity-hints.md`.

## Don'ts

- **DON'T** rely on global state across agent executions.
- **DON'T** use complex logic in Markdown; delegate to Python scripts.
- **DON'T** create model tier variants; agents adapt behavior internally.
