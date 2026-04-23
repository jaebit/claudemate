# autopilot

End-to-end autonomous coding pipeline for Claude Code.

Takes a topic or idea and produces working code through a 5-phase pipeline: research → design → build → review → report. Orchestrates existing plugins (`crew`, `multi-model-debate`, `codex` CLI, `arch-guard`) rather than reimplementing their logic.

## Install

```bash
claude plugins install autopilot
```

## Quick Start

```bash
/autopilot "build a notification system"
```

## Flags

| Flag | Effect |
|------|--------|
| `--skip-research` | Skip Phase 1, start at design |
| `--skip-debate` | Skip debate sub-step in Phase 2 |
| `--no-arch` | Force-skip arch-guard even if config exists |
| `--from-plan <path>` | Skip Phase 1+2, use existing design doc |
| `--continue` | Resume from `.autopilot/state.json` |
| `--verbose` | Detailed per-phase progress |
| `--no-questions` | Minimize interactive prompts (still shows user gate) |
| `--worktree` | Isolate each build step in a git worktree |

## Phase → Plugin Dispatch

| Phase | Plugin / Skill | Required |
|-------|----------------|----------|
| 1 Research | `crew:explore --research-deep` | yes |
| 2 Design | `crew:explore --arch` + `multi-model-debate` + `arch-guard` (ADR/constraints) | crew yes, others optional |
| 3 Build | `crew` (default builder) or `codex-cli` (`--builder codex`); optional `worktree` | yes |
| 4 Review | `codex-cli` (plugin-cc preferred, CLI fallback) + `arch-guard` + `crew:review` | yes (crew); others optional |
| 5 Report | autopilot native (synthesis) | yes |

See `CLAUDE.md` for the full invocation table with exact Skill/Agent call patterns.

## Requirements

- `crew` plugin (required)
- `multi-model-debate` plugin (optional — for design debates)
- `codex` CLI + `openai/codex-plugin-cc` (optional — for cross-model review)
- `arch-guard` plugin (optional — auto-detected via `arch-guard.json`)
