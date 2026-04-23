# multi-model-debate

Structured 3-model debate plugin for Claude Code. Orchestrates Claude, Codex, and Gemini to evaluate software engineering decisions through independent evaluation, cross-examination, and consensus building.

## Prerequisites

- [codex-cli](../codex-cli) plugin (provides Codex MCP tools)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) installed and authenticated

## Installation

```bash
claude plugins add github:jaebit/claudemate
claude plugins install multi-model-debate
```

## Usage

### Start a debate

```
/multi-model-debate:debate-start "Should we use REST or GraphQL for our API?"
```

With options:

```
/multi-model-debate:debate-start "Monorepo vs polyrepo" --context src/package.json,docs/architecture.md
/multi-model-debate:debate-start "Next.js vs Remix vs Astro" --perspectives "Performance,DX,Ecosystem" --rounds 3
```

### Resume an interrupted debate

```
/multi-model-debate:debate-resume
/multi-model-debate:debate-resume .debate/20260315-143022-rest-vs-graphql
```

## How It Works

1. **Setup** — Creates debate workspace, assigns perspectives, extracts decision points
2. **Round 1** — 3 agents evaluate independently in parallel
3. **Synthesis** — Orchestrator compares positions, classifies agreement levels
4. **Round 2+** — Cross-examination on contested points only (skips agreed items)
5. **Final Consensus** — Generates report with verdicts, recommendations, and action items

The orchestration skill runs in a forked sub-agent context (`context: fork`) to keep the main conversation clean.

## Plugin Structure

```
multi-model-debate/
├── .claude-plugin/plugin.json
├── skills/
│   ├── debate-start/SKILL.md        # /debate:start slash command
│   ├── debate-resume/SKILL.md       # /debate:resume slash command
│   └── debate-orchestration/
│       ├── SKILL.md                  # Core orchestration logic (internal)
│       └── reference.md             # Prompt templates and report structure
├── CLAUDE.md
└── README.md
```

## Output

All artifacts are saved to `.debate/<debate-id>/`:

```
.debate/20260315-143022-rest-vs-graphql/
  state.json              # Debate state (enables resume)
  round-1-claude.md       # Round 1 evaluations
  round-1-codex.md
  round-1-gemini.md
  synthesis-round-1.md    # Comparative analysis
  round-2-claude.md       # Round 2 cross-examination
  round-2-codex.md
  round-2-gemini.md
  synthesis-round-2.md
  report.md               # Final consensus report
```

## Agent Perspectives

| Topic Type | Claude | Codex | Gemini |
|---|---|---|---|
| Architecture | Scalability | Developer experience | Cost realism |
| Library/framework | Performance | Ecosystem | Maintenance |
| General | Advocate | Skeptic | Pragmatist |

Custom perspectives via `--perspectives "Label1,Label2,Label3"`.

## Pipeline Controls

### Round Limit

- **Default:** 2 rounds
- **Override:** `--rounds <N>` flag (e.g., `--rounds 3`)
- **Hard cap:** If more than 3 rounds would be needed, the skill pauses and asks for user confirmation before proceeding

### Termination Conditions

A debate ends when **any** of the following is true:

| Condition | Action |
|---|---|
| All decision points reach `Agreement` after synthesis | Early exit — skips remaining rounds, proceeds to Final Consensus |
| `currentRound >= rounds` (default 2, or `--rounds N`) | Proceeds to Final Consensus |
| Max rounds exceeded (>3) | Pauses — requires user confirmation to continue |

The synthesis phase classifies each decision point as `Agreement`, `Partial Agreement`, or `Contested`. Only `Contested` points proceed to cross-examination in the next round.

### Role Assignment

Each model plays a fixed evaluative role per topic type (see Agent Perspectives table above). Roles are assigned during SETUP and recorded in `state.json`:

- **Claude** — Synthesis-oriented role (Scalability / Performance / Advocate). Also serves as the orchestrator for the inline round dispatch.
- **Codex** — Implementation-focused role (Developer experience / Ecosystem / Skeptic). Invoked via MCP (`mcp__plugin_codex-cli_codex__codex`) or CLI fallback.
- **Gemini** — Pragmatist/realist role (Cost realism / Maintenance / Pragmatist). Invoked as a sub-agent running `gemini -p "..."` via Bash.

`debate-orchestration` (synthesis) is a separate internal skill that runs in a `fork` context — it reads the saved round files and produces comparison tables and final reports without dispatching any agents.
