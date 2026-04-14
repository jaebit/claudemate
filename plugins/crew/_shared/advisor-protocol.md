# Advisor Protocol

Defines how the crew:go orchestrator uses advisor consultation at decision points.

## Overview

Two advisor mechanisms are available:

1. **Built-in Advisor** (primary): The official Claude Code `/advisor` feature — executor model (Sonnet) automatically consults Opus within a single API call when it encounters hard decisions. No extra round-trips, full conversation context preserved.
2. **Explicit Opus Subagent** (structured triage only): A tool-less Opus subagent spawned for situations requiring structured decision output (e.g., contested review verdict triage).

## Built-in Advisor (Primary)

The official `advisor_20260301` tool type, activated via Claude Code `/advisor`.

### How It Works

- **Executor** (Sonnet 4.6) runs end-to-end: tool calls, file edits, iteration
- **Advisor** (Opus 4.6) provides ~400-700 token strategic guidance when the executor self-determines it needs help
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

Activate in Claude Code: `/advisor` → select Opus 4.6. No additional parameters required.

### Cost

- Advisor tokens reported separately in API response
- Typical cost reduction: ~11.9% per agentic task vs running Opus end-to-end
- SWE-bench: Sonnet + Advisor = 74.8% (vs 72.1% Sonnet solo)

## Explicit Opus Subagent (Structured Triage)

For situations requiring a **structured decision format** (not free-form advice),
spawn a tool-less Opus subagent directly.

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
