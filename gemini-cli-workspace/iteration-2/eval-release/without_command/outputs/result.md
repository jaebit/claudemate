# Claude Marketplace Release Notes — v3.1

## Headline Summary
Claude Marketplace v3.1 marks the finalization of our major modernization initiative. This release solidifies the **Context-Aware Workflow (cw)** architecture by establishing a lean 6-command surface, purging legacy technical debt, and introducing powerful new plugins like **Docs Optimizer** and the MCP-native **Codex Harness**.

## Breaking Changes
- **Deprecation Cleanup**: Removed 23 legacy command stubs. The "bridge" from v2.x to v3.x is now closed; users must use the modernized command set.
- **Feature Consolidation**: Six overlapping features (`loop`, `swarm`, `team`, `worktree`, `merge`, and `reflect`) have been removed to reduce cognitive load and improve workflow reliability.
- **CLI Replacement**: `codex-cli` has been officially deprecated and replaced by the MCP-native `codex-harness`.

## New Features
- **Context-Aware Workflow (cw) v3.1**: A finalized, high-performance orchestration layer featuring a focused 6-command surface: `explore`, `go`, `manage`, `parallel`, `review`, and `status`.
- **Docs Optimizer v1.0.0**: A new utility plugin designed to automate the optimization of `CLAUDE.md` and `AGENTS.md` files for maximum token efficiency.
- **Codex Harness v1.0.0**: A modern, MCP-native integration for Codex, providing a more stable and powerful interface for Claude Code.
- **Gemini CLI v1.0.0**: Official integration for Google Gemini, enabling cross-provider AI workflows.
- **Plugin-Authoring Skill**: A new specialized skill extracted from marketplace best practices to help developers build their own Claude Code plugins.

## Improvements & Refactoring
- **Architectural Modernization**: Unified the structure of commands, agents, skills, and hooks for better maintainability and faster execution.
- **Internationalization**: Completed the translation of all documentation, usage guides, and READMEs into English.
- **Context Optimization**: Refactored core plugin files to minimize their token footprint within the Claude context window.
- **Agent Standardization**: Implemented a lowercase-with-hyphens naming convention and added comprehensive compliance fields to all agent definitions.

## Bug Fixes
- **Configuration**: Removed non-existent Codex MCP server references from `plugin.json`.
- **Pathing**: Fixed relative path resolution errors in `auto.md`.
- **Schema & Typing**: Corrected schema paths and standardized typing imports across the `cw` plugin.
- **Language Sync**: Resolved language inconsistencies in the `gemini-cli` documentation suite.

## Migration Notes (v3.0 to v3.1)
- **Command Update**: If you have existing scripts or habits relying on `cw loop` or `cw swarm`, transition to using `cw go` for task execution and `cw parallel` for multi-agent orchestration.
- **Plugin Re-installation**: We recommend a clean re-installation of the `cw` plugin to ensure all removed deprecation stubs are cleared from your local environment.
- **Adopt Docs-Optimizer**: Run the new `docs-optimizer` command on your project root to benefit from the latest `CLAUDE.md` structural improvements that v3.1 supports.
