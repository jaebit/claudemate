# arch-guard

Architecture compliance enforcement for layered projects. Config-driven layer boundary checks, contract-first development, and design decision records.

## Overview

arch-guard is a Claude Code plugin that enforces architectural rules for any layered architecture project. Define your layers, reference rules, and constraints in a single `arch-guard.json` config file, and the plugin provides:

- **Hooks** that detect layer violations in real-time as you write code
- **Skills** that scan, scaffold, and verify architecture compliance

## Installation

```bash
claude plugins add github:jaebit/claudemate
claude plugins install arch-guard
```

## Quick Start

1. Run `/arch-guard:setup` to generate `arch-guard.json` interactively
2. Start developing — hooks will warn about violations automatically
3. Run `/arch-guard:arch-check` for a full compliance scan

## Skills

| Skill | Description |
|-------|-------------|
| `/arch-guard:setup` | Interactive config generator — analyzes codebase, creates `arch-guard.json` |
| `/arch-guard:arch-check` | Full architecture scan — layer boundary violations with CRITICAL/WARNING/INFO report |
| `/arch-guard:scaffold <module>` | Create new modules following architecture rules |
| `/arch-guard:contract-first <project>` | Verify contracts exist before implementation |
| `/arch-guard:adr <title>` | Create Architecture Decision Records |
| `/arch-guard:implement <project> [interface]` | Generate implementation stubs + RED tests from interfaces |
| `/arch-guard:impl-review <project>` | Review implementation against architecture docs |
| `/arch-guard:spec-sync` | Compare design docs vs source tree |
| `/arch-guard:integration-map <module>` | Cross-layer change impact analysis |
| `/arch-guard:track` | Phase-based roadmap progress with exit criteria |
| `/arch-guard:tdd <project> <class>` | Architecture-aware TDD guidance |
| `/arch-guard:test-gen [layer]` | Generate architecture guard-rail xUnit tests |

## Hooks

| Hook | Trigger | Action |
|------|---------|--------|
| `session-init` | Session start | Injects compressed rule summary from config |
| `layer-check` | Write/Edit | Identifies layer + warns on forbidden references |
| `contract-guard` | Write | Warns if Contracts project is missing for the layer |
| Stop prompt | End of response | Reminds to run `/arch-check` after modifying source files |

All hooks follow the **never-block** principle — they provide information and warnings but never prevent actions.

## Agents

| Agent | Description |
|-------|-------------|
| `arch-reviewer` | Comprehensive architecture fitness analysis — scores compliance across all rule categories with remediation roadmap |

## Configuration

See [docs/config-reference.md](docs/config-reference.md) for the full `arch-guard.json` schema.

## Supported Languages

- **.NET** (v0.1.0) — `.cs` + `.csproj` analysis
- Java, TypeScript — extension points exist, implementation planned

## Design Decisions

See [docs/architecture-decisions.md](docs/architecture-decisions.md) for the rationale behind arch-guard's design.

