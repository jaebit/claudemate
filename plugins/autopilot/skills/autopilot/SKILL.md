---
name: autopilot
description: >
  End-to-end autonomous coding pipeline. Use when the user says "autopilot",
  "build this from scratch", "go from idea to code", "autonomous build",
  or wants to go from a topic/idea to working code with a single command.
  Orchestrates crew, multi-model-debate, and arch-guard.
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
| `--worktree` | Isolate each build step in a git worktree (create → build → merge back) |

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
5. **Ensure git repository**: run `git rev-parse --git-dir 2>/dev/null`. If not a git repo, run `git init` and create an initial commit (`git add -A && git commit -m "chore: initial commit (pre-autopilot)"`). This is required because crew agents use git worktrees for isolation.
6. Write initial `.autopilot/state.json`:

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
    "no_questions": false,
    "worktree": false
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

7. Detect arch-guard: if `arch-guard.json` exists and `--no-arch` not set, set `config.arch_guard_detected = true`.
8. Apply flag overrides to `config`.

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
  - **Architecture Governance**: see decision criteria below
  - **Architecture Constraints**: from arch-guard (if active)
  - **Open Questions**: from `.autopilot/deferred-questions.md`

#### Architecture Governance Decision

During design consolidation, evaluate whether arch-guard should be enabled. Write the decision in the "Architecture Governance" section of design-brief.md.

**Enable arch-guard when ANY of these apply:**
- Multi-project/multi-package structure (e.g., .NET solution, Java modules, monorepo packages)
- Explicit layer boundaries in design (Domain/Application/Infrastructure/Presentation)
- Module boundaries with directional dependency rules (e.g., "API must not reference DB directly")
- 3+ distinct bounded contexts or services

**Skip arch-guard when ALL of these apply:**
- Single-project, flat structure (e.g., one Next.js app with `src/` only)
- No explicit layer or module boundaries in design
- < 10 source files expected

If enabling: set `config.arch_guard_detected = true` in state.json, then invoke `Skill("arch-guard:setup")` to generate `arch-guard.json` from the design. This runs BEFORE the user gate so the user can review the rules.

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

### Architecture governance
<"arch-guard enabled — {N} rules" or "arch-guard skipped — {reason}">

### Architecture constraints
<from arch-guard rules, or "N/A">

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

### 2f — ADR Generation (conditional)

- **Skip if**: `config.no_arch` is set OR design-brief has no "Tech Decisions" section
- Read `.autopilot/design-brief.md`, extract each entry from the "Tech Decisions" section
- For each key decision:
  - Invoke `Skill("arch-guard:adr", "<decision title>")` with context:
    - Decision rationale from design-brief
    - Debate consensus (if Phase 2b ran)
    - Alternatives considered
  - arch-guard:adr will auto-create `docs/adr/` directory if missing
- Record generated ADR paths in state: `design.adr_paths = [<paths>]`
- Print: `[2/5] {N} ADR(s) generated`

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

### 3b — Build Execution (Step-by-Step Loop)

**CRITICAL**: YOU (autopilot) execute the build loop yourself. Do NOT delegate the entire build to a single agent. Execute each step individually with commit + simplify between steps.

#### 3b.0 — Create Task Plan

If `.caw/task_plan.md` does not exist, create it:
- Spawn `Agent(subagent_type="crew:planner")` with prompt: the design-brief content + "Create a task plan in `.caw/task_plan.md` with phases and steps."
- Wait for planner to complete and verify `.caw/task_plan.md` exists.

#### 3b.1-loop — Execute Each Step

Read `.caw/task_plan.md`. For each pending step, execute this sequence:

**If `config.worktree` is true — Worktree-Isolated Mode:**

**a. Create worktree** — Invoke worktree:create for this step:
```
Skill("worktree:create", "step-{N}")
```
This creates `.worktrees/step-{N}` with a branch `step-{N}`.

