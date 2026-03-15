# CAW Skill Ecosystem Design

Design document for automation skills that enhance Agents.

## Design Principles

1. **Commands are explicit workflows** - User invokes directly
2. **Skills enhance Agents** - Agents utilize automatically
3. **Hook integration** - Event-based automatic triggers
4. **Progressive Disclosure** - Load context only when needed

## Skill Status (16 implemented)

| # | Skill | Description | Status |
|---|-------|-------------|--------|
| 1 | plan-detector | Plan Mode detection and workflow start | ✅ Implemented |
| 2 | insight-collector | Automatic insight collection and storage | ✅ Implemented |
| 3 | ~~session-persister~~ | ~~Session state save and restore~~ | ❌ Removed (delegated to built-in) |
| 4 | quality-gate | Quality verification before step completion | ✅ Implemented |
| 5 | progress-tracker | Work progress metric tracking | ✅ Implemented |
| 6 | context-helper | Agent context understanding and management support | ✅ Implemented |
| 7 | pattern-learner | Codebase pattern learning | ✅ Implemented |
| 8 | decision-logger | Technical decision auto-logging (ADR) | ✅ Implemented |
| 9 | knowledge-base | Project knowledge accumulation and search | ✅ Implemented |
| 10 | review-assistant | Code review checklist auto-generation | ✅ Implemented |
| 11 | **commit-discipline** | Tidy First commit separation rules enforcement | ✅ Implemented |
| 12 | ~~context-manager~~ | ~~Context window optimization~~ | Removed (1M context) |
| 13 | **dependency-analyzer** | Dependency graph analysis and parallel execution | ✅ Implemented |
| 14 | **quick-fix** | Simple review issue auto-fix | ✅ Implemented |
| 15 | **reflect** | Ralph Loop continuous improvement cycle | ✅ Implemented |
| 16 | **serena-sync** | Serena MCP memory synchronization | ✅ Implemented |

---

## Skill Catalog

---

### 1. plan-detector
**Automatic Plan Mode detection and workflow start**

| Property | Value |
|----------|-------|
| **Trigger** | Plan Mode completion detected |
| **Output** | `/cw:start --from-plan` auto-suggestion |
| **Integration** | PostToolUse Hook (ExitPlanMode) |

**Workflow:**
```
1. PostToolUse Hook detects ExitPlanMode
2. plan-detector Skill activates
3. Plan file analysis (implementation feasibility)
4. Suggest workflow start to user
```

**Example:**
```
🎯 Plan Mode Completion Detected

Plan file: .claude/plans/auth-system.md
- Implementation phases: 5 Phases, 12 Steps
- Expected files: 8 modified, 3 created

Would you like to start CAW workflow automatically?
[1] Yes, run /cw:start --from-plan
[2] No, start manually later
```

**Directory:**
```
skills/plan-detector/
├── SKILL.md
└── patterns.md      # Plan file pattern definitions
```

---

### 2. insight-collector
**Auto-collection and storage of model response insights**

| Property | Value |
|----------|-------|
| **Trigger** | `★ Insight` pattern detected in response |
| **Output** | Save to `.caw/insights/` folder |
| **Integration** | PostToolUse Hook (all responses) |

**Workflow:**
```
1. Scan model response
2. Extract "★ Insight" blocks
3. Add metadata (date, context, related files)
4. Save to .caw/insights/{date}-{topic}.md
5. Update insights/index.md
```

**Storage Format:**
```markdown
# Insight: [Extracted Title]

## Metadata
| Field | Value |
|-------|-------|
| **Captured** | 2026-01-04 15:30 |
| **Context** | JWT Authentication Implementation |
| **Related Files** | src/auth/middleware.ts |
| **Phase** | Phase 2: Core Implementation |

## Content
[Original Insight content]

## Tags
#authentication #security #middleware
```

**Directory:**
```
skills/insight-collector/
├── SKILL.md
├── templates/
│   └── insight-template.md
└── scripts/
    └── extract_insights.py   # Insight pattern extraction
```

---

### 3. context-helper
**Agent context understanding and management support**

| Property | Value |
|----------|-------|
| **Trigger** | When Agent needs context |
| **Output** | Relevant context summary |
| **Integration** | All CAW Agents |

