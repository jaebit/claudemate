---
name: contract-first
description: >
  This skill should be used when the user asks "do contracts exist?", "can I start implementing?",
  "contract-first check", "are interfaces defined?", "define interfaces", "suggest interfaces",
  "fill contracts", or wants to verify that the layer's Contracts project exists and required
  interfaces are defined before writing implementation code. Can also design and generate
  interfaces interactively.
argument-hint: "<project-name> e.g. MyApp.Execution.Workflow"
user_invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# /contract-first — Contracts-First Development Enforcement

Verifies that the layer's Contracts project exists and required interfaces are defined before implementation begins.

## Usage

```
/contract-first MyApp.Execution.Workflow
```

Without arguments, targets the project of recently changed files (from `git diff`).

## Reference

Read `arch-guard.json` before starting. If not found, suggest `/setup` first.

## Procedure

### Step 1: Identify Target Layer

Match the target project against `config.layers[].pattern` to find its layer and the corresponding Contracts project.

The Contracts project name follows the pattern: `{layer_base}.{config.contracts.project_suffix}`

### Step 2: Contracts Existence Check

Verify:
1. Contracts project directory exists under `config.project.source_root`
2. Contracts project file exists (`.csproj` for .NET)
3. At least one interface or model is defined

### Step 3: Interface Coverage Check

Scan the target implementation project for types it references or should implement. Check if corresponding interfaces exist in Contracts.

**For .NET:**
```bash
grep -rn 'interface I' {contracts_dir} --include='*.cs'
```

Compare against implementation references to identify gaps.

### Step 4: Result Report

**If blocked:**
```
## Contract-First Check

### Target: {project} (L{level})
### Contracts: {contracts_project}

### Status: BLOCKED
- {contracts_project} does not exist.
- Run `/scaffold {contracts_project}` first.
```

**If ready:**
```
### Status: READY
- Contracts project exists
- {interface1} defined
- {interface2} defined

### Undefined Interfaces (define before implementing):
- WARNING: {InterfaceName} — used in implementation but not in Contracts
```

**Next steps based on result:**

| Result | Recommendation |
|--------|---------------|
| BLOCKED (Contracts missing) | `/scaffold {layer}.Contracts` |
| WARNING — undefined interfaces | Proceed to Step 5 (Interface Design Mode) |
| READY | Start implementation, then → `/arch-check` to verify |

---

## Interface Design Mode (activated only on WARNING path)

Only runs Steps 5-9 when undefined interfaces are detected. Skipped for BLOCKED or READY paths.

### Step 5: Architecture-Based Interface Analysis

Analyze the target project's responsibilities based on:
- `arch-guard.json` layer definition and role
- Architecture documentation (if `config.docs.architecture` is set)
- Existing code patterns in the project

Produce: candidate interface list with rationale.

### Step 6: Interface Proposal

Present structured proposals:

```
## Interface Proposals

### Rationale: Based on {layer_name} layer responsibilities

| # | Interface | Method Signature | Rationale |
|---|-----------|-----------------|-----------|
| 1 | IStepExecutor | Task<StepResult> ExecuteAsync(StepContext, CancellationToken) | Core execution contract |
| 2 | ITransitionResolver | StepId ResolveNext(WorkflowState, StepResult) | State transition logic |

Review:
- Add/change/remove any interfaces?
- Method signature adjustments?
```

Rules:
- Follow language conventions (async, CancellationToken for .NET, etc.)
- Stay within the layer's responsibility boundary
- Reference architecture docs where available

### Step 7: User Feedback Loop

Iterate until user confirms with "OK", "proceed", "generate", etc. **Do not create files before confirmation.**

### Step 8: Generate Interface Files

**For .NET:** Create `{contracts_dir}/{config.contracts.interface_dir}/{InterfaceName}.cs`:

```csharp
namespace {contracts_namespace}.Interfaces;

/// <summary>
/// {description}
/// </summary>
public interface {InterfaceName}
{
    {method signatures};
}
```

Rules:
- One interface per file
- If parameters/return types need new models, create them in `{contracts_dir}/{config.contracts.model_dir}/`
- Never overwrite existing files — ask user first

### Step 9: Re-verify + Final Report

Re-run Steps 2-3 to confirm, then report:

```
## Contract-First Check (Interface Design Complete)

### Generated Interfaces
| File | Purpose |
|------|---------|
| Interfaces/IStepExecutor.cs | Core execution contract |
| Models/StepResult.cs | IStepExecutor return type |

### Status: READY

### Next Steps
- Start implementing the target project
- After implementation: /arch-check to verify compliance
```
