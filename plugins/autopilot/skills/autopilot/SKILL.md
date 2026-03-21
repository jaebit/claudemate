---
name: autopilot
description: >
  End-to-end autonomous coding pipeline. Use when the user says "autopilot",
  "build this from scratch", "go from idea to code", "autonomous build",
  or wants to go from a topic/idea to working code with a single command.
  Orchestrates crew, multi-model-debate, codex-harness, and arch-guard.
argument-hint: "<topic> [flags]"
user_invocable: true
disable-model-invocation: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - Skill
  - AskUserQuestion
---

# /autopilot — Autonomous Coding Pipeline

End-to-end pipeline: idea → research → design → build → review → report.

## Arguments

**Invoked as**: $ARGUMENTS

## Current State

- **Autopilot state**: !`cat .autopilot/state.json 2>/dev/null | head -20 || echo "(no state)"`
- **Arch-guard config**: !`test -f arch-guard.json && echo "DETECTED" || echo "NOT_FOUND"`
- **CW initialized**: !`test -d .caw && echo "YES" || echo "NO"`

## Flags

| Flag | Effect |
|------|--------|
| `--skip-research` | Skip Phase 1, start at design |
| `--skip-debate` | Skip debate sub-step in Phase 2 |
| `--no-arch` | Force-skip arch-guard even if config exists |
| `--from-plan <path>` | Skip Phase 1+2, use existing design doc as design-brief |
| `--continue` | Resume from `.autopilot/state.json` |
| `--verbose` | Detailed per-phase progress |
| `--no-questions` | Minimize interactive prompts (still shows user gate) |

## Pipeline Overview

```
[1/5] RESEARCH    crew:explore --research-deep           autonomous
[2/5] DESIGN      crew:explore --arch + debate + arch    autonomous → USER GATE
[3/5] BUILD       arch-guard scaffold + crew:go           autonomous
[4/5] REVIEW      codex + arch-check + crew:review        autonomous (parallel)
[5/5] REPORT      synthesis                              autonomous
```

---

## Initialization

