---
name: impl-review
description: >
  This skill should be used when the user asks "review implementation", "check design compliance",
  "impl-review", "does this code match the architecture?", "responsibility boundary check",
  or wants to verify implementation code against architecture docs — checking component
  responsibility boundaries, interface contract compliance, and reference rule compliance.
argument-hint: "<project-or-file> e.g. MyApp.Execution.Workflow or path to source file"
user_invocable: false
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /impl-review — Architecture Design Compliance Review

Reviews implementation code against `arch-guard.json` rules and architecture documentation to check design compliance.

## Usage

```
/impl-review MyApp.Execution.Workflow
/impl-review src/MyApp.Execution.Workflow/Services/StepExecutor.cs
```

Without arguments, targets recently changed files (`git diff --name-only HEAD~1`).

## Reference

Read `arch-guard.json` from the project root before starting. This is the single source of truth for all rules.

## Procedure

### Step 1: Identify Target

- If argument is a project name: review the entire project
- If argument is a file path: review that file and related files
- If no argument: use `git diff --name-only HEAD~1` to find recently changed files

### Step 2: Map to Architecture

1. Match the target project/files against `config.layers[].pattern` to identify the layer
2. If `config.docs.architecture` is set, read the architecture document to find the relevant section for this layer/component

### Step 3: Verification Checks

#### 3-A: Component Responsibility Boundary

Using the architecture documentation (from `config.docs.architecture`), verify that each component stays within its defined responsibilities:

- Does the component only do what it's supposed to do?
- Is there logic that belongs to a different component/layer?
- Are there signs of responsibility creep?

#### 3-B: Interface Contract Compliance

- Is the implementation based on interfaces defined in the Contracts project?
- Does the implementation honor the contract semantics (not just the method signatures)?
- Are there undeclared interfaces being implemented?

#### 3-C: Reference Rule Compliance

Using `arch-guard.json`:
- Check `config.references.forbidden[]` for violations
- Check `config.references.cross_layer[]` for unauthorized cross-layer references
- Verify imports/using statements comply with layer rules

### Step 4: Report

```
## Impl-Review Report

### Target: {project_or_file}
### Layer: L{level} {layer_name}
### Architecture Reference: {doc_path} {section}

### Compliant
- OK {description of compliant behavior}

### Violations
- VIOLATION {description of violation}
  Reference: {config rule or architecture doc section}

### Warnings
- WARNING {description of concern}
  Reference: {rule or section}

### Next Steps
(based on results)
```

Recommend the next arch-guard skill based on results. Always use slash command format:

| Result | Recommendation |
|--------|---------------|
| Violations exist | Fix then → `/impl-review {same target}` (re-verify) |
| Warnings only | `/arch-check` — cross-check layer boundary compliance |
| All compliant | `/track` — check phase progress, or `/integration-map {project}` — trace change impact |
