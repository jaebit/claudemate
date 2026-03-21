---
name: implement
description: >
  This skill should be used when the user asks "generate implementation", "implement interface",
  "create stubs", "implement", "generate class from interface", or wants to generate implementation
  classes and unit test stubs from Contracts interfaces following the architecture rules in
  arch-guard.json. Creates sealed classes with constructor injection and empty test methods.
argument-hint: "<project-name> [interface-name] e.g. MyApp.Execution.Workflow IStepExecutor"
user_invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# /implement — Contracts Interface → Implementation Stub + Test Generation

Generates implementation classes and unit test stubs from Contracts interfaces. **Does not write business logic** — only `throw new NotImplementedException()` stubs.

## Usage

```
/implement MyApp.Execution.Workflow IStepExecutor
/implement MyApp.Execution.Workflow          # lists interfaces if not specified
```

## Reference

Read `arch-guard.json` from the project root before starting. This is the single source of truth for all rules.

## Procedure

### Step 1: Parse Input + Validate Project

1. Match the user-specified project name against `config.layers[].pattern` to identify its layer
2. Verify the project directory exists under `config.project.source_root`
3. If missing: "`{project}` not found. Run `/scaffold {project}` to create it first."

### Step 2: Contracts Interface Discovery

1. Find the Contracts project for this layer: `{layer_base}.{config.contracts.project_suffix}`
2. Scan the Contracts project's interface directory (from `config.contracts.interface_dir`)
3. If a specific interface was given, verify it exists
4. If not specified, list available interfaces and ask the user to choose
5. If the Contracts project doesn't exist: "No Contracts project found. Run `/contract-first` first."

**Important**: Never generate implementations for interfaces not defined in Contracts.

### Step 3: Determine Allowed References

From `arch-guard.json`, determine allowed references for this project type:

1. Read `config.references.intra_layer[]` for same-layer references
2. Read `config.references.cross_layer[]` for cross-layer references
3. Read `config.references.forbidden[]` to identify what must be avoided
4. Read the existing project file (`.csproj` for .NET) and report missing required references

### Step 4: Responsibility Boundary Check

If `config.docs.architecture` is set, read the architecture document and verify the interface being implemented fits within this project's responsibilities.

- If the interface seems outside this project's scope → warning
- Warning only, no blocking — user decides

### Step 5: Generate Implementation Class

Create `{source_root}/{project}/Services/{ClassName}.cs`:

```csharp
namespace {project_namespace}.Services;

public sealed class {ClassName} : {InterfaceName}
{
    private readonly ILogger<{ClassName}> _logger;

    public {ClassName}(ILogger<{ClassName}> logger)
    {
        _logger = logger;
    }

    // Stub for each interface method
    public {ReturnType} {MethodName}({Parameters})
    {
        throw new NotImplementedException();
    }
}
```

**Rules**:
- Use `sealed class`
- Constructor injection with `ILogger<T>` by default
- All methods are `throw new NotImplementedException()` stubs
- If the file already exists, **do not overwrite** — ask the user first

### Step 6: Generate RED Tests

Create `{test_root}/{project}.Tests.Unit/{ClassName}Tests.cs`. Generate tests that **fail against the NotImplementedException stubs**.

**Test Category: Contract Compliance** (always generated):

```csharp
namespace {project}.Tests.Unit;

public class {ClassName}Tests
{
    private readonly {InterfaceName} _sut;

    public {ClassName}Tests()
    {
        _sut = new {ClassName}(NullLogger<{ClassName}>.Instance);
    }

    [Fact]
    public void {MethodName}_Should_Not_Throw_NotImplementedException()
    {
        // Act & Assert — RED when stub throws NotImplementedException
        var exception = Record.Exception(() => _sut.{MethodName}({default_params}));
        Assert.IsNotType<NotImplementedException>(exception);
    }

    [Fact]
    public void {MethodName}_Should_Return_Valid_Result()
    {
        // Act
        var result = _sut.{MethodName}({default_params});
        // Assert
        Assert.NotNull(result);
    }
}
```

**Rules**:
- All tests are RED (fail) against the `NotImplementedException` stubs
- Use `NullLogger<T>.Instance` (`Microsoft.Extensions.Logging.Abstractions`)
- Pure xUnit Assert only — no external dependencies
- `Record.Exception()` + `Assert.IsNotType<NotImplementedException>()` pattern
- Do not overwrite existing test files

### Step 7: Forbidden Pattern Verification

Verify the generated code against `config.references.forbidden[]` and `config.forbidden_patterns[]`:

- No forbidden layer references
- No forbidden import/using patterns
- No forbidden code patterns

### Step 8: Result Report + Next Steps

```
## /implement Complete

### Generated Files
| File | Type |
|------|------|
| {source_root}/{project}/Services/{Class}.cs | Implementation stub |
| {test_root}/{project}.Tests.Unit/{Class}Tests.cs | Unit tests (RED) |

### Reference Verification
- Required references: OK/WARNING
- Forbidden references: OK/WARNING

### Responsibility Check
- Architecture boundary: OK/WARNING
```

Recommend next steps using slash command format:

| Situation | Recommendation |
|-----------|---------------|
| RED tests ready, start implementing | `/tdd {project} {class}` |
| After filling stubs, verify compliance | `/impl-review {project}` |
| More interfaces to implement in same project | `/implement {project} {next-interface}` |
| Need architecture guard-rail tests | `/test-gen` |
| Different project implementation | `/contract-first {other-project}` |

## Notes

- **No Contracts = no generation** — stop and suggest `/contract-first`
- **Stubs only** — business logic is user's responsibility
- **Never overwrite existing files** — always ask first
- Implementation class namespace follows the project namespace
