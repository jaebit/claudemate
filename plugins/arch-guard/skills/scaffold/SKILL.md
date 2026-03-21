---
name: scaffold
description: >
  This skill should be used when the user asks "create project", "scaffold", "create module",
  "generate project structure", "add new module", or wants to create a new project/module
  following the architecture rules defined in arch-guard.json. Creates project structure,
  references, test project, and registers in solution.
argument-hint: "<module-name> e.g. MyApp.Execution.Workflow"
user_invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# /scaffold — Config-Driven Module Scaffolding

Creates a new project/module following the architecture rules defined in `arch-guard.json`.

## Usage

```
/scaffold MyApp.Execution.Workflow
```

## Reference

Read `arch-guard.json` before starting. If not found, suggest `/setup` first.

## Procedure

### Step 1: Module Validation

1. Match the module name against `config.layers[].pattern` to identify its layer
2. If no layer matches, also check `config.cross_cutting.pattern` and `config.hosts.pattern`
3. If no match at all: "This module doesn't match any configured layer pattern. Continue anyway?"
4. Identify the layer level and allowed/forbidden references

### Step 2: Contracts-First Gate

If `config.contracts.enabled`:

1. Determine the Contracts project name: `{layer_base}.{config.contracts.project_suffix}`
2. Check if it exists under `config.project.source_root`
3. If it doesn't exist and the user is NOT creating a Contracts project:
   - "The Contracts project `{name}` must exist first. Create it now?"
   - If user agrees, create Contracts first, then proceed with the original module

### Step 3: Project Structure

Create the directory and files based on language and module type.

**For .NET — Contracts project:**
```
{source_root}/{module}/
├── {module}.csproj
├── {config.contracts.interface_dir}    (default: Interfaces/)
└── {config.contracts.model_dir}        (default: Models/)
```

`.csproj` content:
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
```

**For .NET — API project (`*.Api`):**
```
{source_root}/{module}/
├── {module}.csproj
├── Endpoints/
└── Middleware/
```

**For .NET — Other implementation projects:**
```
{source_root}/{module}/
├── {module}.csproj
└── (empty — internal structure added during implementation)
```

### Step 4: Reference Configuration

Set up project references in `.csproj` based on `arch-guard.json`:

**Mandatory references:**
- Own layer's Contracts project (if contracts enabled and not a Contracts project)
- Cross-cutting core project (from `config.cross_cutting.pattern`), except for Contracts projects

**Allowed cross-layer references:**
- Check `config.references.cross_layer[]` for references this project may use
- Check `config.references.intra_layer[]` for the "from" pattern matching this project

Add as `<ProjectReference>` with relative paths.

### Step 5: Test Project

Create a test project:

**For .NET:**
```
{test_root}/{module}.Tests.Unit/
├── {module}.Tests.Unit.csproj
└── (empty)
```

Test `.csproj` includes:
- Reference to the target project
- xUnit package references (or configured test framework)

### Step 6: Solution Registration

**For .NET:**
```bash
dotnet sln {config.project.solution_file} add {source_root}/{module}/{module}.csproj
dotnet sln {config.project.solution_file} add {test_root}/{module}.Tests.Unit/{module}.Tests.Unit.csproj
```

If the solution file doesn't exist, create it first.

### Step 7: Result Report

```
## Scaffold Complete

### Created Projects
- {source_root}/{module}/{module}.csproj
- {test_root}/{module}.Tests.Unit/...

### Project References
- → {contracts_project}
- → {cross_cutting_core}
- → {cross_layer_ref} (cross-layer)

### Layer: L{level} {layer_name}
### Forbidden Reference Check: OK — no violations

### Next Steps
```

Recommend the next skill based on context:

| Situation | Recommendation |
|-----------|---------------|
| Same layer has uncreated projects | `/scaffold {next_project}` |
| All layer projects created | `/contract-first {this_module}` — verify interfaces before implementation |
| This project is Contracts | `/scaffold {implementation_project}` — Contracts-first done, start implementation |
| All planned projects created | `/arch-check` — verify full architecture compliance |
