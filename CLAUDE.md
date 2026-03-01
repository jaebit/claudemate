# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Operational Commands

```bash
# Install marketplace
claude plugins add github:jaebit/context-aware-workflow

# Install specific plugin
claude plugins install <plugin-name>

# Clear plugin cache
rm -rf ~/.claude/plugins/cache/<marketplace>/<plugin>/

# Run tests (context-aware-workflow)
cd plugins/context-aware-workflow && python -m pytest tests/
```

---

# Golden Rules

## Immutable

- **plugin.json Schema:** Only `name`, `version`, `description`, `mcpServers` fields allowed. Any other field causes validation failure.
- **File-Based Discovery:** Commands (`commands/*.md`), agents (`agents/*.md`), skills (`skills/*/SKILL.md`), hooks (`hooks/hooks.json`) are auto-discovered by path, not declared in plugin.json.
- **Registry Sync:** Every plugin MUST be registered in `.claude-plugin/marketplace.json`.

## Cross-Platform (REQUIRED)

- **Paths:** Use `/` (auto-handled), `path.join()`, `os.path.join()`
- **Commands:** Use `python3` or `node` (NOT cat/rm/type/sh)
- **Wrap paths:** `"${CLAUDE_PLUGIN_ROOT}/path"`
- **Note:** `${CLAUDE_PLUGIN_ROOT}` is runtime substitution, NOT env var

## Constraints

- **DON'T** add `author`, `features`, `commands`, `agents`, `skills`, or `hooks` fields to plugin.json.
- **DON'T** use `type: "prompt"` hooks outside of `Stop`/`SubagentStop` events.
- **DON'T** create MCP servers without proper error handling and Zod validation.
- **DO** update `marketplace.json` and root `README.md` when adding/removing plugins.
- **DO** validate YAML frontmatter syntax before committing.
- **DO** use strict semantic versioning in `plugin.json`.

## Git Strategy

- Branch: Feature branches from `master`
- Commits: Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- PR: Update CHANGELOG if user-facing changes

---

# Active Plugins

- **[Context-Aware Workflow](./plugins/context-aware-workflow/CLAUDE.md)**
- **[Codex Harness](./plugins/codex-harness/CLAUDE.md)**
- **[Gemini CLI](./plugins/gemini-cli/CLAUDE.md)**
- **[Docs Optimizer](./plugins/docs-optimizer/CLAUDE.md)**
