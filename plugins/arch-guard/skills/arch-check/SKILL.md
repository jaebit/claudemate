---
name: arch-check
description: >
  This skill should be used when the user asks "check architecture", "layer violations",
  "arch-check", "reference rule violations", "cross-layer reference check", "architecture scan",
  or wants to detect layer boundary violations by analyzing source references against
  arch-guard.json rules.
user_invocable: false
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /arch-check — Layer Boundary Violation Detection

Analyzes source references (imports, project references) against `arch-guard.json` rules to detect layer boundary violations.

## Reference

Read `arch-guard.json` from the project root before starting. This is the single source of truth for all rules.

## Procedure

### Step 1: Load Configuration

Read `arch-guard.json`. If not found, suggest running `/setup` first and stop.

Extract from config:
- `layers[]` — layer definitions with patterns, allowed/forbidden calls
- `references.forbidden[]` — explicit forbidden reference rules
- `references.cross_layer[]` — allowed cross-layer references
- `references.intra_layer[]` — allowed intra-layer references
- `forbidden_patterns[]` — code patterns to detect

### Step 2: Project Mapping

Find all projects/modules under `config.project.source_root`.

**For .NET:**
```bash
find {source_root} -name "*.csproj" -type f
```

For each project:
1. Match against `config.layers[].pattern` to identify its layer
2. Identify sub-project type (Contracts, Domain, Application, Infrastructure, Api, etc.)

### Step 3: ProjectReference Analysis (.NET)

Extract `<ProjectReference>` entries from each `.csproj`:

```bash
grep -r '<ProjectReference' {source_root} --include='*.csproj'
```

For each reference, apply rules from `arch-guard.json`:

#### Check 3-A: Forbidden References

Match against `config.references.forbidden[]`. If a reference matches a forbidden rule, flag as **CRITICAL**.

#### Check 3-B: Cross-Layer Reference Validation

Cross-layer references must appear in `config.references.cross_layer[]`. If not listed, flag as **WARNING**.

#### Check 3-C: Contracts-Through Principle

If `config.contracts.enabled`, cross-layer references should only target the other layer's Contracts project. Direct references to Application, Domain, or Infrastructure across layers are violations.

### Step 4: Import/Using Statement Analysis

Scan source files for import statements:

**For .NET:**
```bash
grep -rn '^using {project_prefix}\.' {source_root} --include='*.cs'
```

Map each import's namespace to a project and apply the same rules as Step 3.

Example:
- `src/MyApp.Gateway.Routing/` contains `using MyApp.Execution.Workflow;` → **CRITICAL** if Gateway→Execution is forbidden
- `src/MyApp.Execution.Workflow/` contains `using MyApp.Registry.Contracts;` → **OK** if listed in cross_layer

### Step 5: Forbidden Pattern Detection

Check each pattern in `config.forbidden_patterns[]`:

For each pattern with a `detect` block:
```bash
grep -rn '{detect.using_pattern}' {source_root} --include='*.cs'
```

If the match appears in projects matching `detect.in_projects` but is not expected, flag as **CRITICAL**.

### Step 6: Scoring (if configured)

If `config.scoring` is defined, calculate a compliance score:

For each scoring area:
1. Count violations in that area
2. Apply penalty: `max(0, weight - (violations * penalty_per_violation))`
3. Sum all area scores for total

Map total to grade using `config.scoring.grades`.

### Step 7: Violation Report

```
## Arch-Check Report

### CRITICAL Violations (immediate fix required)
1. X {Source} → {Target} ({reason})
   File: {path}:{line}
   Rule: {config reference}

### WARNING (review needed)
1. WARNING {Source} → {Target}
   File: {path}:{line}
   Rule: Unlisted cross-layer reference

### INFO
1. Total projects: {N}
2. Total references: {N}
3. Cross-layer references: {N} (allowed {N}, violation {N})

### Forbidden Patterns
- {pattern_name}: {count} occurrences

### Score: {score}/100 — Grade: {grade}

### Summary
- CRITICAL: {N}
- WARNING: {N}
- Violation rate: {violations}/{total_refs} ({percent}%)
```

## Severity Criteria

| Severity | Condition | Action |
|----------|-----------|--------|
| CRITICAL | Matches `references.forbidden[]`, forbidden patterns | Fix immediately |
| WARNING | Unlisted cross-layer reference, suspicious pattern | Team review |
| INFO | Statistics, valid references | Informational |

## Next Steps

At the end of the report, recommend the next arch-guard skill based on results. Always use slash command format:

| Result | Recommendation |
|--------|---------------|
| CRITICAL violations exist | Fix violations then → `/arch-check` (re-verify) |
| WARNING only | `/contract-first {project}` — verify design compliance |
| 0 violations | `/adr` to document compliance status, or continue development |
