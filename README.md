# claudemate

Claude Code plugin marketplace — automate, orchestrate, and extend AI-powered development workflows.

## Available Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [crew](./plugins/crew) | 4.1.1 | Agent-orchestrated development — 9-stage pipeline, 8 adaptive agents, parallel execution, research, review |
| [autopilot](./plugins/autopilot) | 0.4.0 | End-to-end autonomous pipeline — research → design → build → review → report |
| [multi-model-debate](./plugins/multi-model-debate) | 1.0.0 | Multi-agent debates using Claude, Codex, and Gemini for decision-making |
| [arch-guard](./plugins/arch-guard) | 0.2.2 | Architecture compliance — layer boundary checks, contract-first development, ADRs |
| [gemini-cli](./plugins/gemini-cli) | 1.0.0 | Gemini CLI integration — code review, commit messages, documentation |
| [worktree](./plugins/worktree) | 0.1.0 | Git worktree lifecycle management — create, merge, cleanup |

## Quick Start

```bash
# Add marketplace
claude plugins add github:jaebit/claudemate

# Install plugins
claude plugins install crew
claude plugins install autopilot
claude plugins install arch-guard
```

## Highlights

### autopilot

Single command from idea to working code:

```bash
/autopilot "build a notification system"
```

Chains crew, multi-model-debate, and arch-guard into a 5-phase autonomous pipeline with one user confirmation gate after design.

### crew

Agent-orchestrated development:

```bash
/crew:go "Add JWT authentication"     # Full 9-stage pipeline
/crew:explore --arch "microservice"   # Architecture design
/crew:review --all                    # Unified code review
```

### multi-model-debate

Cross-model evaluation for design decisions:

```bash
/multi-model-debate:debate-orchestration "REST vs GraphQL"
```

### arch-guard

Architecture compliance for layered projects:

```bash
/arch-guard:arch-check       # Verify layer boundaries
/arch-guard:contract-first   # Define interfaces first
/arch-guard:scaffold         # Generate module structure
```

## Contributing

1. Create a new folder under `plugins/`
2. Add `.claude-plugin/plugin.json` (only `name`, `version`, `description`)
3. Add skills (`skills/*/SKILL.md`), hooks (`hooks/hooks.json`), agents, or commands
4. Register in `.claude-plugin/marketplace.json`
5. Submit a pull request

## License

MIT License