1. Parse flags from `$ARGUMENTS`. Extract `<topic>` (everything that isn't a flag).
2. If `--continue`: read `.autopilot/state.json`.
   - If `phase == "complete"` AND `completion.missing > 0`: **gap-filling mode** — read `.autopilot/remaining-work.md`, set `phase = "build"`, `build.status = "pending"`, and resume from Phase 3 using remaining-work.md as the task description for crew:go.
   - Otherwise: find first phase with status != `complete` and != `skipped`, resume from there. Skip to that phase section below.
3. If `--from-plan <path>`: read the file at `<path>`, copy its content to `.autopilot/design-brief.md`, skip to Phase 3.
4. Create `.autopilot/` directory.
5. Write initial `.autopilot/state.json`:

```json
{
  "schema_version": "1.1",
  "topic": "<topic>",
  "phase": "research",
  "started_at": "<ISO timestamp>",
  "config": {
    "skip_research": false,
    "skip_debate": false,
    "no_arch": false,
    "arch_guard_detected": false,
    "verbose": false,
    "no_questions": false
  },
  "phases": {
    "research": { "status": "pending" },
    "design": { "status": "pending", "user_approved": false, "revision_count": 0 },
    "build": { "status": "pending" },
    "review": { "status": "pending", "rounds": 0 },
    "report": { "status": "pending" }
  },
  "deliverables": [],
  "completion": {
    "total": 0,
    "built": 0,
    "missing": 0,
    "verdict": "pending"
  },
  "gap_fill_round": 0,
  "last_error": null
}
```

6. Detect arch-guard: if `arch-guard.json` exists and `--no-arch` not set, set `config.arch_guard_detected = true`.
7. Apply flag overrides to `config`.

Print: `AUTOPILOT started: "<topic>"`

---

## Completion Status Protocol

Every phase ends with one of:
- **DONE** — phase completed successfully, proceed to next
- **DONE_WITH_CONCERNS** — completed but issues noted in state; proceed
- **BLOCKED** — cannot proceed; save state, report to user
- **NEEDS_CONTEXT** — missing info; append to `.autopilot/deferred-questions.md`

On BLOCKED: save state and stop. User can `--continue` after resolving.
On 3 consecutive failures in the same phase: stop and suggest manual skill invocation.

---

## Phase 1: RESEARCH [1/5] (autonomous)

**Skip if**: `--skip-research` flag is set → mark `research.status = "skipped"`, go to Phase 2.

1. Print `[1/5] Researching...`
2. Update state: `research.status = "running"`, `phase = "research"`
3. Invoke via Agent tool: spawn an agent with prompt `"/crew:explore --research-deep <topic>"`
4. On success:
   - Locate output at `.caw/research/<slug>/RESEARCH-REPORT.md`
   - Save path to `research.report_path` in state
   - Scan report for open questions or ambiguities → append to `.autopilot/deferred-questions.md`
   - Set `research.status = "complete"`
   - Print `[1/5] Research complete`
5. On failure:
   - Set `research.status = "failed"`, record error in `last_error`
   - Print `[1/5] Research failed: <error>. Use --continue to retry or --skip-research to skip.`
   - Stop.

---

## Phase 2: DESIGN [2/5] (autonomous → user gate)

**Skip if**: `--from-plan` was used → already skipped.

1. Print `[2/5] Designing...`
2. Update state: `design.status = "running"`, `phase = "design"`

### 2a — Architecture Design

- Read the research report (from `research.report_path` or locate in `.caw/research/`)
- Invoke via Agent tool: spawn an agent with prompt `"/crew:explore --arch <topic>"`, providing research report context
- Output: `.caw/design/architecture.md`
- Collect any design questions → append to `.autopilot/deferred-questions.md`

### 2b — Multi-Model Debate (conditional)

- **Skip if**: `--skip-debate` flag is set OR `multi-model-debate` plugin is not available
- Check availability: attempt to verify debate skill exists
- If available:
  - Read `.caw/design/architecture.md`, extract top 2-3 key design decisions (component boundaries, technology choices, data model approaches)
  - For each decision: invoke `Skill("multi-model-debate:debate-orchestration")` with the decision as topic
  - Fold consensus results into the architecture doc
- If unavailable: print `[2/5] Debate skipped (multi-model-debate plugin not found)`

### 2c — Architecture Constraints (conditional)

- **Skip if**: `config.arch_guard_detected` is false OR `--no-arch` is set
- If active:
  - Invoke `Skill("arch-guard:arch-check")` to surface existing layer/reference constraints
  - Fold constraints into design doc
- If arch-guard.json absent but project looks like layered architecture:
  - Print info: `Consider running /arch-guard:setup to define architecture rules (skipping for now)`

### 2d — Consolidate Design Brief

- Read `.caw/design/architecture.md` (+ debate reports if any + arch-guard constraints if any)
- Merge into `.autopilot/design-brief.md` with sections:
  - **Overview**: what is being built and why
  - **Components**: key modules/services with responsibilities
  - **Tech Decisions**: chosen approaches (with debate consensus if available)
  - **Data Model**: entities and relationships
  - **Architecture Constraints**: from arch-guard (if active)
  - **Open Questions**: from `.autopilot/deferred-questions.md`

### 2d.1 — Extract Deliverables

After writing `.autopilot/design-brief.md`, parse it and extract every **concrete deliverable**: files to create, classes/interfaces to implement, configuration files, test files, app manifests, migration scripts.

For each deliverable, record in `state.json` under `"deliverables"` array:
- `id`: sequential identifier (d1, d2, ...)
- `name`: short name (e.g., "AgentStepExecutor")
- `type`: one of `file`, `class`, `interface`, `function`, `config`, `directory`, `test`
- `expected_path`: best-guess file path where this should exist after build
- `source_section`: which design-brief section it came from (e.g., "Components", "Data Model")
- `status`: `"pending"`

Set `completion.total` to the deliverable count. Leave `completion.verdict` as `"pending"`.

**Extraction heuristic**: scan design-brief sections (Components, Data Model, Build Sequence, Tests) for nouns that map to code artifacts. Include both interfaces AND their expected implementations. Include test projects. Include infrastructure configs (Docker, migrations).

### 2e — USER GATE

Present to the user via `AskUserQuestion`:

```
## Autopilot Design Review

### What will be built
<brief summary from design-brief>

### Key components
<component list>

### Tech decisions
<decisions with debate results if any>

### Planned Deliverables ({completion.total} items)
<table: name | type | expected_path — from state.json deliverables>

### Architecture constraints
<from arch-guard, or "none active">

### Open questions
<from deferred-questions.md, or "none">

---
Options:
1. **Approve** — proceed to build ({completion.total} deliverables)
2. **Revise** — provide feedback (I'll re-design, max 3 rounds)
3. **Abort** — cancel pipeline
```

- On **Approve**: set `design.user_approved = true`, `design.status = "complete"`, print `[2/5] Design approved`
- On **Revise**: write feedback to `.autopilot/design-feedback.md`, increment `design.revision_count`, re-run 2a with feedback as additional context. Max 3 revision rounds; after 3, present final version and require approve or abort.
- On **Abort**: set `phase = "cancelled"`, `design.status = "cancelled"`, print `AUTOPILOT_CANCELLED`, stop.

---

## Phase 3: BUILD [3/5] (autonomous)

1. Print `[3/5] Building...`
2. Update state: `build.status = "running"`, `phase = "build"`

### 3a — Arch-guard Scaffolding (conditional)

- **Skip if**: `config.arch_guard_detected` is false
- If active and design-brief identifies layered modules:
  - For each identified module/layer: invoke `Skill("arch-guard:scaffold")` with the module name
  - Then invoke `Skill("arch-guard:contract-first")` to define interfaces
  - Optionally invoke `Skill("arch-guard:implement")` for interface stubs

### 3b — CW Go Execution

- Transform `.autopilot/design-brief.md` content into a task description suitable for crew:go
- Invoke via Agent tool: spawn an agent with prompt `"/crew:go <design-brief summary> --from-plan --skip-expansion --no-questions"`
  - If `.caw/task_plan.md` doesn't exist yet, let crew:go create it from the design brief
  - crew:go handles its own 9-stage pipeline (planning, execution, QA, review, fix, check)
- On success:
  - Run **3b.1 — Verify Deliverables** (see below)
  - Set `build.status = "complete"`, `build.cw_state_path = ".caw/auto-state.json"`
  - Print `[3/5] Build complete ({completion.built}/{completion.total} deliverables)`

### 3b.1 — Verify Deliverables

After crew:go completes, iterate through every entry in `state.json.deliverables`:

- **type `file` / `config` / `directory`**: check if `expected_path` exists (use Bash: `test -f` or `test -d`)
- **type `class` / `interface` / `function`**: Grep `expected_path` (or project-wide if path is approximate) for the declaration keyword (`class <name>`, `interface <name>`, `function <name>`, `def <name>`)
- **type `test`**: check file exists AND contains at least one test attribute/decorator (`[Fact]`, `[Test]`, `@Test`, `def test_`, etc.)

Update each deliverable:
- Found → `status = "built"`
- Not found → `status = "missing"`
- File exists but declaration missing → `status = "partial"`

Compute and write to `state.json`:
- `completion.built` = count of status == "built"
- `completion.missing` = count of status == "missing" or "partial"
- `completion.total` = deliverables.length
- `completion.verdict`:
  - `"complete"` if missing == 0
  - `"partial"` if missing > 0 AND built >= 50% of total
  - `"minimal"` if built < 50% of total

**Note**: `build.status` remains `"complete"` regardless — the build itself didn't fail, it scoped down. The gap information flows to review and report.

### 3b.2 — Auto-Setup Arch-Guard (conditional)

If `config.arch_guard_detected` is false AND the built project appears to have layered architecture (multiple projects/modules with clear layer boundaries — e.g., Contracts/Domain/Infrastructure/Api/Hosts pattern, or src/ with 3+ subprojects):

1. Invoke `Skill("arch-guard:setup")` to generate `arch-guard.json` from the project structure
2. If setup succeeds: set `config.arch_guard_detected = true`, update `state.json`
3. Print `[3/5] arch-guard.json auto-generated — architecture checks enabled for review`
4. If setup fails or no layered pattern detected: skip silently

This ensures Phase 4 Stream B (Architecture Review) runs even when the project was scaffolded from scratch by autopilot.

### 3b.3 — Auto-Generate Architecture Tests (conditional)

If `config.arch_guard_detected` is true (either pre-existing or just created in 3b.2):

1. Invoke `Skill("arch-guard:test-gen")` to generate architecture guard-rail tests (layer dependency, reference direction, etc.)
2. Run the generated tests (e.g., `dotnet test`, `npm test`, etc.) to verify they pass against the current build
3. If tests pass: print `[3/5] Architecture tests generated and passing`
4. If tests fail: log failures but do not block — they will be surfaced in Phase 4 review

This catches layer violations and missing integrations immediately after build, rather than leaving them as manual "Next Steps".

- On failure:
  - Set `build.status = "failed"`, record error
  - Print `[3/5] Build failed. Use /autopilot --continue to retry (delegates to crew:go --continue).`
  - Stop.

---

## Phase 4: REVIEW [4/5] (autonomous, parallel)

1. Print `[4/5] Reviewing...`
2. Update state: `review.status = "running"`, `phase = "review"`, increment `review.rounds`

### Dispatch 3 Review Streams in Parallel

Use the Agent tool — send a single message with up to 3 Agent calls:

**Stream A — Codex Review** (conditional):
- If `codex-harness` plugin is available: spawn an Agent that invokes the codex MCP tool with a review prompt covering the changed files
- If unavailable: skip, note in results

**Stream B — Architecture Review** (conditional):
- If `config.arch_guard_detected` is true (either pre-existing or auto-generated in 3b.2): spawn an Agent that runs `Skill("arch-guard:arch-check")` and `Skill("arch-guard:impl-review")` on the changed files
- Produces architecture fitness score
- If not active: skip, note in results

**Stream C — CW Review**:
- Invoke via Agent tool: spawn an agent with prompt `"/crew:review --all"` for functional, security, and quality review

**Stream D — Completeness Review** (conditional):
- If `state.json.completion.verdict != "complete"`:
  - Read `state.json.deliverables` where status == `missing` or `partial`
  - For each missing deliverable, search the codebase for evidence of intentional deferral: TODO/FIXME comments mentioning the deliverable name, stub files, "Phase 2"/"next sprint" references
  - Classify each gap as:
    - `intentional_deferral` — stub or TODO exists, explicitly deferred
    - `oversight` — nothing exists, not mentioned anywhere
    - `partial` — file exists but implementation is incomplete
  - Append gap classification to `.autopilot/review-results.md` under a "## Completeness Gaps" section

### Cross-Model Validation

When reviews complete, compare findings:
- Findings unique to Codex (if ran)
- Findings unique to Claude (crew:review)
- Findings both found → high-confidence issues
- Disagreements → flag for deeper investigation

### Auto-Fix Loop (max 3 rounds)

- Aggregate all results into `.autopilot/review-results.md`
- If issues with severity >= major exist:
  - Invoke via Agent tool: spawn an agent with prompt `"/crew:review --fix"` to auto-fix
  - Re-run review streams (increment `review.rounds`)
  - Max 3 rounds total
- After max rounds with remaining issues: mark as DONE_WITH_CONCERNS (don't block)

### Review Readiness Dashboard

Write to `.autopilot/review-results.md` and print:

```
| Review Stream     | Status             | Score              |
|-------------------|--------------------|---------------------|
| Codex Review      | DONE / SKIPPED     | —                   |
| Architecture      | DONE / SKIPPED     | B (82)              |
| CW Review         | DONE_WITH_CONCERNS | 2 minor             |
| Completeness      | DONE / SKIPPED     | 8/12 (4 missing)    |
| Cross-Model Check | DONE               | 1 divergence        |
```

Set `review.status` based on overall result. Print `[4/5] Review complete`.

---

## Phase 5: REPORT [5/5] (autonomous)

1. Print `[5/5] Generating report...`
2. Update state: `report.status = "running"`, `phase = "report"`
3. Read all artifacts:
   - `.autopilot/design-brief.md`
   - `.autopilot/review-results.md`
   - `.caw/research/<slug>/RESEARCH-REPORT.md` (if exists)
   - Run `git diff --stat` for file change summary
4. Write `.autopilot/REPORT.md`:

```markdown
# Autopilot Report

## Topic
{topic}

## What Was Built
{summary from design-brief + component list}

## Architecture Score
{from arch-reviewer, or "N/A — arch-guard not active"}

## Review Results
{from review-results.md — issues found, fixed, remaining}

## Completeness
{table from state.json.deliverables: name | type | status (BUILT/MISSING/PARTIAL) | expected_path}

**Verdict**: {completion.verdict} ({completion.built}/{completion.total} deliverables built, {completion.missing} missing)

## Remaining Work
{if completion.missing > 0: numbered list of missing deliverables with name, type, path, and brief description of what needs to be implemented}
{if completion.missing == 0: "All designed deliverables were built."}

## Files Created/Modified
{git diff --stat output}

## Suggested Commit Message
{conventional commit message based on what was built}
```

5. If `completion.missing > 0`: also write `.autopilot/remaining-work.md` as a standalone file containing the Remaining Work section. This file is structured for use as input to gap-filling.
6. Set `report.status = "complete"`, `report.report_path = ".autopilot/REPORT.md"`

### 5a — Auto Gap-Fill Loop (max 1 round)

If `completion.missing > 0` AND this is NOT already a gap-fill round (check `state.gap_fill_round` — default 0):

1. Print: `[5/5] Gaps detected ({completion.missing} items) — auto gap-filling...`
2. Set `state.gap_fill_round = 1`
3. Loop back to **Phase 3b** (crew:go with `.autopilot/remaining-work.md` as task input, `--from-plan --skip-expansion --no-questions`)
4. Then re-run **Phase 4** (review) and **Phase 5** (report) as normal
5. If gaps remain after 1 gap-fill round → proceed to completion with COMPLETE_WITH_GAPS (don't loop indefinitely)

If `completion.missing == 0` OR `state.gap_fill_round >= 1` → proceed to step 7.

### 5b — Final Completion

7. Set `phase = "complete"`
8. Print the report content, then the completion signal:

If `completion.verdict == "complete"` (or `deliverables` array is empty — backward compat):
```
---
SIGNAL: AUTOPILOT_COMPLETE
---
```

If `completion.verdict == "partial"` or `"minimal"`:
```
---
SIGNAL: AUTOPILOT_COMPLETE_WITH_GAPS ({completion.built}/{completion.total} deliverables)
Remaining: .autopilot/remaining-work.md
Use /autopilot --continue to build remaining items.
---
```

---

## Error Handling

| Phase | On Failure | Recovery |
|-------|-----------|----------|
| Research | Log error, mark failed, stop | `--continue` retries, or `--skip-research` |
| Design | Preserve partial artifacts, stop | `--continue` retries with existing research |
| Build | crew:go has 5-level error recovery | `--continue` delegates to `crew:go --continue` |
| Review | Individual stream failure = skip that stream | Report notes which reviews ran |
| Report | Should not fail (read-only synthesis) | `--continue` retries |

Global: 3 consecutive failures on the same phase → suggest manual skill invocation for that phase.

---

## Progress Display

```
/autopilot "build a notification system"

AUTOPILOT started: "build a notification system"

[1/5] Researching...        done
[2/5] Designing...          done (user approved)
[3/5] Building...           done (8 steps, 12 files)
[4/5] Reviewing...          done (3 streams, 1 fix round)
[5/5] Generating report...  done

Report: .autopilot/REPORT.md

---
SIGNAL: AUTOPILOT_COMPLETE
---
```

## Boundaries

**Will:**
- Create `.autopilot/` directory and all artifacts within it
- Invoke crew:explore, crew:go, crew:review via Agent tool (spawning agents that run the slash commands, since these skills have disable-model-invocation)
- Invoke multi-model-debate:debate-orchestration via Skill tool (if available)
- Invoke arch-guard skills via Skill tool (if arch-guard.json exists)
- Invoke codex MCP tool via Agent (if codex-harness available)
- Present one user gate after design phase via AskUserQuestion
- Read/write `.autopilot/state.json` for resume support
- Run `git diff --stat` for reporting

**Won't:**
- Reimplement logic from crew, debate, codex, or arch-guard plugins
- Push to remote or create PRs automatically
- Skip the user gate (Phase 2e) unless `--from-plan` is used
- Continue past 3 consecutive failures without stopping
- Modify files outside `.autopilot/` except through delegated skills
