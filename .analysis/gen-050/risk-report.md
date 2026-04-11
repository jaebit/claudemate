# claudemate Plugin Ecosystem Risk Assessment Report
## Generation: gen-050 | Date: 2026-04-11

### Executive Summary

This technical analysis examines 7 plugins across the claudemate ecosystem, revealing significant disparities in complexity, testing coverage, and architectural standards. While plugin.json schema compliance is universal (100%), critical gaps exist in test coverage, shared resource standardization, and hook implementation patterns.

---

## Section 1: Shared Resource Analysis

### _shared/ Directory Mapping

**Plugins with _shared/ resources:**
- **arch-guard**: 2 files (detect-project.mjs, load-config.mjs)
- **autopilot**: 1 file (phase-artifacts.md)  
- **crew**: 34 files (comprehensive shared ecosystem)

**Total shared resources:** 37 files across 3/7 plugins (43% adoption)

**crew _shared/ inventory:**
- Documentation templates: advisor-protocol.md, agent-registry.md, background-heuristics.md
- Schema definitions: 7 JSON schemas in schemas/ subdirectory
- Integration guides: serena-integration.md, session-management.md
- Memory templates: 4 Serena memory templates in serena-memory-templates/

**Shared resource patterns:**
- **arch-guard**: Utility scripts (.mjs) for project detection
- **autopilot**: Process documentation (.md)
- **crew**: Mixed ecosystem (schemas, docs, templates)

---

## Section 2: Risk Assessment Matrix

### **[P0] Immediate Risks - Requires Direct Action**

**P0-1: Test Coverage Monopolization**  
*Evidence:* Only crew (1/7 plugins) has test coverage with 4 test files. Remaining 6 plugins have zero test files.
- **Impact:** 86% of plugins lack quality assurance
- **Risk:** Silent failures, regression vulnerabilities, deployment confidence degradation
- **Files verified:** `fd -t f . plugins/*/tests/` shows only crew/tests/ exists

**P0-2: Complexity Concentration Outlier**  
*Evidence:* crew contains 107 files vs average of 9.5 files for other plugins (11x complexity ratio)
- **Impact:** Single point of ecosystem failure, maintenance bottleneck
- **Risk:** Crew failure cascades to autopilot (declared dependency)
- **Verification:** File counts confirmed via `fd -t f . plugins/*/` 

### **[P1] Short-term Improvement Targets**

**P1-1: Hook Event Implementation Gap**  
*Evidence:* Only 4/7 plugins implement hooks, with varying event coverage:
- arch-guard: 3 events (SessionStart, PreToolUse, Stop)
- autopilot: 2 events (SessionStart, SubagentStop) 
- crew: 5 events (comprehensive lifecycle)
- gemini-cli: 1 event (SessionStart only)

**P1-2: MCP Integration Underutilization**  
*Evidence:* Only codex-cli (1/7) uses mcpServers field in plugin.json
- **Risk:** Limited external service integration, missed automation opportunities

**P1-3: _shared Resource Standardization Absence**  
*Evidence:* No consistent structure across arch-guard (.mjs), autopilot (.md), crew (mixed)
- **Risk:** Resource reuse friction, inconsistent patterns

### **[P2] Long-term Strategic Concerns**

**P2-1: Plugin Distribution Imbalance**  
*Evidence:* crew's 34 _shared files dwarf arch-guard (2) and autopilot (1)
- **Recommendation:** Extract reusable components to marketplace-level shared library

**P2-2: Testing Framework Standardization**  
*Evidence:* crew uses pytest, but no testing standard exists for other plugins

---

## Section 3: Dependency Structure Summary

### Plugin.json Schema Compliance: ✅ 100%
**Verification:** All 7 plugins use only allowed fields (name, version, description, mcpServers)
- **Standard compliance:** arch-guard, autopilot, crew, gemini-cli, multi-model-debate, worktree
- **MCP integration:** codex-cli (uses mcpServers.codex)

### .claude-plugin/ Path Standardization: ✅ 100%
**Verification:** All plugins consistently use `.claude-plugin/plugin.json` structure
- **Discovery method:** `fd -H -t f "plugin.json" plugins/` confirms universal compliance

### Hook Implementation Coverage: ⚠️ 57% 
- **Implemented:** arch-guard, autopilot, crew, gemini-cli
- **Missing:** codex-cli, multi-model-debate, worktree

### Inter-plugin Dependencies:
- **autopilot → crew** (declared dependency)
- **autopilot → multi-model-debate** (optional)
- **autopilot → codex-cli** (optional)
- **crew** (standalone, no external dependencies)

---

## Section 4: Improvement Roadmap

### Phase 1: P0 Risk Mitigation (Immediate - Week 1)

**Action 1.1: Test Coverage Expansion**
- Add basic test structure to all 6 untested plugins
- Template: Follow crew's pytest pattern
- Target: Minimum smoke tests for core functionality

**Action 1.2: Crew Complexity Audit**  
- Analyze crew's 107 files for decomposition opportunities
- Extract standalone utilities to marketplace-level shared/
- Document essential vs auxiliary components

### Phase 2: P1 Standardization (Short-term - Month 1)

**Action 2.1: Hook Pattern Standardization**
- Implement SessionStart hooks for codex-cli, multi-model-debate, worktree
- Standardize hook event coverage across plugins
- Document hook best practices

**Action 2.2: _shared Resource Framework**
- Define standard _shared/ directory structure
- Create templates for .mjs utilities, .md documentation, .json schemas
- Migrate existing shared resources to standard

### Phase 3: P2 Strategic Enhancement (Long-term - Quarter 1)

**Action 3.1: MCP Integration Strategy**
- Evaluate MCP opportunities for remaining 6 plugins  
- Standardize external service integration patterns
- Create MCP integration guidelines

**Action 3.2: Plugin Architecture Guidelines**
- Document complexity thresholds (target: <30 files per plugin)
- Establish plugin decomposition criteria
- Create marketplace-level shared library

### Success Metrics

- Test coverage: 0% → 85% (6 additional plugins)
- Hook coverage: 57% → 100% (3 additional plugins)
- _shared standardization: ad-hoc → templated structure
- crew complexity: 107 files → <50 files (decomposition target)

---

*Report generated via domain-expert v1.2.0 with file-system cross-verification (fd -H flag compliance)*