**Features:**
```
1. Provide file priority based on context_manifest.json
2. Filter only files needed for current Phase/Step
3. Provide previous Phase result summary
4. Connect related Insights
```

**Agent Usage Example:**
```markdown
## Context Helper Call

Current work: Phase 2, Step 2.3
Required context:
  ✅ src/auth/jwt.ts (created in Phase 2.1)
  ✅ src/auth/middleware.ts (modified in Phase 2.2)
  📋 Related Insight: "JWT Token Refresh Pattern"

Recommended read order:
1. .caw/task_plan.md (current state)
2. src/auth/jwt.ts (dependency)
3. .caw/insights/jwt-refresh-pattern.md
```

**Directory:**
```
skills/context-helper/
├── SKILL.md
└── context-strategies.md   # Context strategy definitions
```

---

### 4. pattern-learner
**Codebase pattern learning and provision to Agents**

| Property | Value |
|----------|-------|
| **Trigger** | Automatic on /cw:start, on Agent request |
| **Output** | Document patterns in `.caw/patterns/` |
| **Integration** | Planner, Builder Agent |

**Learning Targets:**
```
1. Coding style (naming, formatting)
2. Architecture patterns (directory structure, modularization)
3. Test patterns (test file location, naming)
4. Error handling patterns
5. API response format
```

**Output Example:**
```markdown
# Learned Patterns: [Project Name]

## Naming Conventions
- Components: PascalCase (UserProfile.tsx)
- Utilities: camelCase (formatDate.ts)
- Constants: UPPER_SNAKE (MAX_RETRY_COUNT)

## Architecture Patterns
- Feature-based directory structure
- Barrel exports (index.ts)
- Separation: components/ hooks/ utils/

## Testing Patterns
- Test location: __tests__/ alongside source
- Naming: {filename}.test.ts
- Framework: Jest + React Testing Library

## Error Handling
- Custom error classes in errors/
- Try-catch with specific error types
- Consistent error response format
```

**Directory:**
```
skills/pattern-learner/
├── SKILL.md
├── analyzers/
│   ├── style-analyzer.md
│   ├── architecture-analyzer.md
│   └── test-analyzer.md
└── templates/
    └── patterns-template.md
```

---

### 5. decision-logger
**Automatic technical decision logging**

| Property | Value |
|----------|-------|
| **Trigger** | AskUserQuestion response, architecture selection |
| **Output** | Save in ADR format to `.caw/decisions/` |
| **Integration** | Architect, Planner Agent |

**ADR (Architecture Decision Record) Format:**
```markdown
# ADR-001: JWT vs Session Authentication

## Status
Accepted

## Context
User authentication method selection needed.
RESTful API server prefers stateless.

## Decision
Adopt JWT-based authentication

## Rationale
- Stateless: Server scalability
- Mobile support ease
- Microservices compatible

## Consequences
- Token refresh logic needed
- Header size increase due to token size
- Immediate invalidation difficult (blacklist needed)

## Alternatives Considered
1. Session-based: Server memory burden
2. OAuth only: External dependency increase
```

**Directory:**
```
skills/decision-logger/
├── SKILL.md
├── templates/
│   └── adr-template.md
└── scripts/
    └── generate_adr_id.py
```

---

### 6. progress-tracker
**Work progress metric tracking**

| Property | Value |
|----------|-------|
| **Trigger** | Step completion, Phase transition |
| **Output** | Update `.caw/metrics.json` |
| **Integration** | PostToolUse Hook, /cw:status |

**Tracked Metrics:**
```json
{
  "task_id": "auth-jwt-impl",
  "started": "2026-01-04T10:00:00Z",
  "phases": {
    "phase_1": {
      "name": "Setup",
      "started": "2026-01-04T10:00:00Z",
      "completed": "2026-01-04T10:30:00Z",
      "duration_minutes": 30,
      "steps_total": 3,
      "steps_completed": 3
    },
    "phase_2": {
      "name": "Implementation",
      "started": "2026-01-04T10:30:00Z",
      "completed": null,
      "steps_total": 5,
      "steps_completed": 2
    }
  },
  "overall_progress": 0.45,
  "estimated_completion": "2026-01-04T12:00:00Z",
  "blockers": [],
  "insights_captured": 3
}
```

