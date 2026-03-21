---
name: integration-map
description: >
  This skill should be used when the user asks "what does this change affect?", "impact analysis",
  "integration-map", "dependency map", "change impact scope", or wants to trace how a module
  change propagates across layers via the project reference graph.
argument-hint: "<module-or-file> e.g. MyApp.Execution.Contracts"
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /integration-map — Cross-Layer Change Impact Analysis

Analyzes how a change to a specific module propagates through the project reference graph across layers.

## Usage

```
/integration-map MyApp.Execution.Contracts
/integration-map src/MyApp.Gateway.Policy/ActionClassifier.cs
```

## Reference

Read `arch-guard.json` from the project root before starting. This is the single source of truth for all rules.

## Procedure

### Step 1: Identify Target Module

Match the user-specified module/file against `config.layers[].pattern` to identify its layer and project.

### Step 2: Reverse Dependency Graph

Find all projects that **reference** the target project.

**For .NET:**
```bash
grep -rl '{target_project}' {source_root} --include='*.csproj'
```

Repeat recursively to trace the full propagation path — a project that references the target, and projects that reference *that* project, etc.

### Step 3: Cross-Layer Path Identification

Using `config.layers[]`, classify each affected project by layer:

- **Same layer (intra-layer)**: Direct dependents within the same layer
- **Cross-layer**: Dependents in other layers — these are the high-impact paths

Trace the propagation path from the target through each affected layer.

### Step 4: Impact Report

```
## Integration Map: {target_module}

### Direct Impact (same layer — L{level})
- {ProjectA} (L{level})
- {ProjectB} (L{level})

### Cross-Layer Impact
- {ProjectC} (L{other_level}) — via {reference_chain}

### Propagation Path
{target} → {ProjectA} → {ProjectC}
           → {ProjectB}

### Recommended Test Scope
- {test_root}/{project}.Tests.Unit/
- {test_root}/{project}.Tests.Integration/ (if exists)
- Architecture tests (if exists)

### Next Steps
- `/arch-check` — verify layer boundary compliance before making changes
- `/impl-review {affected_project}` — check design compliance of affected projects
```

## Notes

- Reference graph scanning is language-specific (`.csproj` for .NET, `build.gradle` for Java, `package.json` for TypeScript)
- Only direct project-level references are traced — runtime/dynamic dependencies are not captured
- If the target is a Contracts project, the impact radius is typically larger since many projects reference Contracts
