---
name: optimize
description: "Optimize a CLAUDE.md/AGENTS.md file using research-backed classification rules (arxiv 2602.11988v1)"
forked-context: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Docs Optimization Skill

Apply classification rules from arxiv 2602.11988v1 to reduce token overhead while preserving agent-critical information.

## Classification Rules

### HIGH-VALUE (Keep)
Content that measurably improves agent performance:
- **Test/build commands** - exact CLI invocations the agent cannot infer
- **Repo-specific constraints** - immutable rules, golden rules, project-specific Do's/Don'ts
- **Unique tool references** - custom MCP servers, plugin-specific tools, CLI flags
- **Operational commands** - deployment, CI/CD, environment setup

### HARMFUL (Remove)
Content that degrades performance by consuming tokens without benefit:
- **Directory structure trees** - agent discovers via Glob/LS; static trees go stale
- **Detailed inventories** - file-by-file descriptions, component catalogs
- **Schema tables** - full field listings already in source code
- **General coding patterns** - things the LLM already knows (REST conventions, error handling basics)

### NEUTRAL (Remove unless repo-unique)
Content that neither helps nor hurts, but wastes tokens:
- **README duplicates** - project context already in README.md
- **Tech stack lists** - discoverable from package.json/pyproject.toml
- **Aspirational guidelines** - vague quality goals without actionable rules
- **Maintenance policies** - versioning/changelog instructions

## Migration Strategies

| Strategy | When | How |
|----------|------|-----|
| **Pointer** | Content exists in another file | Replace with 1-line reference: `See path/to/file` |
| **Skill** | Needed only during specific tasks | Move to `skills/*/SKILL.md` for on-demand loading |
| **Delete** | Pure duplicate or auto-discoverable | Remove (source of truth already exists) |
| **Merge** | Scattered Do's/Don'ts lists | Consolidate into single Constraints section |

## 5-Step Process

### Step 1: SCAN
- Read the target file
- Count total lines: `wc -l <file>`
- List each `##` section with its line count

### Step 2: CLASSIFY
For each section, apply classification rules. Output a table:

```
| Section | Lines | Classification | Reason |
|---------|-------|----------------|--------|
| Operational Commands | 12 | HIGH-VALUE | Exact CLI invocations |
| Directory Structure | 45 | HARMFUL | Stale tree, auto-discoverable |
| ...
```

If `--report-only` flag: stop here and display the table.

### Step 3: PLAN
For each non-HIGH-VALUE section, assign a migration strategy. Calculate expected final line count.

```
| Section | Strategy | Target | Expected Lines |
|---------|----------|--------|----------------|
| Directory Structure | Delete | - | 0 |
| API Reference | Pointer | See docs/api.md | 1 |
| ...
```

If `--dry-run` flag: stop here and display the plan.

### Step 4: REWRITE
- Keep all HIGH-VALUE sections verbatim
- Apply migration strategies to other sections
- Merge scattered constraints into a single section
- Compress verbose wording (remove filler, use tables over paragraphs)
- Write the optimized file

### Step 5: VERIFY
- Confirm pointer targets exist (Glob/Read check)
- Run project tests if available (`pytest`, `npm test`, etc.)
- Display before/after comparison:
  ```
  Before: N lines | After: M lines | Reduction: X%
  ```