**Directory:**
```
skills/progress-tracker/
├── SKILL.md
└── scripts/
    └── calculate_metrics.py
```

---

### 7. quality-gate
**Quality verification before step completion**

| Property | Value |
|----------|-------|
| **Trigger** | When Builder declares step complete |
| **Output** | Verification result, pass/fail |
| **Integration** | Builder, Reviewer Agent |

**Verification Items:**
```
1. Verify code changes exist
2. Lint/type check pass
3. Related tests pass
4. task_plan.md status update confirmed
5. Pattern compliance check (pattern-learner integration)
```

**Verification Result:**
```
🔍 Quality Gate: Step 2.3

Checks:
  ✅ Code changes detected (3 files)
  ✅ TypeScript compilation passed
  ✅ ESLint passed (0 errors)
  ⚠️ Tests: 2 passed, 1 skipped
  ✅ task_plan.md updated
  ✅ Naming conventions followed

Result: PASSED (with warnings)

Warnings:
  - 1 test skipped in auth.test.ts:45

Proceed to next step? [Y/n]
```

**Directory:**
```
skills/quality-gate/
├── SKILL.md
├── checks/
│   ├── code-checks.md
│   ├── test-checks.md
│   └── pattern-checks.md
└── scripts/
    └── run_checks.py
```

---

### 8. knowledge-base
**Project knowledge accumulation and search**

| Property | Value |
|----------|-------|
| **Trigger** | Agent question, session end |
| **Output** | `.caw/knowledge/` knowledge repository |
| **Integration** | All Agents |

**Knowledge Types:**
```
1. Codebase structure (auto-generated)
2. External dependency information
3. Business logic explanation
4. Troubleshooting records
5. Performance optimization notes
```

**Structure:**
```
.caw/knowledge/
├── index.md                    # Knowledge index
├── codebase/
│   ├── structure.md            # Directory structure
│   └── dependencies.md         # Key dependencies
├── domain/
│   ├── authentication.md       # Domain knowledge
│   └── user-management.md
├── troubleshooting/
│   └── common-errors.md        # Resolved issues
└── performance/
    └── optimization-notes.md
```

**Directory:**
```
skills/knowledge-base/
├── SKILL.md
├── templates/
│   ├── knowledge-entry.md
│   └── troubleshooting-entry.md
└── scripts/
    └── search_knowledge.py
```

---

### ~~9. session-persister~~ (Removed)

> Removed — session/loop state persistence is now handled by Claude Code's built-in `/ralph-loop` feature.

---

### 10. review-assistant
**Code review checklist auto-generation**

| Property | Value |
|----------|-------|
| **Trigger** | When /cw:review executed |
| **Output** | Context-based review checklist |
| **Integration** | Reviewer Agent |

**Checklist Generation:**
```markdown
# Review Checklist: Phase 2 Implementation

## Foundation Information
- Pattern: src/auth/ directory pattern
- Related Decisions: ADR-001 (JWT selection)
- Insights: 3 related Insights

## Auto-Generated Checklist

### Security (JWT related)
- [ ] Is token expiry time appropriate?
- [ ] Is refresh token stored securely?
- [ ] Is token validation logic complete?

### Code Quality
- [ ] Consistent with existing auth patterns?
- [ ] Does error handling follow standards?
- [ ] Is test coverage sufficient?

### Performance
- [ ] Is token validation efficient per request?
- [ ] No unnecessary DB queries?
```

**Directory:**
```
skills/review-assistant/
├── SKILL.md
├── checklists/
│   ├── security-checklist.md
│   ├── performance-checklist.md
│   └── quality-checklist.md
└── templates/
    └── review-template.md
```

---

### 11. commit-discipline (NEW)
**Tidy First commit separation rules enforcement**

| Property | Value |
|----------|-------|
| **Trigger** | Before git commit, when Builder commits |
| **Output** | VALID / INVALID / MIXED_CHANGE_DETECTED |
| **Integration** | PreToolUse Hook (Bash), Builder |

