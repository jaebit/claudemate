# Agent Registry

Comprehensive catalog of all available agents for CAW v3.0 workflows.

## Overview

8 agents total. Each agent adapts its behavior based on task complexity (see [Complexity-Adaptive Behavior](./complexity-hints.md)). Claude Code handles model selection - agents do not control which model runs.

## Core Agents

### Planner
Plans and structures tasks into executable steps. Includes brainstorm mode for ideation.

| ID | File | Skills |
|----|------|--------|
| `cw:planner` | `planner.md` | pattern-learner, session-manager, knowledge-engine, insight-collector |

**Capabilities**: Task decomposition, phase structuring, dependency analysis, Tidy First methodology, Socratic brainstorming, requirements discovery

**Commands**: `/cw:start`, `/cw:brainstorm`

---

### Builder
Implements code following TDD approach.

| ID | File | Skills |
|----|------|--------|
| `cw:builder` | `builder.md` | quality-gate, session-manager, progress-tracker, pattern-learner, insight-collector |

**Capabilities**: TDD implementation, test-first development, code generation, pattern following, Serena symbolic editing, Tidy First commits

**Commands**: `/cw:next`, `/cw:loop`

---

### Reviewer
Reviews code for quality, security, and best practices.

| ID | File | Skills |
|----|------|--------|
| `cw:reviewer` | `reviewer.md` | quality-gate, pattern-learner, knowledge-engine, insight-collector |

**Capabilities**: Code quality analysis, bug detection, security scanning, performance review, architecture validation

**Commands**: `/cw:review`, `/cw:qaloop`, `/cw:ultraqa`

---

### Fixer
Applies fixes based on review feedback, from auto-fix to deep remediation.

| ID | File | Skills |
|----|------|--------|
| `cw:fixer` | `fixer.md` | quality-gate |

**Capabilities**: Auto-fixing lint issues, refactoring, pattern extraction, security patching, dependency analysis

**Commands**: `/cw:fix`, `/cw:qaloop`

---

### Architect
Designs system architecture and user experiences.

| ID | File | Skills |
|----|------|--------|
| `cw:architect` | `architect.md` | knowledge-engine, pattern-learner, insight-collector |

**Capabilities**: Architecture design, component diagrams, data models, API specs, wireframes, user flows, interaction specs, accessibility planning

**Commands**: `/cw:design --arch`, `/cw:design --ui`, `/cw:design`

---

## Specialized Agents

### Analyst
Extracts requirements during auto workflow expansion.

| ID | File | Skills |
|----|------|--------|
| `cw:analyst` | `analyst.md` | insight-collector, knowledge-engine |

**Capabilities**: Requirements extraction, specification creation, edge case discovery, dependency mapping

**Commands**: `/cw:auto` (expansion phase)

---

### Bootstrapper
Initializes workflow environment.

| ID | File | Skills |
|----|------|--------|
| `cw:bootstrapper` | `bootstrapper.md` | - |

**Capabilities**: Project type detection, framework identification, directory setup, context manifest creation, Serena onboarding

**Commands**: `/cw:init`, `/cw:start` (when `.caw/` missing)

---

### ComplianceChecker
Validates adherence to project rules and conventions.

| ID | File | Skills |
|----|------|--------|
| `cw:compliance-checker` | `compliance-checker.md` | quality-gate, knowledge-engine |

**Capabilities**: Rule validation, convention checking, style enforcement, compliance reporting

**Commands**: `/cw:check`

---

## Agent Selection Matrix

### By Task Type

| Task Type | Recommended Agent |
|-----------|-------------------|
| Planning | `cw:planner` |
| Brainstorming | `cw:planner` (brainstorm mode) |
| Implementation | `cw:builder` |
| Code Review | `cw:reviewer` |
| Bug Fixing | `cw:fixer` |
| Architecture | `cw:architect` |
| UX/UI Design | `cw:architect` (--ui mode) |
| Requirements | `cw:analyst` |
| Initialization | `cw:bootstrapper` |
| Compliance | `cw:compliance-checker` |

### By Command

| Command | Primary Agent |
|---------|---------------|
| `/cw:start` | `cw:planner` |
| `/cw:brainstorm` | `cw:planner` |
| `/cw:next` | `cw:builder` |
| `/cw:loop` | `cw:builder` |
| `/cw:review` | `cw:reviewer` |
| `/cw:qaloop` | `cw:reviewer` + `cw:fixer` |
| `/cw:ultraqa` | `cw:reviewer` |
| `/cw:fix` | `cw:fixer` |
| `/cw:design` | `cw:architect` |
| `/cw:auto` | `cw:analyst` + `cw:planner` + `cw:builder` |
| `/cw:init` | `cw:bootstrapper` |
| `/cw:check` | `cw:compliance-checker` |

## Related Documentation

- [Complexity-Adaptive Behavior](./complexity-hints.md) - How agents adapt to task complexity
- [Parallel Execution](./parallel-execution.md) - Concurrent agent execution
