# arch-guard.json Configuration Reference

## Top-Level Schema

```json
{
  "version": "1",
  "project": { ... },
  "layers": [ ... ],
  "cross_cutting": { ... },
  "hosts": { ... },
  "references": { ... },
  "contracts": { ... },
  "tech_stack": { ... },
  "forbidden_patterns": [ ... ],
  "docs": { ... },
  "phases": [ ... ],
  "scoring": { ... }
}
```

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Config version. Currently `"1"` |
| `project.language` | string | `"dotnet"`, `"java"`, `"typescript"`, `"python"` |
| `layers` | array | At least one layer definition |

## `project`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | — | Project display name |
| `language` | string | **required** | Programming language |
| `source_root` | string | `"src/"` | Source code root directory |
| `test_root` | string | `"tests/"` | Test code root directory |
| `solution_file` | string | — | Solution file (.sln for .NET) |

## `layers[]`

Each layer defines an architectural boundary:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Layer display name (e.g. "Domain") |
| `level` | number | Layer level number (1 = innermost) |
| `pattern` | string | Glob pattern matching projects (e.g. `"MyApp.Domain.*"`) |
| `passive` | boolean | If true, this layer only receives calls, never initiates |
| `calls_allowed` | number[] | Layer levels this layer may call |
| `calls_forbidden` | number[] | Layer levels this layer must never call |

## `cross_cutting`

Optional shared/utility layer that all layers may reference.

| Field | Type | Description |
|-------|------|-------------|
| `pattern` | string | Glob pattern (e.g. `"MyApp.BuildingBlocks.*"`) |
| `label` | string | Display label |

## `hosts`

Optional host/entry-point layer.

| Field | Type | Description |
|-------|------|-------------|
| `pattern` | string | Glob pattern (e.g. `"MyApp.Hosts.*"`) |
| `no_inbound_refs` | boolean | If true, no project may reference hosts |

## `references`

### `references.intra_layer[]`

Rules for references within the same layer:

```json
{ "from": "*.Domain", "allowed": ["BuildingBlocks.Core", "self.Contracts"] }
```

- `self.*` expands to the same layer prefix

### `references.cross_layer[]`

Allowed cross-layer references:

```json
{ "from": "MyApp.Execution.*", "to": ["MyApp.Registry.Contracts"] }
```

### `references.forbidden[]`

Explicitly forbidden references:

```json
{
  "from": "*.Infrastructure",
  "to": "*.Domain",
  "reason": "Infrastructure must not reference Domain"
}
```

- `to` can be a string or array of strings
- `reason` is displayed in violation reports

## `contracts`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable contracts-first enforcement |
| `project_suffix` | string | `"Contracts"` | Suffix for contracts projects |
| `interface_dir` | string | `"Interfaces/"` | Directory for interfaces within contracts |
| `model_dir` | string | `"Models/"` | Directory for shared models within contracts |

## `tech_stack`

| Field | Type | Description |
|-------|------|-------------|
| `required` | string[] | Required packages/frameworks |
| `forbidden` | string[] | Forbidden packages/frameworks |

## `forbidden_patterns[]`

Custom code patterns to detect:

```json
{
  "name": "gateway_bypass",
  "description": "Direct call bypassing gateway layer",
  "detect": {
    "using_pattern": "using MyApp.Knowledge",
    "in_projects": "MyApp.Execution.*"
  }
}
```

## `docs`

| Field | Type | Description |
|-------|------|-------------|
| `architecture` | string | Path to architecture documentation |
| `adr_dir` | string | Path to ADR directory (default: `"docs/adr/"`) |

## `scoring`

### `scoring.areas[]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Scoring area name |
| `weight` | number | Weight (all weights should sum to 100) |
| `penalty_per_violation` | number | Points deducted per violation |

### `scoring.grades`

```json
{
  "A": { "min": 90, "meaning": "Architecture compliant" },
  "B": { "min": 70, "meaning": "Minor violations" },
  "C": { "min": 50, "meaning": "Structural violations" },
  "D": { "min": 0, "meaning": "Severe violations" }
}
```
