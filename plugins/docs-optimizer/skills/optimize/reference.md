# Docs Optimization Reference

Based on arxiv 2602.11988v1.

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
| **Pointer** | Content exists in another file | Replace with 1-line reference: `See path/to/file`. If multiple sections become single-line pointers, consolidate them into one `## References` section |
| **Skill** | Needed only during specific tasks | Move to `skills/*/SKILL.md` for on-demand loading |
| **Delete** | Pure duplicate or auto-discoverable | Remove (source of truth already exists) |
| **Merge** | Scattered Do's/Don'ts lists | Consolidate into single Constraints section |

## Classification Table Format

```
| Section | Lines | Classification | Reason |
|---------|-------|----------------|--------|
| Operational Commands | 12 | HIGH-VALUE | Exact CLI invocations |
| Directory Structure | 45 | HARMFUL | Stale tree, auto-discoverable |
```

## Migration Plan Format

```
| Section | Strategy | Target | Expected Lines |
|---------|----------|--------|----------------|
| Directory Structure | Delete | - | 0 |
| API Reference | Pointer | See docs/api.md | 1 |
```
