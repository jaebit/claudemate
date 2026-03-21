# arch-guard — Execution Flow

## Overview

arch-guard enforces architecture rules through three mechanisms working together:

```
┌─────────────────────────────────────────────────────┐
│  arch-guard.json  (Single Source of Truth)           │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
     ┌─────▼─────┐         ┌─────▼──────┐
     │   Hooks   │         │   Skills   │
     │ (passive) │         │  (active)  │
     └───────────┘         └────────────┘
  Auto-detect on every      User-invoked for
  Write/Edit/Session        deep analysis
```

- **Hooks** — run automatically in the background, never block
- **Skills** — user-invoked (`/command`) for analysis, generation, and reporting
- **Agent** — user-invoked for comprehensive scoring across all rule categories

---

## Typical Project Lifecycle

```
Phase 1: Setup          Phase 2: Build              Phase 3: Verify & Track
─────────────────       ────────────────────        ─────────────────────────

  /setup                  /scaffold                   /arch-check
    │                       │                           │
    ▼                       ▼                           ▼
  arch-guard.json         /contract-first             /impl-review
  created                   │                           │
    │                       ▼                           ▼
    │                     /implement                  /test-gen
    │                       │                           │
    │                       ▼                           ▼
    │                     /tdd                        /spec-sync
    │                       │                           │
    │                       ▼                           ▼
    │                     (repeat per module)         /track
    │                                                   │
    │                                                   ▼
    └───────────────────────────────────────────▶  arch-reviewer
                                                  (comprehensive score)
```

---

## Phase 1: Setup

### 1. `/setup` — Initialize Configuration

```
User: /setup

arch-guard:
  1. Scans project structure (*.sln, *.csproj, tsconfig.json, etc.)
  2. Asks about layers, reference rules, contracts pattern
  3. Generates arch-guard.json

Output: arch-guard.json at project root
```

After this, **hooks activate automatically**:

| Hook | Trigger | What It Does |
|------|---------|--------------|
| `session-init` | Session start/resume/clear | Injects compressed rule summary into context |
| `layer-check` | Every Write/Edit | Identifies layer + warns on forbidden references |
| `contract-guard` | Every Write | Warns if Contracts project is missing for the layer |
| Stop prompt | End of response | Reminds to run `/arch-check` after source changes |

---

## Phase 2: Build (per module)

### 2. `/scaffold <module>` — Create Module Structure

```
User: /scaffold MyApp.Execution.Workflow

arch-guard:
  1. Identifies layer from config patterns
  2. Checks Contracts-first gate
  3. Creates project directory + project file
  4. Sets up allowed ProjectReferences
  5. Creates test project
  6. Registers in solution

Output: Project structure with correct references
Next:   /contract-first MyApp.Execution.Workflow
```

### 3. `/contract-first <project>` — Define Interfaces Before Implementing

```
User: /contract-first MyApp.Execution.Workflow

arch-guard:
  1. Finds the Contracts project for this layer
  2. Checks if it exists → if not, suggests /scaffold
  3. Checks interface coverage
  4. If gaps found → enters Interface Design Mode
     - Proposes interfaces based on architecture docs
     - User reviews and confirms
     - Generates interface files

Output: Verified Contracts with interfaces defined
Next:   /implement MyApp.Execution.Workflow IStepExecutor
```

### 4. `/implement <project> [interface]` — Generate Stubs + RED Tests

```
User: /implement MyApp.Execution.Workflow IStepExecutor

arch-guard:
  1. Validates project exists, finds Contracts interface
  2. Determines allowed references from config
  3. Checks responsibility boundary against architecture docs
  4. Generates sealed class with NotImplementedException stubs
  5. Generates RED tests (fail against stubs)
  6. Verifies no forbidden patterns in generated code

Output: Implementation stub + RED test file
Next:   /tdd MyApp.Execution.Workflow StepExecutor
```

### 5. `/tdd <project> <class>` — Architecture-Aware TDD Guide

```
User: /tdd MyApp.Execution.Workflow StepExecutor

arch-guard:
  1. Confirms RED state (all tests fail)
  2. Determines method implementation priority
  3. For each method:
     a. Shows applicable architecture rules from config
     b. User/tool implements
     c. Confirms GREEN (test passes)
     d. Suggests Tidy First commit message
  4. REFACTOR phase: review, extract, rename
  5. Final architecture verification

Output: GREEN tests + Tidy First commit suggestions
Next:   /impl-review MyApp.Execution.Workflow
```

### 6. `/adr <title>` — Record Design Decisions (anytime)

```
User: /adr "Why we chose event sourcing for state"

arch-guard:
  1. Determines next ADR number
  2. References architecture docs for context
  3. Generates ADR in Michael Nygard format
  4. User reviews and confirms

Output: docs/adr/ADR-{N}-{slug}.md
```