**b. Build** — Spawn Builder to work INSIDE the worktree:
```
Agent(subagent_type="crew:builder", prompt="Implement Step {N}: {step description}. Context files: {list}. IMPORTANT: Work in directory .worktrees/step-{N}/ — all file reads/writes must be relative to that directory. When done, commit your changes with: cd .worktrees/step-{N} && git add -A && git commit -m '[feat] Step {N}: {step description}'")
```
Wait for builder to complete.

**c. Merge back** — Invoke worktree:merge from the worktree context:
```
Skill("worktree:merge", "")
```
Note: worktree:merge must be invoked from inside the worktree. If the Skill tool cannot change cwd, run manually:
```bash
cd .worktrees/step-{N} && git status --porcelain
```
If worktree has uncommitted changes, commit them first. Then merge from the main repo:
```bash
BRANCH="step-{N}"
REPO_ROOT=$(git rev-parse --show-toplevel)
ORIGINAL_REPO=$(cd "$REPO_ROOT" && git rev-parse --git-common-dir | xargs dirname)
git -C "$ORIGINAL_REPO" merge --squash "$BRANCH"
git -C "$ORIGINAL_REPO" commit -m "[feat] Step {N}: {step description}"
```

**d. Simplify** — Spawn code-simplifier on modified files:
```
Agent(subagent_type="code-simplifier:code-simplifier", prompt="Simplify the files modified in Step {N}: {file list}")
```

**e. Tidy commit** — Run Bash directly:
```bash
git status --porcelain
```
If output is non-empty:
```bash
git add -A
git commit -m "[tidy] Simplify Step {N}"
```

**f. Cleanup** — Remove the worktree:
```bash
git worktree remove .worktrees/step-{N} 2>/dev/null
git branch -d step-{N} 2>/dev/null
```

**g. Next** — Proceed to the next pending step. Repeat a-f.

---

**If `config.worktree` is false — Default Mode (no isolation):**

**a. Build** — Spawn Builder for THIS step only:
```
Agent(subagent_type="crew:builder", prompt="Implement Step {N}: {step description}. Context files: {list}.")
```
Wait for builder to complete.

**b. Commit** — Run these Bash commands directly (do NOT delegate):
```bash
git status --porcelain
```
If output is non-empty:
```bash
git add -A
git commit -m "[feat] Step {N}: {step description}"
```

**c. Simplify** — Spawn code-simplifier on modified files:
```
Agent(subagent_type="code-simplifier:code-simplifier", prompt="Simplify the files modified in Step {N}: {file list}")
```

**d. Tidy commit** — Run Bash directly:
```bash
git status --porcelain
```
If output is non-empty:
```bash
git add -A
git commit -m "[tidy] Simplify Step {N}"
```

**e. Next** — Proceed to the next pending step. Repeat a-d.

#### 3b.2 — Completion

After all steps complete:
- Run **3b.3 — Verify Deliverables** (see below)
- Set `build.status = "complete"`
- Print `[3/5] Build complete ({completion.built}/{completion.total} deliverables)`

### 3b.3 — Verify Deliverables

After build loop completes, iterate through **every** entry in `state.json.deliverables` and update **both** the individual `status` field **and** the `completion` summary.

**CRITICAL**: You MUST update each deliverable's `status` field in the `deliverables` array. Do NOT only update `completion` counts — the per-item `status` is required for reporting, gap-filling, and `--continue` resume.

**Check rules by type:**
- **`file` / `config` / `directory`**: check if `expected_path` exists (use Bash: `test -f` or `test -d`)
- **`class` / `interface` / `function`**: Grep `expected_path` (or project-wide if path is approximate) for the declaration keyword (`class <name>`, `interface <name>`, `function <name>`, `def <name>`)
- **`test`**: check file exists AND contains at least one test attribute/decorator (`[Fact]`, `[Test]`, `@Test`, `def test_`, etc.)

**Update each deliverable in the `deliverables` array:**
- Found → set `"status": "built"`
- Not found → set `"status": "missing"`
- File exists but declaration missing → set `"status": "partial"`

