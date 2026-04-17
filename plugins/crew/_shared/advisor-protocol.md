# Advisor Protocol

Defines how the crew:go orchestrator uses advisor consultation at decision points.

## Overview

Two advisor mechanisms are available, and they are **complementary, not alternatives**:

1. **Built-in Advisor** (primary, free-form guidance): The official Claude Code `/advisor` feature — the executor model automatically consults a stronger advisor model within a single API call when it encounters hard decisions. Returns prose guidance. No extra round-trips, full conversation context preserved.
2. **Explicit Opus Subagent** (structured triage): A tool-less Opus subagent spawned for situations that require a **machine-parseable decision schema** (e.g., per-finding GENUINE/FALSE_POSITIVE classification for contested review triage). The built-in advisor cannot replace this path — free-form prose is not reliably parseable into per-item verdicts.

Model pairing (as of 2026-04, Opus 4.7 / Sonnet 4.6 era): the executor is whatever Claude Code runs as the primary model, and the advisor is the strongest available Opus. Both update automatically when new model versions ship — this protocol does not hardcode model IDs.

## Built-in Advisor (Primary)

The official `advisor_20260301` tool type, activated via Claude Code `/advisor`.

### How It Works

- **Executor** (current primary Sonnet) runs end-to-end: tool calls, file edits, iteration
- **Advisor** (current strongest Opus) provides ~400-700 token strategic guidance when the executor self-determines it needs help
- Advisor **never** calls tools or produces user-facing output
- Advisor receives **full conversation context** automatically
- All handled within a single `/v1/messages` request — zero extra round-trips

### When It Activates

The executor autonomously decides to consult the advisor. Typical triggers:
- Complex architectural decisions during planning or execution
- Ambiguous error diagnosis during recovery
- Multi-file refactoring strategy
- Security-sensitive code paths

### Setup

Activate in Claude Code: `/advisor` → select the current Opus model. No additional parameters required.

### Cost

- Advisor tokens reported separately in API response
- Typical cost reduction: ~11.9% per agentic task vs running Opus end-to-end
- SWE-bench: Sonnet + Advisor = 74.8% (vs 72.1% Sonnet solo)

## Explicit Opus Subagent (Structured Triage)

For situations requiring a **structured decision format** (not free-form advice),
spawn a tool-less Opus subagent directly.

**Why this exists alongside built-in `/advisor`**: the built-in advisor returns free-form prose optimized for guiding the executor, not for being parsed by downstream code. When the orchestrator needs to route decisions programmatically (e.g., "which of these 7 findings should the Fixer act on?"), it needs deterministic schema output. A tool-less Opus subagent with a strict response template fills that gap. Do not assume one path obsoletes the other.

### Invocation

```
Agent(model="opus", prompt="<advisor prompt>")
```

The subagent has NO tools — it provides reasoning and structured decisions only.

### When to Use

This is reserved for **contested review triage** (Stage 6 of crew:go):

**Condition**: Reviewer verdicts split (not unanimous) on same files.
**Purpose**: Triage which reviewer findings are genuine vs false positives.

### Prompt Template

```
You are an Advisor providing diagnostic judgment. You have NO tools.
Respond in under 500 tokens with a structured decision.

## Situation
{situation_type}: {brief_description}

## Context
- Step: {step_id} — {step_description}
- Conflict: {conflict_summary}
- Reviewer verdicts: {verdict_details}
- Files involved: {file_list}

## Your Task
For each contested finding, classify as:
- GENUINE: Real issue that needs fixing. Reason: ...
- FALSE_POSITIVE: Not a real issue. Reason: ...

## Verdicts
{structured verdicts}
```

### Response Consumption

The orchestrator reads the response inline (not written to file).
Only GENUINE findings are forwarded to the Fix stage.
FALSE_POSITIVE findings are logged but not acted on.

### Cost Control

- Max response: 500 tokens (enforced via prompt instruction)
- Max explicit subagent calls per workflow: 3 (tracked in `auto-state.json` → `advisor.calls_made`)
- tools: none (no tool tokens consumed)
- Only triggered on contested review path, never on happy path

### Opt-Out

Flag: `--no-advisor` on `/crew:go`
Config: `config.advisor_enabled: false` in `auto-state.json`
When disabled, contested reviews fall back to majority-vote resolution.

## Migration Notes

Previously, the advisor protocol also covered:
- **Execution Recovery (Stage 4)**: Diagnosis after consecutive failures
- **QA Stall (Stage 5)**: Determining real bug vs flaky check

These are now handled by the built-in advisor. The executor (with `/advisor` active)
naturally consults Opus during recovery attempts, making explicit subagent calls
at these decision points redundant.