**Core Principle:**
```
"Never mix structural and behavioral changes in the same commit.
Always make structural changes first when both are needed."
— Kent Beck, Tidy First
```

**Commit Types:**
| Type | Icon | Prefix | Description |
|------|------|--------|-------------|
| Tidy | 🧹 | `[tidy]` | Structural changes (no behavior change) |
| Build | 🔨 | `[feat]`, `[fix]` | Behavioral changes (new features, bug fixes) |

**Verification Result:**
```
🧹 Commit Discipline Check

Analyzing staged changes...
  ✅ src/auth/jwt.ts - Tidy (rename, extract method)
  ✅ src/auth/middleware.ts - Tidy (move function)
  ❌ src/routes/login.ts - Build (new endpoint)

Result: MIXED_CHANGE_DETECTED

Recommendation:
1. First commit: Tidy changes only
   git commit -m "[tidy] Extract JWT utilities"
2. Second commit: Build changes
   git commit -m "[feat] Add login endpoint"
```

**Directory:**
```
skills/commit-discipline/
├── SKILL.md
└── change-classifier.md   # Change type classification criteria
```

---

### 12. ~~context-manager~~ (REMOVED)

Removed in v3.1.0 — 1M context window makes packing/pruning unnecessary.

---

### 13. dependency-analyzer (NEW)
**Dependency graph analysis and parallel execution opportunity identification**

| Property | Value |
|----------|-------|
| **Trigger** | /cw:next --parallel |
| **Output** | Dependency graph, parallel execution groups |
| **Integration** | Builder, /cw:next |

**Analysis Targets:**
```
1. Phase level dependencies
2. Step level dependencies
3. File level dependencies
```

**Output Example:**
```
📊 Dependency Analysis

Phase Dependencies:
  Phase 1: Setup → (no deps)
  Phase 2: Core → Phase 1
  Phase 3: API → Phase 2
  Phase 4: Tests → Phase 2, 3 (parallel possible)

Parallel Execution Groups:
  Group A: Steps 2.1, 2.2, 2.3 (independent)
  Group B: Steps 3.1, 3.2 (after Group A)

Parallel Recommendation:
  ✅ Phase 4 can run in parallel with Phase 3
```

**Directory:**
```
skills/dependency-analyzer/
├── SKILL.md
└── analyzers/
    ├── phase-deps.md
    ├── step-deps.md
    └── file-deps.md
```

---

### 14. quick-fix (NEW)
**Simple review issue auto-fix**

| Property | Value |
|----------|-------|
| **Trigger** | /cw:fix execution, after review completion |
| **Output** | Auto-fix results, remaining issues list |
| **Integration** | Reviewer, /cw:fix |

**Auto-Fixable Categories:**
```
1. Magic Numbers → Extract constants
2. Missing Docs → Add JSDoc/docstring
3. Style Violations → Lint auto-fix
4. Import Order → Auto-sort
5. Unused Variables → Remove
```

**Fix Results:**
```
🔧 Quick Fix Results

Fixed (5):
  ✅ src/auth/jwt.ts:23 - Magic number → TOKEN_EXPIRY
  ✅ src/auth/jwt.ts:45 - Added JSDoc
  ✅ src/utils/helpers.ts - Import ordering
  ✅ src/routes/login.ts - Unused import removed
  ✅ src/routes/login.ts:67 - Magic number → MAX_RETRIES

Skipped (2):
  ⏭️ Complex refactoring needed (use /cw:fix --deep)
  ⏭️ Security concern (manual review required)

Summary: 5 fixed, 2 skipped, 0 failed

Issues requiring deep analysis:
- Complex refactoring candidates
- Security-related items
```

**Directory:**
```
skills/quick-fix/
├── SKILL.md
└── fixers/
    ├── magic-numbers.md
    ├── missing-docs.md
    ├── style-fixes.md
    └── import-order.md
```

---

### ~~15. reflect~~ (Removed)

> Removed — reflection/improvement cycles are now handled by Claude Code's built-in `/ralph-loop` feature.

---

### 16. serena-sync (NEW)
**Serena MCP memory synchronization**

