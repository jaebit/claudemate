---
name: track
description: >
  This skill should be used when the user asks "show progress", "what phase are we in?", "track",
  "roadmap status", "milestone progress", or wants phase-based progress percentages with exit
  criteria fulfillment rates — for structural presence checklists (exists/not exists) use
  spec-sync instead.
user_invocable: false
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /track — Phase-Based Roadmap Progress

Analyzes git log, source structure, and test status to calculate phase-based progress percentages.

## Reference

Read `arch-guard.json` from the project root before starting. This is the single source of truth for all rules.

## Procedure

### Step 1: Load Phase Definitions

Read `config.phases[]` from `arch-guard.json`.

If `config.phases` is not defined or empty:
```
WARNING: No phases defined in arch-guard.json.
To use /track, add a "phases" section to your config with phase names, projects, and exit criteria.
You can still use /spec-sync to check structural presence.
```
Stop here if no phases are defined.

Each phase should have:
- `name` — phase name
- `projects[]` — projects belonging to this phase
- `exit_criteria[]` — conditions that must be met to complete the phase

### Step 2: Exit Criteria Evaluation

For each phase's exit criteria, translate into verifiable conditions:

- **Project exists**: Check if project directory and project file exist
- **Interface defined**: Check Contracts project for interface files
- **Tests passing**: Run test command and check results
- **File exists**: Check for specific required files
- **Custom check**: Read the criterion and evaluate based on file/code analysis

### Step 3: Git Log Analysis

Analyze recent commit activity for each phase's projects:

```bash
git log --oneline --since="2 weeks ago" -- {source_root}/{project_pattern}*
```

Count commits per phase to show development activity focus.

### Step 4: Progress Report

```
## Phase Progress Report

### Phase {N}: {name}
Progress: {bar} {percent}%

| Exit Criteria | Status | Evidence |
|--------------|--------|---------|
| {criterion} | DONE/IN PROGRESS/NOT STARTED | {evidence} |

### Overall Summary
- Phase {N}: {percent}% ({met}/{total} criteria)
- Biggest blocker: {description}
- Recent 2-week activity: {N} commits in {phase}, {M} commits in {phase}

### Next Steps
(based on results)
```

Recommend the next arch-guard skill. Always use slash command format:

| Situation | Recommendation |
|-----------|---------------|
| Projects not created for this phase | `/scaffold {project}` |
| Projects exist but no Contracts | `/contract-first {project}` |
| Completed criteria need compliance check | `/impl-review {project}` |
| Phase looks complete | `/arch-check` — full compliance scan before milestone |

## Notes

- Requires `config.phases[]` to be defined — without phases, this skill has no data to work with
- For structural presence checks without phase grouping, use `/spec-sync` instead
- Exit criteria are evaluated heuristically — some criteria may need manual verification
- Git log analysis shows development focus, not necessarily completion
