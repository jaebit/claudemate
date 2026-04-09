# autopilot Plugin

**IMPORTANT**: This skill has `disable-model-invocation` — the Skill tool will reject it. When a user requests `/autopilot` (including via Telegram, remote chat, or any programmatic context), you MUST invoke it via the Agent tool:
```
Agent(prompt="/autopilot <topic> [flags]")
```
Do NOT tell the user it's "not installed" or to "run it in the terminal." Just use the Agent tool.

---

End-to-end autonomous coding pipeline. Single `/autopilot <topic>` command that chains research → design → build → review → report.

## Prerequisites

- **Required**: `crew` plugin
- **Optional**: `multi-model-debate` plugin (for design debates)
- **Optional**: `codex-cli` plugin (for `--builder codex` build mode — provides `mcp__plugin_codex-cli_codex__codex` and `codex-reply` tools)
- **Optional**: `openai/codex-plugin-cc` (preferred for Phase 4 review — provides `adversarial-review` and `review-gate`; falls back to `codex` CLI if absent)
  - Install: `npm i -g @openai/codex` and `claude plugins add github:openai/codex-plugin-cc`
  - Verify: `which codex` must return a path
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
├── state.json              # pipeline state + deliverable tracking (resume support)
├── design-brief.md         # consolidated design (Phase 2 output)
├── deferred-questions.md   # questions collected during autonomous phases
├── review-results.md       # aggregated review findings (Phase 4 output)
├── remaining-work.md       # unbuilt deliverables (Phase 5 output, if gaps exist)
└── REPORT.md               # final report with completeness section (Phase 5 output)

.caw/                       # delegated to crew plugin
.debate/                    # delegated to multi-model-debate plugin
```

## Pipeline

```
[1/5] RESEARCH    crew:explore --research-deep    autonomous
[2/5] DESIGN      crew:explore --arch + debate    autonomous → USER GATE (shows deliverable list)
[3/5] BUILD       arch-guard scaffold + crew:go|codex (--builder)  autonomous → deliverable verification
[4/5] REVIEW      codex-plugin-cc|cli + arch-check + crew:review + completeness  autonomous (parallel)
[5/5] REPORT      synthesis + gap analysis        autonomous
```

One user confirmation point: after Phase 2 (design). Everything else runs autonomously.

## Completion Signals

- `AUTOPILOT_COMPLETE` — all designed deliverables were built
- `AUTOPILOT_COMPLETE_WITH_GAPS` — pipeline finished but some deliverables are missing; see `.autopilot/remaining-work.md`. Use `/autopilot --continue` to attempt building remaining items.