| Property | Value |
|----------|-------|
| **Trigger** | /cw:sync, on session end |
| **Output** | Serena memory update |
| **Integration** | Serena MCP, /cw:sync |
| **MCP Server** | serena |

**Memory Schema:**
| Memory Name | Content | Update Source |
|-------------|---------|---------------|
| `project_onboarding` | Project type, framework, conventions, key files | Bootstrapper |
| `domain_knowledge` | Business rules, domain concepts, patterns | Planner, Builder |
| `lessons_learned` | Error resolution, debugging insights, cautions | Builder |
| `workflow_patterns` | Successful workflow approaches, best practices | All agents |

**Sync Operation:**
```
🔄 Serena Sync

Direction: CAW → Serena

Syncing:
  ✅ project_onboarding (unchanged)
  ✅ domain_knowledge (2 new entries)
  ✅ lessons_learned (1 new insight)
  ✅ workflow_patterns (updated)

Result: 4 memories synced
Last sync: 2026-01-21T10:30:00Z
```

**Directory:**
```
skills/serena-sync/
├── SKILL.md
└── schema/
    └── memory-schema.md
```

---

## Hook Integration Design

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "echo 'Session started'" }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "skill", "skill": "progress-tracker" }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "skill", "skill": "commit-discipline" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": { "tool_name": "ExitPlanMode" },
        "hooks": [
          { "type": "skill", "skill": "plan-detector" }
        ]
      },
      {
        "matcher": { "response_pattern": "★ Insight" },
        "hooks": [
          { "type": "skill", "skill": "insight-collector" }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "skill", "skill": "serena-sync" }
        ]
      }
    ]
  }
}
```

---

## Agent-Skill Mapping

| Agent | Skills Used |
|-------|-------------|
| **Bootstrapper** | pattern-learner, knowledge-base |
| **Planner** | pattern-learner, context-helper, decision-logger, dependency-analyzer |
| **Builder** | context-helper, quality-gate, progress-tracker, commit-discipline, quick-fix |
| **Reviewer** | review-assistant, pattern-learner, insight-collector |
| **Fixer** | quick-fix, pattern-learner |
| **ComplianceChecker** | quality-gate, knowledge-base, commit-discipline |
| **Ideator** | knowledge-base, insight-collector |
| **Designer** | pattern-learner, decision-logger |
| **Architect** | decision-logger, knowledge-base, pattern-learner, dependency-analyzer |

---

## Directory Structure

```
context-aware-workflow/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── *.md
├── commands/
│   └── *.md
├── skills/                    # 16 Skills
│   ├── plan-detector/
│   │   └── SKILL.md
│   ├── insight-collector/
│   │   ├── SKILL.md
│   │   └── templates/
│   ├── context-helper/
│   │   └── SKILL.md
│   ├── pattern-learner/
│   │   └── SKILL.md
│   ├── decision-logger/
│   │   └── SKILL.md
│   ├── progress-tracker/
│   │   └── SKILL.md
│   ├── quality-gate/
│   │   └── SKILL.md
│   ├── knowledge-base/
│   │   └── SKILL.md
│   ├── review-assistant/
│   │   └── SKILL.md
│   ├── commit-discipline/      # NEW
│   │   └── SKILL.md
│   ├── dependency-analyzer/    # NEW
│   │   └── SKILL.md
│   ├── quick-fix/              # NEW
│   │   └── SKILL.md
│   ├── reflect/                # NEW
│   │   └── SKILL.md
│   └── serena-sync/            # NEW
│       └── SKILL.md
├── hooks/
│   └── hooks.json
└── docs/
    └── SKILL_DESIGN.md
```

---

## Version History

### v1.7.0 (Current)
- **All 16 skills implemented**
- 6 new skills added:
  - `commit-discipline` - Tidy First commit separation
  - `dependency-analyzer` - Dependency analysis and parallel execution
  - `quick-fix` - Auto-fix
  - `reflect` - Ralph Loop continuous improvement
  - `serena-sync` - Serena MCP sync

### v1.6.0
- Basic 10 skills design complete
- Tidy First methodology integration
- Git Worktree support

### v1.5.0
- Ralph Loop design
- Serena MCP integration plan
