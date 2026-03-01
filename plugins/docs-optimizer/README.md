# docs-optimizer

Optimize CLAUDE.md and AGENTS.md files using research-backed classification rules from [arxiv 2602.11988v1](https://arxiv.org/abs/2602.11988v1).

## Why

Large CLAUDE.md files waste context tokens and can degrade agent performance. This plugin applies empirical classification rules to identify what to keep, what to remove, and what to migrate — typically achieving 40-65% reduction.

## Quick Start

```bash
# Install
claude plugins install docs-optimizer

# Optimize all CLAUDE.md/AGENTS.md in project
/docs-optimizer:optimize

# Optimize a specific file
/docs-optimizer:optimize path/to/CLAUDE.md

# Preview without changes
/docs-optimizer:optimize --dry-run

# Analysis report only
/docs-optimizer:optimize --report-only
```

## Classification Rules

| Category | Action | Examples |
|----------|--------|---------|
| **HIGH-VALUE** | Keep | Test/build commands, repo-specific constraints, unique tool references |
| **HARMFUL** | Remove | Directory trees, detailed inventories, schema tables, general coding patterns |
| **NEUTRAL** | Remove | README duplicates, tech stack lists, aspirational guidelines |

## Migration Strategies

- **Pointer**: Replace with 1-line reference (`See path/to/file`)
- **Skill**: Move to on-demand skill for task-specific loading
- **Delete**: Remove pure duplicates or auto-discoverable content
- **Merge**: Consolidate scattered Do's/Don'ts into single Constraints section

## Process

1. **Scan** — Count lines, identify sections
2. **Classify** — Apply rules to each section
3. **Plan** — Assign migration strategy, estimate reduction
4. **Rewrite** — Generate optimized version
5. **Verify** — Check pointer targets, run tests, show before/after

## Research Basis

Based on findings from arxiv 2602.11988v1, which demonstrates that:
- Directory structures and detailed inventories actively harm agent performance
- Test/build commands and repo-specific constraints are the highest-value content
- Optimal CLAUDE.md files are concise, actionable, and avoid duplicating discoverable information
