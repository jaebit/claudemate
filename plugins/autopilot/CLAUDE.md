# autopilot Plugin

End-to-end autonomous coding pipeline. Single `/autopilot <topic>` command that chains research → design → build → review → report.

## Prerequisites

- **Required**: `cw` plugin (context-aware-workflow)
- **Optional**: `multi-model-debate` plugin (for design debates)
- **Optional**: `codex-harness` plugin (for cross-model review)
- **Optional**: `arch-guard` plugin (auto-detected via `arch-guard.json`)

## Usage

```bash
/autopilot "build a notification system"
/autopilot "add user authentication" --skip-research
/autopilot --continue                    # resume from state
/autopilot "refactor payments" --no-arch --skip-debate
```

## Artifacts

```
.autopilot/
├── state.json              # pipeline state (resume support)
├── design-brief.md         # consolidated design (Phase 2 output)
├── deferred-questions.md   # questions collected during autonomous phases
├── review-results.md       # aggregated review findings (Phase 4 output)
└── REPORT.md               # final report (Phase 5 output)

.caw/                       # delegated to cw plugin
.debate/                    # delegated to multi-model-debate plugin
```

## Pipeline

```
[1/5] RESEARCH    cw:explore --research-deep    autonomous
[2/5] DESIGN      cw:explore --arch + debate    autonomous → USER GATE
[3/5] BUILD       arch-guard scaffold + cw:go   autonomous
[4/5] REVIEW      codex + arch-check + cw:review autonomous (parallel)
[5/5] REPORT      synthesis                     autonomous
```

One user confirmation point: after Phase 2 (design). Everything else runs autonomously.
