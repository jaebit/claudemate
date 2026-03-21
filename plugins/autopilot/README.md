# autopilot

End-to-end autonomous coding pipeline for Claude Code.

Takes a topic or idea and produces working code through a 5-phase pipeline: research → design → build → review → report. Orchestrates existing plugins (`cw`, `multi-model-debate`, `codex-harness`, `arch-guard`) rather than reimplementing their logic.

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

## Requirements

- `cw` plugin (required)
- `multi-model-debate` plugin (optional — for design debates)
- `codex-harness` plugin (optional — for cross-model review)
- `arch-guard` plugin (optional — auto-detected via `arch-guard.json`)
