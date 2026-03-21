# Agent Registry

Comprehensive catalog of all available agents for CAW v3.1.0 workflows.

## Overview

8 agents total. Each agent adapts its behavior based on task complexity (see [Complexity-Adaptive Behavior](./complexity-hints.md)). Claude Code handles model selection - agents do not control which model runs.

## Core Agents

### Planner
Plans and structures tasks into executable steps. Includes brainstorm mode for ideation.

| ID | File | Skills |
|----|------|--------|
| `crew:planner` | `planner.md` | pattern-learner, session-manager, knowledge-engine, insight-collector |

**Capabilities**: Task decomposition, phase structuring, dependency analysis, Tidy First methodology, Socratic brainstorming, requirements discovery

**Commands**: `/crew:start`, `/crew:brainstorm`

---

### Builder
Implements code following TDD approach.

| ID | File | Skills |
|----|------|--------|
| `crew:builder` | `builder.md` | quality-gate, session-manager, progress-tracker, pattern-learner, insight-collector |

**Capabilities**: TDD implementation, test-first development, code generation, pattern following, Serena symbolic editing, Tidy First commits

**Commands**: `/crew:next`, `/crew:loop`

---

### Reviewer
Reviews code for quality, security, and best practices.

| ID | File | Skills |
|----|------|--------|
| `crew:reviewer` | `reviewer.md` | quality-gate, pattern-learner, knowledge-engine, insight-collector |

**Capabilities**: Code quality analysis, bug detection, security scanning, performance review, architecture validation

**Commands**: `/crew:review`, `/crew:qaloop`, `/crew:ultraqa`

---

### Fixer
Applies fixes based on review feedback, from auto-fix to deep remediation.

| ID | File | Skills |
|----|------|--------|
| `crew:fixer` | `fixer.md` | quality-gate |

**Capabilities**: Auto-fixing lint issues, refactoring, pattern extraction, security patching, dependency analysis

**Commands**: `/crew:fix`, `/crew:qaloop`

---

### Architect
Designs system architecture and user experiences.

| ID | File | Skills |
|----|------|--------|
| `crew:architect` | `architect.md` | knowledge-engine, pattern-learner, insight-collector |

**Capabilities**: Architecture design, component diagrams, data models, API specs, wireframes, user flows, interaction specs, accessibility planning

**Commands**: `/crew:design --arch`, `/crew:design --ui`, `/crew:design`

---

## Specialized Agents

### Analyst
Extracts requirements during auto workflow expansion.

| ID | File | Skills |
|----|------|--------|
| `crew:analyst` | `analyst.md` | insight-collector, knowledge-engine |

**Capabilities**: Requirements extraction, specification creation, edge case discovery, dependency mapping

**Commands**: `/crew:auto` (expansion phase)

---

### Bootstrapper
Initializes workflow environment.

| ID | File | Skills |
|----|------|--------|
| `crew:bootstrapper` | `bootstrapper.md` | - |

**Capabilities**: Project type detection, framework identification, directory setup, context manifest creation, Serena onboarding

**Commands**: `/crew:init`, `/crew:start` (when `.caw/` missing)

---

### ComplianceChecker
Validates adherence to project rules and conventions.

| ID | File | Skills |
|----|------|--------|
| `crew:compliance-checker` | `compliance-checker.md` | quality-gate, knowledge-engine |

**Capabilities**: Rule validation, convention checking, style enforcement, compliance reporting

**Commands**: `/crew:check`

---

## Agent Selection Matrix

### By Task Type

| Task Type | Recommended Agent |
|-----------|-------------------|
| Planning | `crew:planner` |
| Brainstorming | `crew:planner` (brainstorm mode) |
| Implementation | `crew:builder` |
| Code Review | `crew:reviewer` |
| Bug Fixing | `crew:fixer` |
| Architecture | `crew:architect` |
| UX/UI Design | `crew:architect` (--ui mode) |
| Requirements | `crew:analyst` |
| Initialization | `crew:bootstrapper` |
| Compliance | `crew:compliance-checker` |

### By Command

| Command | Primary Agent |
|---------|---------------|
| `/crew:start` | `crew:planner` |
| `/crew:brainstorm` | `crew:planner` |
| `/crew:next` | `crew:builder` |
| `/crew:loop` | `crew:builder` |
| `/crew:review` | `crew:reviewer` |
| `/crew:qaloop` | `crew:reviewer` + `crew:fixer` |
| `/crew:ultraqa` | `crew:reviewer` |
| `/crew:fix` | `crew:fixer` |
| `/crew:design` | `crew:architect` |
| `/crew:auto` | `crew:analyst` + `crew:planner` + `crew:builder` |
| `/crew:init` | `crew:bootstrapper` |
| `/crew:check` | `crew:compliance-checker` |

## Skills Inventory

| Skill | Purpose |
|-------|---------|
| progress-tracker | Workflow progress metrics |
| plan-detector | Plan Mode completion detection |
| quality-gate | Automated quality checks |
| commit-discipline | Tidy First commit classification |
| insight-collector | Hybrid learning and pattern capture |
| pattern-learner | Codebase pattern analysis |
| knowledge-engine | ADR logging, knowledge management |
| session-manager | Session state, context, analytics |
| learning-loop | Ralph Loop reflection and improvement |
| structured-research | 4-stage deep research (decompose → investigate → cross-validate → synthesize) |

## Related Documentation

- [Complexity-Adaptive Behavior](./complexity-hints.md) - How agents adapt to task complexity
- [Parallel Execution](./parallel-execution.md) - Concurrent agent execution
