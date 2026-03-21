---
name: spec-sync
description: >
  This skill should be used when the user asks "check implementation status", "spec sync",
  "what's been implemented?", "create implementation checklist", "compare design vs source",
  or wants to check which design-doc components actually exist in the source tree. Generates
  a structural presence checklist (exists / not exists) — for phase progress percentages
  use track instead.
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /spec-sync — Design Document → Implementation Status Checklist

Compares the expected project structure (from `arch-guard.json` and architecture docs) against the actual source tree to generate an implementation status checklist.

## Reference

Read `arch-guard.json` from the project root before starting. This is the single source of truth for all rules.

## Procedure

### Step 1: Load Configuration

Read `arch-guard.json`. If not found, suggest `/setup` first and stop.

Also read the architecture documentation from `config.docs.architecture` if set.

### Step 2: Expected Project Structure

From `config.layers[]`, build the expected list of projects:

For each layer:
1. Scan `config.project.source_root` for directories matching `layer.pattern`
2. Compare found projects against expected projects (from architecture docs or config)
3. Check for project files (`.csproj` for .NET, `build.gradle` for Java, `tsconfig.json` for TypeScript)

### Step 3: Contracts Coverage

If `config.contracts.enabled`:
- For each layer, check if the Contracts project exists
- Check if it contains at least one interface/model

### Step 4: Test Coverage

Check `config.project.test_root` for test projects:
- Does each source project have a corresponding test project?
- Does the test project contain at least one test file?

### Step 5: Phase Mapping (if configured)

If `config.phases[]` is defined, map each project to its phase:

For each phase:
1. List the projects assigned to that phase
2. Check which ones exist in the source tree
3. Calculate the structural presence ratio

If `config.phases` is not defined, skip this step and report all projects without phase grouping.

### Step 6: Discrepancy Detection

Find discrepancies:
- Projects in source tree that don't match any configured layer pattern → "Unmatched project"
- Expected projects from architecture docs that don't exist → "Missing project"
- Empty projects (project file exists but no source code) → "(empty project)"

### Step 7: Checklist Output

```
## Spec-Sync Checklist

### Layer: {layer_name} (L{level})
- [x] {ProjectA} — exists, project file confirmed
- [ ] {ProjectB} — not created
- [x] {ProjectC} — exists (empty project)

### Contracts
- [x] {Layer}.Contracts — exists, {N} interfaces
- [ ] {Layer2}.Contracts — not created

### Phase {N}: {phase_name} (if phases configured)
- [x] {project} — exists
- [ ] {project} — not created

### Test Projects
- [x] {project}.Tests.Unit — exists
- [ ] {project}.Tests.Unit — not created

### Discrepancies
- WARNING: {source_root}/{UnknownProject}/ exists but not defined in configuration

### Summary
- Total expected: {N}, exists: {M} ({percent}%)
- Contracts: {N}/{M}
- Tests: {N}/{M}

### Next Steps
(based on results)
```

Recommend the next arch-guard skill. Always use slash command format:

| Situation | Recommendation |
|-----------|---------------|
| Missing projects exist | `/scaffold {project}` — highest priority first |
| Missing Contracts | `/scaffold {layer}.Contracts` — Contracts-first priority |
| All projects exist, code not implemented | `/contract-first {project}` — verify interfaces before implementation |
| Implementation in progress | `/track` — phase progress percentages |
| Discrepancies found | `/arch-check` — check reference rule compliance |

## Notes

- Projects in the source tree not matching any config pattern are reported as discrepancies
- Empty projects (project file only, no source) are marked accordingly
- Contracts projects should always exist before implementation projects in the same layer
