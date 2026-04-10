# Advisor Protocol (Escape Hatch)

Defines when and how the crew:go orchestrator consults an Opus-tier advisor
for judgment-only guidance at decision points.

## Overview

The Advisor is a tool-less Opus subagent spawned for diagnostic judgment only.
It cannot read files, write code, or execute commands. It receives a structured
situation summary and returns a triage decision under 500 tokens.

## Invocation

```
Agent(model="opus", prompt="<advisor prompt>")
```

The advisor has NO tools — it provides reasoning and decisions only.

## When to Consult

### Trigger 1: Execution Recovery (Stage 4)

**Condition**: `consecutive_failures >= 2` AND Fixer-Haiku has already failed.
**Position in recovery chain**: retry → Fixer-Haiku → **ADVISOR** → Planner-Haiku → skip → abort
**Purpose**: Diagnose *why* the step keeps failing before trying a different approach.

### Trigger 2: Contested Review (Stage 6)

**Condition**: Reviewer verdicts split (not unanimous) on same files.
**Purpose**: Triage which reviewer findings are genuine vs false positives.

### Trigger 3: QA Stall (Stage 5)

**Condition**: Same issue hash appears in 2 consecutive QA cycles.
**Purpose**: Determine if the issue is a real bug or a flaky/misconfigured check.

## Prompt Template

```
You are an Advisor providing diagnostic judgment. You have NO tools.
Respond in under 500 tokens with a structured decision.

## Situation
{situation_type}: {brief_description}

## Context
- Step: {step_id} — {step_description}
- Error/Conflict: {error_or_conflict_summary}
- Prior attempts: {what_was_tried}
- Files involved: {file_list}

## Your Task
Provide ONE of these decisions:
1. RETRY_WITH_HINT: "The likely root cause is X. Instruct the builder/fixer to Y."
2. REPLAN: "This step should be decomposed differently. Suggest: Z."
3. SKIP: "This failure is non-blocking because X. Safe to skip."
4. ESCALATE: "This requires human judgment because X."

## Decision
{decision_type}: {reasoning}
```

## Response Consumption

The orchestrator reads the advisor response inline (not written to file).
Based on the decision_type:

| Decision | Orchestrator Action |
|----------|-------------------|
| RETRY_WITH_HINT | Pass hint to next recovery agent's prompt |
| REPLAN | Invoke Planner-Haiku with advisor's suggestion |
| SKIP | Mark step skipped, log advisor reasoning, continue |
| ESCALATE | Pause workflow, surface advisor reasoning to user |

## Cost Control

- Max response: 500 tokens (enforced via prompt instruction)
- Max advisor calls per workflow: 3 (tracked in `auto-state.json` → `advisor.calls_made`)
- tools: none (no tool tokens consumed)
- Only triggered on failure/conflict paths, never on happy path

## Opt-Out

Flag: `--no-advisor`
Config: `config.advisor_enabled: false`
When disabled, the recovery chain skips the advisor step entirely
(existing behavior: retry → Fixer-Haiku → Planner-Haiku → skip → abort).