Example — before:
```json
{ "id": "d1", "name": "FooService", "type": "class", "expected_path": "src/Foo.cs", "status": "pending" }
```
After verification (file exists, class declaration found):
```json
{ "id": "d1", "name": "FooService", "type": "class", "expected_path": "src/Foo.cs", "status": "built" }
```

**Then compute `completion` from the updated statuses:**
- `completion.built` = count where status == `"built"`
- `completion.missing` = count where status == `"missing"` or `"partial"`
- `completion.total` = deliverables.length
- `completion.verdict`:
  - `"complete"` if missing == 0
  - `"partial"` if missing > 0 AND built >= 50% of total
  - `"minimal"` if built < 50% of total

**Write the full updated `state.json`** with both the modified `deliverables` array and the `completion` summary.

**Note**: `build.status` remains `"complete"` regardless — the build itself didn't fail, it scoped down. The gap information flows to review and report.

### 3c — Auto-Setup Arch-Guard Fallback (conditional)

**Skip if**: `config.arch_guard_detected` is already true (set in Phase 2d) OR `config.no_arch` is set.

Fallback for cases where Phase 2d didn't enable arch-guard but the built project grew into a multi-module structure:

1. Check if the built project has 3+ subprojects/packages with clear boundaries
2. If yes: invoke `Skill("arch-guard:setup")`, set `config.arch_guard_detected = true`
3. If no: skip silently

### 3d — Auto-Generate Architecture Tests (conditional)

If `config.arch_guard_detected` is true (either pre-existing or just created in 3c):

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
- If `codex` CLI is available (`which codex` returns 0): spawn an Agent that runs `codex -q "Review these changed files for bugs, security issues, and code quality: {file list}"` via Bash tool
- If unavailable: skip, note in results

**Stream B — Architecture Review** (conditional):
- If `config.arch_guard_detected` is true (either pre-existing or auto-generated in 3c): spawn an Agent that runs `Skill("arch-guard:arch-check")` and `Skill("arch-guard:impl-review")` on the changed files
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
3. Loop back to **Phase 3b** — run the step-by-step build loop using `.autopilot/remaining-work.md` as the task plan source
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

## Remote Invocation

This skill has `disable-model-invocation: true`, which means the Skill tool cannot invoke it directly. This affects any context where a model needs to call `/autopilot` on behalf of a user (e.g., Telegram bots, remote chat interfaces, programmatic orchestration).

**Workaround**: Use the Agent tool to spawn a subagent that runs the skill:

```
Agent(prompt="/autopilot <topic> [flags]")
```

The subagent gets a fresh context, loads the skill content, and executes the full pipeline. This is the same pattern autopilot itself uses to invoke crew skills (crew:explore, crew:go, crew:review) which also have `disable-model-invocation`.

---

## Boundaries

**Will:**
- Create `.autopilot/` directory and all artifacts within it
- Invoke crew:explore, crew:go, crew:review via Agent tool (spawning agents that run the slash commands, since these skills have disable-model-invocation)
- Invoke multi-model-debate:debate-orchestration via Skill tool (if available)
- Invoke arch-guard skills via Skill tool (if arch-guard.json exists), including arch-guard:adr for ADR generation
- Invoke codex CLI via Agent (if codex CLI available)
- Present one user gate after design phase via AskUserQuestion
- Read/write `.autopilot/state.json` for resume support
- Run `git diff --stat` for reporting

**Won't:**
- **Write source code directly** — ALL code generation MUST go through crew:go (Phase 3b). Never use Write/Edit tools to create source files yourself. Never spawn a general-purpose Agent to write code. This is the single most important boundary.
- Reimplement logic from crew, debate, codex, or arch-guard plugins
- Push to remote or create PRs automatically
- Skip the user gate (Phase 2e) unless `--from-plan` is used
- Continue past 3 consecutive failures without stopping
- Modify files outside `.autopilot/` except through delegated skills
