# Crew Plugin Agent Matrix Analysis

## Agent Role Matrix

### Core Development Agents

| Agent | Model | Primary Responsibility | Key Tools | Integration Point |
|-------|--------|----------------------|-----------|-------------------|
| **analyst** | sonnet | Extract functional, non-functional, and implicit requirements from user requests | Read, Write, Glob, Grep, AskUserQuestion | Feeds into architect or planner |
| **architect** | sonnet | Design scalable system architecture and user experiences with component diagrams, data models, wireframes | Read, Write, Glob, Grep, Bash | Creates .caw/design/ specs for planner |
| **planner** | sonnet | Transform requirements into actionable, structured plans with Tidy First methodology | Read, Write, Glob, Grep, Bash, WebSearch | Generates .caw/task_plan.md |
| **builder** | sonnet | Execute implementation steps using TDD approach with automatic test execution | Read, Write, Edit, Bash, Grep, Glob | Implements task plan steps |

### Quality Assurance Agents

| Agent | Model | Primary Responsibility | Key Tools | Integration Point |
|-------|--------|----------------------|-----------|-------------------|
| **reviewer** | sonnet | Analyze implementations for quality, security, architecture, and potential issues | Read, Grep, Glob, Bash | Creates .caw/last_review.json |
| **fixer** | sonnet | Apply intelligent code improvements from auto-fix to deep remediation | Read, Write, Edit, Bash, Grep, Glob | Consumes review feedback |
| **compliance-checker** | haiku | Validate adherence to project rules, conventions, and workflow requirements | Read, Glob, Grep | Pre-merge validation |

### Infrastructure Agent

| Agent | Model | Primary Responsibility | Key Tools | Integration Point |
|-------|--------|----------------------|-----------|-------------------|
| **bootstrapper** | haiku | Environment initialization, .caw/ workspace setup, and project context detection | Read, Write, Glob, Bash | Must run before planner |

## Agent Workflow Dependencies

### Primary Flow
1. **bootstrapper** → Sets up .caw/ workspace
2. **analyst** → Extracts requirements → `.caw/spec.md`
3. **architect** → Designs system → `.caw/design/architecture.md`, `.caw/design/ux-ui.md`
4. **planner** → Creates plan → `.caw/task_plan.md`
5. **builder** → Implements steps → Code changes
6. **reviewer** → Reviews code → `.caw/last_review.json`
7. **fixer** → Applies fixes → Improved code
8. **compliance-checker** → Final validation

### Adaptive Complexity
All agents implement complexity-adaptive behavior:
- **Low**: Minimal analysis, direct implementation
- **Medium**: Standard TDD workflow, pattern following
- **High**: Deep analysis with Serena, comprehensive validation

## Schema Overview

### last_review.schema.json
Structured output from Reviewer agent for consumption by Fixer agent and Quick Fix skill.

**Key Fields:**
- `summary.overall_status`: APPROVED | APPROVED_WITH_SUGGESTIONS | NEEDS_WORK | REJECTED
- `issues[]`: Categorized issues with auto_fixable boolean
- `scores`: Quality metrics (correctness, code_quality, best_practices, security, performance)
- `action_items[]`: Prioritized improvement tasks

**Issue Categories:** constants, docs, style, imports, naming, logic, performance, security, architecture

### metrics.schema.json
Comprehensive workflow analytics and cost tracking schema.

**Key Sections:**
- `token_usage`: Input/output/cached token counts
- `cost_breakdown`: Cost per model tier (haiku/sonnet/opus)
- `agent_usage`: Per-agent invocation statistics
- `phase_metrics`: Performance by workflow phase
- `optimization_insights`: Generated recommendations for cost/performance improvement

**Background Tasks:** Execution statistics with timing patterns
**Eco Mode:** Usage tracking and estimated savings

### mode.schema.json
Tracks active workflow mode for context-aware behavior.

**Active Modes:**
- `DEEP_WORK`: Comprehensive analysis, completion required
- `MINIMAL_CHANGE`: Quick fixes, minimal scope
- `DEEP_ANALYSIS`: Research-focused workflow
- `RESEARCH`: Investigation and exploration
- `NORMAL`: Standard workflow behavior

**Trigger Keywords:** deepwork, quickfix, research, investigate, etc.

## Specialized Capabilities

### Agent-Specific Skills
- **analyst**: insight-collector, knowledge-engine
- **architect**: knowledge-engine, pattern-learner, insight-collector
- **planner**: pattern-learner, session-manager, knowledge-engine, insight-collector
- **builder**: quality-gate, session-manager, progress-tracker, pattern-learner, insight-collector
- **reviewer**: quality-gate, pattern-learner, knowledge-engine, insight-collector
- **fixer**: quality-gate
- **compliance-checker**: quality-gate, knowledge-engine

### MCP Server Integration
- **serena**: Advanced semantic code analysis (all development agents)
- **context7**: Documentation lookup (architect, planner, builder)
- **sequential**: Workflow coordination (analyst)

### Tidy First Methodology
**builder** and **planner** implement Tidy First approach:
- Structural improvements (Tidy steps) before behavioral changes (Build steps)
- Numbered with .0 suffix (e.g., 2.0 for tidy, 2.1 for build)
- Separate commit discipline: `[tidy]` vs `[feat]`/`[fix]` prefixes