Loaded cached credentials.
I will now generate professional release notes based on the provided commit history, focusing on the major transition from v2.1.0 to v3.1.

# Release Notes: Context-Aware Workflow (CW) Evolution

## Summary
This release marks a significant milestone in the evolution of the Context-Aware Workflow system, progressing from version 2.1.0 through a major v3.0 modernization to the current v3.1. The focus of these updates has been on architectural consolidation, performance optimization, and transitioning to an MCP-native (Model Context Protocol) infrastructure. By streamlining the command surface and removing redundant features, the workflow is now leaner, faster, and more intuitive.

---

## ⚠️ Breaking Changes
- **v3.1 Command Finalization:** Finalized the core 6-command surface and removed 23 legacy deprecation stubs to ensure a clean, modern API.
- **v3.0 Modernization:** Major consolidation of commands, agents, skills, and hooks, representing a significant shift in how the workflow is structured.
- **Feature Removal:** Deprecated and removed 6 overlapping features (Loop, Swarm, Team, Worktree, Merge, and Reflect) in favor of more integrated, modern alternatives.

## 🚀 Features
- **MCP-Native Integration:** Replaced `codex-cli` with `codex-harness`, fully embracing Model Context Protocol for improved tool interoperability.
- **Documentation Optimizer:** Introduced the `docs-optimizer` plugin, enabling automated optimization of `CLAUDE.md` and other project documentation.
- **New Skills:** Added the `plugin-authoring` skill, providing dedicated support for extending the workflow's capabilities.
- **Agent Teams:** (v2.1.0) Introduced native support for Agent Teams and worktree integration.

## 🛠 Bug Fixes
- **Plugin Configuration:** Removed references to non-existent Codex MCP servers in `plugin.json`.
- **Naming Standards:** Fixed inconsistencies in agent naming by standardizing the `name` field to a `lowercase-with-hyphens` format.

## 🧹 Improvements & Refactoring
- **Architectural Alignment:** Refactored agents to strictly align with the tiering conventions and schemas defined in the project's core guidelines.
- **Enhanced Validation:** Added comprehensive subagent tier validation reports to ensure system-wide compliance and reliability.
- **Documentation Overhaul:** Updated the `README.md`, `USER_GUIDE.md`, and `USAGE-GUIDE.md` to reflect the latest feature sets and migration paths.
- **Migration Support:** Provided handoff documentation for the transition from `codex-cli` to `codex-harness`.
