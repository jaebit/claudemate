# Phase Artifacts Contract

What each phase produces and consumes. All paths relative to project root.

## Phase 1: RESEARCH

- **Produces**: `.caw/research/<slug>/RESEARCH-REPORT.md`
- **Produces**: `.autopilot/deferred-questions.md` (append)

## Phase 2: DESIGN

- **Consumes**: `.caw/research/<slug>/RESEARCH-REPORT.md`
- **Consumes**: `arch-guard.json` (if exists)
- **Produces**: `.caw/design/architecture.md`
- **Produces**: `.debate/<id>/report.md` (if debate ran)
- **Produces**: `.autopilot/design-brief.md` (consolidated)
- **Produces**: `.autopilot/deferred-questions.md` (append)

## Phase 3: BUILD

- **Consumes**: `.autopilot/design-brief.md`
- **Consumes**: `arch-guard.json` (if exists)
- **Produces**: source code (project files)
- **Produces**: `.caw/auto-state.json`
- **Produces**: `.caw/task_plan.md`

## Phase 4: REVIEW

- **Consumes**: source code (changed files)
- **Consumes**: `.autopilot/design-brief.md`
- **Consumes**: `arch-guard.json` (if exists)
- **Produces**: `.autopilot/review-results.md`

## Phase 5: REPORT

- **Consumes**: all above artifacts
- **Produces**: `.autopilot/REPORT.md`

## State

- **All phases**: `.autopilot/state.json` (read/write)
