This release represents a significant evolution of the **Context Aware Workflow (CW)** system, moving from a broad collection of experimental plugins to a highly optimized, modernized core. The focus has shifted towards consolidating the command surface, improving token efficiency, and enhancing cross-platform compatibility.

### **Release Highlights**

- **Modernization (v3.0/v3.1):** Streamlined the entire workflow by consolidating commands and removing over 20 deprecated stubs and redundant features.
- **Enhanced Intelligence:** Introduced "Agent Teams" and refined "Intent-Based Skills" for more autonomous and context-aware execution.
- **Ecosystem Expansion:** Added specialized plugins for Rails 8, Quant analysis (Quant-K), and Google Gemini integration.
- **Performance Optimization:** Drastic reduction in token usage across skills and agents to support longer, more complex sessions.

---

### **v3.1 — Finalization & Cleanup**
*Focus: Removing legacy debt and finalizing the modernized command surface.*

#### **Breaking Changes**
- Finalized the **6-command surface**, removing 23 legacy deprecation stubs to ensure a cleaner API.

#### **Bug Fixes**
- Removed reference to a non-existent `codex` MCP server from `plugin.json`.

---

### **v3.0 — Modernization & Consolidation**
*Focus: Deep architectural refactoring for the next generation of AI-native workflows.*

#### **Breaking Changes**
- **Consolidated Core:** Merged commands, agents, skills, and hooks into a unified modernization framework.
- **Feature Pruning:** Removed 6 overlapping features (Loop, Swarm, Team, Worktree, Merge, Reflect) in favor of more robust, integrated alternatives.

#### **Features**
- **Plugin-Authoring Skill:** Extracted from `CLAUDE.md` to help automate the creation of new plugins.
- **Docs-Optimizer:** Added a dedicated plugin to automatically optimize project documentation for AI readability.
- **Codex-Harness:** Replaced the legacy `codex-cli` with an MCP-native harness for better tool integration.

---

### **v2.1.0 — Agent Teams & Integration**
*Focus: Scaling automation through collaborative agent structures.*

#### **Features**
- **Agent Teams:** Implemented a multi-agent collaboration system.
- **Native Worktree Integration:** Improved support for managing multiple Git worktrees directly within the workflow.

#### **Improvements**
- **Validation Suite:** Added official Claude Code spec validation and agent tiering reports.
- **Documentation:** Comprehensive updates to `USAGE-GUIDE.md` and `USER_GUIDE.md`.

---

### **Quant-K (formerly KRX-Quant) Updates**
*Focus: High-performance financial data analysis.*

#### **Features**
- **ROE Calculation:** Added Return on Equity metrics to the stock screener.
- **Ultra-Analyze Mode:** New high-depth analysis workflow for market data.
- **Parallel Collection:** Multi-threaded data gathering to prevent UI freezes.

#### **Improvements**
- **Token Efficiency:** Reduced `SKILL.md` sizes by up to 86% through aggressive optimization.
- **Architecture:** Shifted from MCP-based pykrx to direct calls for increased stability and speed.
- **Robustness:** Added dynamic port allocation and auto-reconnect logic for persistent sessions.

---

### **v1.5.0 - v1.9.0 — Foundation & Automation**
*Focus: Establishing the Core Context Aware Workflow (CAW).*

#### **Features**
- **v1.9.0:** Automated generation of `GUIDELINES.md` and `AGENTS.md`.
- **v1.8.0:** Added OMC (Official Model Context) integration, QA Loop, UltraQA, and Research Mode.
- **v1.5.0:** Introduced the Ralph Loop integration, model routing, and "Magic Keywords."
- **Auto-Mode:** Implemented signal-based phase transitions for fully autonomous execution.

---

### **Plugin Ecosystem Highlights**

#### **Rails 8 + Hotwire**
- Added a comprehensive Ruby 4.0/Rails 8 knowledge base.
- Included 20+ slash commands for rapid Rails development.

#### **Gemini CLI Integration**
- Added `/gemini:search` command with Search Grounding support.
- Full registration in the marketplace with dedicated documentation.

#### **Intent-Based Skills**
- Added a research-driven pipeline that allows agents to "learn" and create new skills based on project needs.
- Improved cross-platform compatibility with UTF-8 support for Windows.

---

### **General Improvements & Bug Fixes**
- **Cross-Platform:** Standardized Python calls (using `python3`) and improved path handling for Windows, macOS, and Linux.
- **Token Optimization:** System-wide refactor of command and agent files to minimize context window usage.
- **Security:** Hardened `.gitignore` and secret handling across all plugin templates.
