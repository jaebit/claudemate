# Claude Marketplace

A plugin marketplace for Claude Code. Provides plugins to extend and automate AI-powered development workflows.

## Highlights

- **Workflow Automation** - Structured development process from task planning to review
- **AI Tool Integration** - Seamless integration with various AI CLI tools like Gemini and Codex
- **Productivity Boost** - Automate repetitive tasks and apply quality gates

## Available Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [cw](./plugins/context-aware-workflow) | 2.1.0 | Context-aware workflow orchestration - Plan Mode integration, automatic task planning, QA loops, Ralph Loop improvement cycles, model routing, Agent Teams, native worktree isolation |
| [codex-harness](./plugins/codex-harness) | 1.0.0 | Codex MCP integration - native codex/codex-reply tools + cloud operations |
| [gemini-cli](./plugins/gemini-cli) | 1.0.0 | Gemini CLI integration - code review, commit message generation, documentation, release notes |

## Quick Start

```bash
# Add marketplace
claude plugins add github:jyyang/claude-marketplace

# Install plugins
claude plugins install cw
claude plugins install codex-harness
claude plugins install gemini-cli
```

## Plugin Highlights

### Context-Aware Workflow (cw)

Structured development workflow orchestration:

```bash
/cw:start "Implement JWT auth"    # Generate task plan
/cw:loop "Fix bug"                # Auto-repeat until complete
/cw:auto "Add logout button"      # Run full workflow automatically
```

### Codex Harness

MCP-native Codex integration (auto-started `codex mcp-server`):

```bash
# MCP tools: codex, codex-reply (available automatically)
# CLI commands for cloud features:
/codex:cloud --env env123 Review this PR
/codex:apply task_abc123
```

### Gemini CLI

Google Gemini CLI integration:

```bash
/gemini:review              # Review staged changes
/gemini:commit              # Generate commit message
/gemini:docs src/utils.py   # Generate documentation
```

## Manual Installation

```bash
git clone https://github.com/jyyang/claude-marketplace.git
cp -r claude-marketplace/plugins/<plugin-name> ~/.claude/plugins/
```

## Contributing

1. Create a new folder under `plugins/`
2. Add `.claude-plugin/plugin.json` metadata
3. Configure commands, skills, agents, and hooks
4. Update `marketplace.json`
5. Submit a pull request

## License

MIT License
