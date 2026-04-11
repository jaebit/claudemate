---
title: Vault Conventions
zone: meta
created: 2026-04-11
last_updated: 2026-04-11
---

# Vault Conventions

## Core Principle

**"Same Vault, different governance."**

The `knowledge/` directory is a single Obsidian Vault with logical zones.
Markdown files are the source of truth. Obsidian is a human-facing lens, not the storage layer.

## Zone Architecture

| Zone | Prefix | Stability | Write Owner | Description |
|------|--------|-----------|-------------|-------------|
| `00-meta/` | 00 | Highest | Human only | System: indices, conventions, schemas |
| `10-wiki/` | 10 | High | Wiki CLI only | Code knowledge: module pages, cross-cutting docs |
| `20-notes/` | 20 | Medium | Human + limited agent | Research notes, design docs |
| `30-memory/` | 30 | Dynamic | Memory manager only | Agent memory: facts, experiences |
| `90-templates/` | 90 | Utility | Human only | Obsidian Templater templates |

## Numbered Prefix Convention

Numbers encode a **stability gradient**:
- `00` = most stable (rules, indices — rarely change)
- `10` = stable (refined code knowledge)
- `20` = moderate (research, human notes)
- `30` = most dynamic (agent experiences)
- `90` = utility (templates, helpers)

Sub-folders use **pure semantic names** (e.g., `modules/`, `cross-cutting/`, `facts/`).

## Write Ownership Rules

1. **`10-wiki/`**: Only the wiki CLI (`wiki init`, `wiki update`) may create or modify files.
   Human edits must go through the CLI or be flagged in CI.
2. **`30-memory/`**: Only the memory manager pipeline may write.
   Manual edits are prohibited.
3. **`20-notes/`**: Humans may freely edit. Agents may append to `LLM-ZONE` sections only.
4. **`00-meta/`** and **`90-templates/`**: Human-only. Agents must not modify.

## Zone-Based Editing

Files that allow mixed human/agent editing use zone markers:

```markdown
<!-- HUMAN-ZONE -->
Content here is human-authored. Agents must not modify.
<!-- /HUMAN-ZONE -->

<!-- LLM-ZONE -->
Content here is agent-generated. Humans may review but should edit via the agent.
<!-- /LLM-ZONE -->
```

**Rules:**
- Agents must never modify content inside `HUMAN-ZONE` markers
- Humans should not edit `LLM-ZONE` content directly (use agent commands instead)
- Zone markers themselves must not be moved or deleted by agents

## Frontmatter Requirements

Every Markdown file in the vault MUST include YAML frontmatter with at minimum:

```yaml
---
title: Page Title
zone: meta | wiki | notes | memory
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
---
```

Wiki pages additionally require:
```yaml
module: module-name
last_verified_commit: abc1234
confidence: 0.0-1.0
```

Memory entries additionally require:
```yaml
memory_type: factual | experiential
canonical_id: unique-stable-id
confidence: 0.0-1.0
source_task: task-id-or-description
```

## Obsidian Sync

**Obsidian Sync is explicitly prohibited.** Git tracks all change history.
Use `git` for backup, versioning, and collaboration.

## File Naming

- Use `kebab-case` for all filenames
- Wiki module pages: match the module/package directory name
- Memory entries: `{canonical_id}.md` format
- Notes: free naming, but prefer descriptive kebab-case
