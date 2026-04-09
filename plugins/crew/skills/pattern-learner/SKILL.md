---
name: pattern-learner
user_invocable: false
description: Analyzes codebase to learn project-specific patterns including code style, architecture conventions, and testing approaches
context: fork
agent: Explore
allowed-tools: Read, Glob, Grep, Bash
---

# Pattern Learner

Analyzes codebase to extract and document project-specific coding patterns.

## Project Snapshot

- **Project files**: !`find . -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.go" 2>/dev/null | head -30 || echo "(no source files found)"`
- **Project config**: !`cat package.json 2>/dev/null | head -15 || cat pyproject.toml 2>/dev/null | head -15 || cat go.mod 2>/dev/null | head -5 || echo "(no project config found)"`
- **Cached patterns**: !`cat .caw/patterns/patterns.md 2>/dev/null | head -20 || echo "(no cached patterns)"`

## Triggers

1. `/crew:go` → auto-analyze at workflow start
2. Agent request ("What are the patterns?")
3. Pattern refresh ("Re-analyze patterns")
4. Before new file creation

## Pattern Categories

| Category | What to Learn | Examples |
|----------|---------------|----------|
| Naming | Conventions | camelCase functions, PascalCase classes |
| Architecture | Structure | Clean Architecture, Feature-based |
| Error Handling | Patterns | Result<T,E>, try-catch style |
| Testing | Structure | AAA pattern, *.test.ts |
| Imports | Organization | Grouped, path aliases |
| Documentation | Comments | JSDoc, docstrings |

## Workflow

### 1. File Discovery
```yaml
config_files: package.json, tsconfig.json, pyproject.toml, go.mod, .eslintrc*
source_files: src/**/*.{ts,tsx}, lib/**/*.py, **/*.go (5-10 samples)
test_files: tests/**/* , **/*.test.*
```

### 2. Pattern Analysis
```yaml
naming: functions, classes, constants, files
architecture: directories, modules, exports
error_handling: patterns, logging, propagation
testing: location, naming, structure, mocking
imports: ordering, aliases, grouping
```

### 3. Save Results
```
Path: .caw/patterns/patterns.md
Cache: .caw/patterns/.pattern-cache.json
```

### 4. Confirm
```
📊 Patterns analyzed: {N} files
   - Naming: {convention}
   - Architecture: {pattern}
   - Testing: {framework}
```

## Pattern Template

```markdown
# Project Patterns

| Field | Value |
|-------|-------|
| **Analyzed** | YYYY-MM-DD |
| **Language** | TypeScript/Python/Go |

## Naming Conventions
| Element | Pattern | Confidence | Example |
|---------|---------|------------|---------|
| Functions | camelCase | High (95%) | `getUserById()` |

## Architecture Patterns
[Directory structure, module patterns]

## Error Handling
[Detected patterns]

## Testing Patterns
[Test organization, naming]
```

## Language-Specific Analysis

| Language | Config | Naming | Patterns |
|----------|--------|--------|----------|
| TS/JS | tsconfig.json | camelCase/PascalCase, I prefix | async/await, try-catch |
| Python | pyproject.toml | snake_case/PascalCase | Type hints, exceptions |
| Go | go.mod | Exported=Pascal, unexported=camel | if err != nil |

## Confidence Levels

| Level | Criteria |
|-------|----------|
| High | 90%+ files follow |
| Medium | 70-90% follow |
| Low | 50-70% follow |
| Mixed | <50% (no clear pattern) |

## Integration

- **quality-gate**: Uses patterns in conventions check
- **knowledge-engine**: Generates pattern-based review checklist
- **session-manager**: Provides pattern docs as context
- **Agents**: Builder follows, Reviewer checks compliance

## Boundaries

**Will:** Analyze code, document patterns, cache results, show confidence
**Won't:** Enforce patterns (quality-gate), auto-fix, modify config, override linter
