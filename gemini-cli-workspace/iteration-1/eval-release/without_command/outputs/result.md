# Release Notes: Context-Aware Workflow (CAW)

Comprehensive release notes for the `context-aware-workflow` (Claude Code plugin) marketplace project, covering major milestones from foundational architecture to the v3.1 modernization.

---

## [v3.1] — Finalized Command Surface
*March 2026*

This release focuses on radical simplification and stability, pruning legacy code to provide a focused, high-performance toolset.

### 🚀 Features
- **Lean Command Surface:** Finalized the core 6-command interface for better discoverability and reduced cognitive load.
- **Enhanced Authoring:** Extracted the `plugin-authoring` skill directly from `CLAUDE.md` to assist developers in building compatible extensions.

### 🧹 Refactoring (Breaking Changes)
- **Deprecation Cleanup:** Removed 23 legacy stubs and deprecated components to streamline the codebase.
- **Feature Consolidation:** Removed 6 overlapping/redundant features including `swarm`, `team`, `worktree`, `merge`, `reflect`, and legacy `loop` implementations.

---

## [v3.0] — Modernization & Consolidation
*February 2026*

A major architectural overhaul to align with modern Claude Code standards and improve token efficiency.

### 🚀 Features
- **Unified Architecture:** Consolidated agents, skills, hooks, and commands into a cohesive internal structure.
- **Intent Recognition:** Introduced an intent-based skill system with ambiguity detection to better handle vague user prompts.
- **Async Hooks:** Implemented non-blocking hooks for Gemini reviews, improving UI responsiveness during background processing.

### ⚡ Performance
- **Token Optimization:** Major refactoring of agents, commands, and skill files to minimize token usage without sacrificing functionality.
- **Shared Templates:** Implemented shared templates to reduce duplication across plugin components.

---

## [v2.1.0] — Collaboration & Worktrees
*January 2026*

Focused on scaling the workflow to complex environments and multi-tasking.

### 🚀 Features
- **Agent Teams:** Introduced the ability to deploy specialized "teams" of agents for multifaceted tasks.
- **Native Worktree Integration:** Seamless support for git worktrees, allowing parallel development across different branches.
- **Subagent Tiering:** Established a formal tiering system for agents (Analyst, Architect, Builder, etc.) with explicit validation reports.

### 📝 Documentation
- **Comprehensive Guides:** Major updates to `USAGE-GUIDE.md`, `USER_GUIDE.md`, and `README.md` reflecting v2.1.0 capabilities.
- **Official Spec Validation:** Added Claude Code official spec validation docs.

---

## [v1.9.0] — Automated Governance
*December 2025*

### 🚀 Features
- **Auto-Generation:** Added automated generation for `GUIDELINES.md` and `AGENTS.md` to maintain project consistency.
- **Signal-Based Transitions:** Implemented "Auto Mode" with signal-based phase transitions for autonomous workflow progression.

### 🔧 Bug Fixes
- **Platform Compatibility:** Improved macOS and Windows support by unifying Python execution (switching to `python3`) and handling UTF-8 encoding issues.

---

## [v1.8.0] — Research & QA Loops
*November 2025*

### 🚀 Features
- **OMC Integration:** Full integration with "Oh My Claude" (OMC) features.
- **QA Loop & UltraQA:** Introduced specialized loops for rigorous quality assurance and testing.
- **Research Mode:** Added a dedicated mode for deep-dive codebase investigations.
- **Agent Resolver:** Implemented a system-wide agent resolver for OMC integration.

---

## [v1.5.0] — Intelligent Routing
*October 2025*

### 🚀 Features
- **Ralph Loop:** Integration with Ralph Loop for iterative refinement.
- **Model Routing:** Intelligent routing of tasks to specific models based on complexity.
- **Magic Keywords:** Introduced specialized trigger words for quick command invocation.
- **Forked Context:** Added support for managing independent context branches.

---

## [v1.1.0] — Foundation & Persistence
*September 2025*

### 🚀 Features
- **Serena MCP Integration:** Added cross-session persistence via Serena MCP.
- **Parallel Execution:** Introduced initial support for parallel task and phase-level execution.
- **Tidy First Discipline:** Integrated "Tidy First" commit discipline and quality gates.
- **Project-Local Storage:** Migrated workflow state to project-local storage for better privacy and portability.

### 🔧 Core Fixes & Improvements
- **Cross-Platform Hooks:** Standardized `hooks.json` to support Windows, macOS, and Linux seamlessly.
- **Schema Validation:** Implemented strict schema validation for `plugin.json` and marketplace manifests.
- **Initial Agents:** Bootstrapped the core agent set: `analyst`, `architect`, `bootstrapper`, `builder`, `fixer`, `planner`, and `reviewer`.

---

## 🛠 Related Ecosystem Updates
- **Codex Migration:** Successfully migrated from `codex-cli` to the MCP-native `codex-harness`.
- **Docs Optimizer:** Launched a standalone `docs-optimizer` plugin to maintain high-quality `CLAUDE.md` files.
- **Gemini CLI:** Registered the `gemini-cli` plugin with specialized commands for code review and documentation.
- **Quant-K Support:** Integrated high-performance trading workflow tools (formerly `krx-quant`).

---
*Generated based on repository commit history.*
