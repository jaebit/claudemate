---
name: test-gen
description: >
  This skill should be used when the user asks "generate architecture tests", "test-gen",
  "guard-rail tests", "create reference tests", "layer violation tests", or wants to generate
  xUnit architecture guard-rail tests that codify the layer reference rules, namespace
  restrictions, and forbidden patterns from arch-guard.json.
argument-hint: "[layer-name] e.g. Execution (optional — omit for all layers)"
user_invocable: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# /test-gen — Architecture Guard-Rail Test Generation

Generates xUnit tests that codify the layer reference rules, namespace restrictions, and forbidden patterns from `arch-guard.json`.

## Usage

```
/test-gen                # all layers
/test-gen Execution      # specific layer only
```

## Reference

Read `arch-guard.json` from the project root before starting. This is the single source of truth for all rules.

## Procedure

### Step 1: Determine Scope

- No argument → all layers
- Argument given → filter to that layer only

### Step 2: Test Project Setup

Check for an architecture test project under `config.project.test_root`. The project name should follow the pattern: `{config.project.name}.Architecture.Tests` or similar.

If it doesn't exist, create it:

```xml
<!-- {ProjectName}.Architecture.Tests.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.*" />
    <PackageReference Include="xunit" Version="2.*" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.*" />
  </ItemGroup>
</Project>
```

Register in solution if applicable.

**Dependency principle**: xUnit + `Microsoft.NET.Test.Sdk` only. No external architecture test libraries.

### Step 3: Common Helper

Create `Helpers/SolutionHelper.cs` with utilities driven by `arch-guard.json`:

```csharp
public static class SolutionHelper
{
    // Find the solution file
    public static string FindSolutionFile() { ... }

    // Parse .sln → project paths
    public static IEnumerable<string> GetProjectPaths(string slnPath) { ... }

    // Parse .csproj → ProjectReference entries
    public static IEnumerable<string> GetProjectReferences(string csprojPath) { ... }

    // Map project name → layer (using arch-guard.json layer patterns)
    public static string GetLayer(string projectName) { ... }

    // Map project name → project type (Contracts, Domain, etc.)
    public static string GetProjectType(string projectName) { ... }

    // Extract using statements from .cs file (excluding comments)
    public static IEnumerable<string> GetUsingStatements(string csFilePath) { ... }
}
```

The `GetLayer` method should use the patterns from `config.layers[].pattern` to classify projects.

### Step 4: ProjectReference Tests

Create `ProjectReferenceTests.cs` — codifies `config.references.forbidden[]`:

```csharp
public class ProjectReferenceTests
{
    // For each rule in config.references.forbidden[]:
    // Generate a test that verifies no project matching "from" references a project matching "to"

    [Fact]
    public void Forbidden_Reference_{from}_To_{to}_ShouldNotExist()
    {
        // Scan .csproj files for forbidden ProjectReference patterns
    }

    [Fact]
    public void CrossLayer_References_Should_Target_Contracts_Only()
    {
        // If config.contracts.enabled, cross-layer refs must target Contracts projects
    }
}
```

### Step 5: Namespace/Import Tests

Create `NamespaceReferenceTests.cs` — verifies using/import statements comply with layer rules:

```csharp
public class NamespaceReferenceTests
{
    // For each forbidden reference rule, check using statements in source files
    // If layer A cannot reference layer B, then files in A should not have using B.* statements

    [Theory]
    // InlineData generated from config.references.forbidden[]
    public void Layer_ShouldNot_Import_Forbidden_Namespace(string sourceLayer, string targetLayer)
    {
        // Scan .cs files in sourceLayer projects for using statements from targetLayer
    }
}
```

**Note**: Exclude using statements inside comments to avoid false positives.

### Step 6: Forbidden Pattern Tests

Create `ForbiddenPatternTests.cs` — codifies `config.forbidden_patterns[]`:

```csharp
public class ForbiddenPatternTests
{
    // For each pattern in config.forbidden_patterns[]:
    // Generate a test that scans relevant projects for the forbidden pattern

    [Fact]
    public void {PatternName}_ShouldNotExist()
    {
        // Use detect.using_pattern from config
        // Scan detect.in_projects for matches
    }
}
```

### Step 7: Build Verification

```bash
dotnet build {test_project_path}
```

Fix build errors if any.

### Step 8: Result Report + Next Steps

```
## /test-gen Complete

### Generated Test Files
| File | Tests | Source Rules |
|------|-------|-------------|
| ProjectReferenceTests.cs | {N} | config.references.forbidden |
| NamespaceReferenceTests.cs | {N} | config.references.forbidden (using) |
| ForbiddenPatternTests.cs | {N} | config.forbidden_patterns |

### Run Tests
```bash
dotnet test {test_project_path}
```
```

Recommend next steps using slash command format:

| Situation | Recommendation |
|-----------|---------------|
| Tests fail → violations to fix | `/arch-check` |
| All tests pass | `/track` |
| Generate tests for another layer | `/test-gen {layer}` |
| Start implementation | `/implement {project}` |

## Notes

- **No external dependencies** — xUnit + file system parsing only
- **Comments excluded** — `GetUsingStatements` skips comment lines to avoid false positives
- **Existing test files preserved** — only adds new files, never modifies existing ones
- **Heuristic-based** — source code text analysis has limitations; complex indirect patterns may not be caught