**Repeat steps 2–5 for each module in the project.**

---

## Phase 3: Verify & Track

### 7. `/arch-check` — Full Compliance Scan

```
User: /arch-check

arch-guard:
  1. Loads all rules from arch-guard.json
  2. Maps all projects to layers
  3. Scans ProjectReferences for forbidden references
  4. Scans using/import statements for namespace violations
  5. Detects forbidden code patterns
  6. Calculates compliance score (if scoring configured)

Output: CRITICAL / WARNING / INFO report with score
Next:   Fix violations → /arch-check (re-verify)
```

### 8. `/impl-review <project>` — Design Compliance Review

```
User: /impl-review MyApp.Execution.Workflow

arch-guard:
  1. Identifies target layer and architecture section
  2. Checks component responsibility boundaries
  3. Checks interface contract compliance
  4. Checks reference rule compliance

Output: Compliant / Violation / Warning report
Next:   /arch-check or /integration-map
```

### 9. `/test-gen [layer]` — Generate Guard-Rail Tests

```
User: /test-gen

arch-guard:
  1. Creates/verifies architecture test project
  2. Generates SolutionHelper (config-driven layer mapping)
  3. Generates ProjectReferenceTests (from references.forbidden)
  4. Generates NamespaceReferenceTests (from references.forbidden)
  5. Generates ForbiddenPatternTests (from forbidden_patterns)
  6. Builds and verifies

Output: Executable xUnit tests codifying config rules
Next:   dotnet test → /arch-check if failures
```

### 10. `/spec-sync` — Design vs Implementation Checklist

```
User: /spec-sync

arch-guard:
  1. Builds expected project list from config + architecture docs
  2. Checks each project: directory exists? project file? source code?
  3. Checks Contracts coverage
  4. Checks test project coverage
  5. Maps to phases (if config.phases defined)
  6. Detects discrepancies (extra projects not in config)

Output: [x]/[ ] checklist with percentages
Next:   /scaffold for missing, /track for progress
```

### 11. `/integration-map <module>` — Change Impact Analysis

```
User: /integration-map MyApp.Execution.Contracts

arch-guard:
  1. Identifies target module's layer
  2. Builds reverse dependency graph (who references this?)
  3. Traces propagation recursively
  4. Classifies: intra-layer vs cross-layer impact

Output: Impact map with propagation paths + test scope
Next:   /arch-check or /impl-review on affected projects
```

### 12. `/track` — Phase Progress

```
User: /track

arch-guard:
  1. Loads phase definitions from config.phases[]
  2. Evaluates each exit criterion
  3. Analyzes git log for development activity
  4. Calculates phase completion percentages

Output: Phase progress bars + exit criteria status
Next:   /scaffold or /contract-first for incomplete items
```

### 13. `arch-reviewer` agent — Comprehensive Fitness Score

```
User: "Run a comprehensive architecture review"

arch-reviewer agent:
  1. Scans all projects, maps to layers
  2. Checks all rule categories:
     - Layer boundary compliance
     - Contracts-first compliance
     - Responsibility boundary
     - Tech stack compliance
     - Forbidden pattern absence
  3. Calculates weighted score → Grade (A/B/C/D)
  4. Produces remediation roadmap by priority

Output: Scored report with grade + prioritized fix list
```

---

## Skill Dependency Graph

```
                        /setup
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
          /scaffold    /adr       /spec-sync
              │                       │
              ▼                       ▼
        /contract-first            /track
              │
              ▼
         /implement
              │
              ▼
           /tdd
              │
     ┌────────┼────────┐
     ▼        ▼        ▼
/impl-review /arch-check /test-gen
     │        │          │
     └────────┼──────────┘
              ▼
      /integration-map
              │
              ▼
       arch-reviewer
```

**Legend**: Arrows show the typical invocation order, not hard dependencies. Any skill can be run independently — it will suggest prerequisites if needed.

---

## Hook + Skill Interaction

```
Developer writes code
        │
        ▼
  ┌─────────────┐     layer-check hook fires
  │  Write/Edit │────────────────────────────▶ "WARNING: {project} (L3)
  └─────────────┘                               references {forbidden} (L4)"
        │
        ▼                contract-guard hook fires
  ┌─────────────┐────────────────────────────▶ "WARNING: No Contracts project
  │  Write new  │                               for this layer"
  │  source file│
  └─────────────┘
        │
        ▼                Stop prompt fires
  ┌─────────────┐────────────────────────────▶ "Source files modified.
  │  Response   │                               Consider running /arch-check"
  │  complete   │
  └─────────────┘
        │
        ▼
  User runs /arch-check for full verification
```

Hooks provide **real-time awareness** during development. Skills provide **thorough verification** on demand. The agent provides a **comprehensive score** at milestones.
