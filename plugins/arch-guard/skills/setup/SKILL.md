---
name: setup
description: >
  This skill should be used when the user asks "set up arch-guard", "create arch-guard config",
  "initialize architecture rules", "generate arch-guard.json", "configure layer rules",
  or wants to create an arch-guard.json configuration file for their project by analyzing
  the codebase structure and interactively defining layer rules.
user_invocable: true
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
---

# /setup — Interactive arch-guard.json Generator

Analyzes the codebase directory structure and optionally reads design docs to generate an `arch-guard.json` configuration file interactively.

## Procedure

### Step 1: Check for Existing Config

Look for `arch-guard.json` in the current working directory.

- If found: "An arch-guard.json already exists. Would you like to update it or start fresh?"
- If not found: proceed to Step 2

### Step 2: Detect Project Structure

Scan the project to determine language and structure:

**For .NET projects:**
```bash
find . -name "*.sln" -maxdepth 2
find . -name "*.csproj" -maxdepth 4
```

**For Java projects:**
```bash
find . -name "build.gradle" -o -name "pom.xml" -maxdepth 4
```

**For TypeScript projects:**
```bash
find . -name "tsconfig.json" -maxdepth 3
```

Identify:
1. Language (dotnet, java, typescript)
2. Source root directory (e.g. `src/`, `app/`)
3. Test root directory (e.g. `tests/`, `test/`)
4. Project/module list with directory names

### Step 3: Identify Layer Patterns

Present the discovered projects/modules and ask the user to define layers:

```
## Discovered Projects

I found the following projects under src/:
1. MyApp.Domain
2. MyApp.Domain.Contracts
3. MyApp.Application
4. MyApp.Infrastructure
5. MyApp.Api
6. MyApp.BuildingBlocks.Core

## Questions

1. How many architectural layers does your project have?
2. Which projects belong to each layer?
3. What is the dependency direction? (e.g., Domain has no dependencies, Infrastructure depends on Application)
4. Are there cross-cutting/shared projects? (e.g., BuildingBlocks)
5. Are there host/entry-point projects? (e.g., Api, Hosts)
```

### Step 4: Define Reference Rules

Based on the layer structure, ask about reference rules:

```
## Reference Rules

For each layer, I need to know:
1. Which layers can it call? (calls_allowed)
2. Which layers must it never call? (calls_forbidden)
3. Are there specific forbidden references? (e.g., Infrastructure must not reference Domain)
4. Are there allowed cross-layer references? (e.g., Execution can reference Registry.Contracts)
```

### Step 5: Contracts Configuration

Ask if the project uses a contracts-first pattern:

```
## Contracts-First Pattern

1. Does your project use a Contracts/Interfaces project pattern? (yes/no)
2. If yes, what is the project suffix? (default: "Contracts")
3. Where are interfaces stored? (default: "Interfaces/")
4. Where are shared models stored? (default: "Models/")
```

### Step 6: Additional Configuration

Ask about:
1. Forbidden code patterns (e.g., direct database calls from API layer)
2. Tech stack constraints (required/forbidden packages)
3. Documentation paths (architecture docs, ADR directory)
4. Scoring weights (or use defaults)

### Step 7: Generate arch-guard.json

Assemble the configuration and present it to the user for review:

```json
{
  "version": "1",
  "project": { ... },
  "layers": [ ... ],
  "references": { ... },
  "contracts": { ... },
  ...
}
```

Ask: "Does this configuration look correct? Any changes needed?"

### Step 8: Write Config File

After user confirmation, write `arch-guard.json` to the project root.

### Step 9: Result

```
## Setup Complete

- Config: arch-guard.json (written to project root)
- Layers: {count} defined
- Forbidden references: {count} rules
- Contracts-first: {enabled/disabled}

### Next Steps
- /arch-check — scan the codebase for existing violations
- /scaffold {module} — create a new module following the rules
- /adr "initial architecture" — document the architecture decisions
```
