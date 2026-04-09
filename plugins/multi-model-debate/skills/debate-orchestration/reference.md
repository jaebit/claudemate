# Debate Prompt Templates

## Round 1 — Independent Evaluation Prompt

```
You are evaluating a software engineering decision.

Topic: {topic}
Your perspective: {perspective}
Decision points to address: {decisionPoints}

{context if provided}

For each decision point, provide:
1. Your recommendation
2. Supporting evidence (benchmarks, ecosystem data, real-world examples)
3. Risks and trade-offs
4. Confidence level (High/Medium/Low)

Format as markdown with ## headers per decision point.
```

## Round 2+ — Cross-Examination Prompt

```
You previously evaluated: {topic}
Your perspective: {perspective}
Your original position: {agent's round N-1 response}

Other agents disagreed on these points:
{opposing arguments from other agents}

For each contested point:
1. State: [MAINTAIN] or [MODIFY] your position
2. Evaluate the opposing arguments (which are strong? which are weak?)
3. If MODIFY: explain what changed your mind
4. Final recommendation with updated confidence
```

## Agent Dispatch Patterns

**Claude** (Agent tool, sub-agent):
```
prompt: "<prompt with Claude perspective>"
subagent_type: "general-purpose"
description: "Debate round {N} Claude evaluation"
```
The sub-agent may use Read/Glob/Grep to research the codebase if context is relevant.

**Codex** (MCP tool — Round 1, initial call):
```
tool: mcp__plugin_codex-harness_codex__codex
prompt: "<prompt with Codex perspective>"
sandbox: "read-only"
approval-policy: "never"
developer-instructions: "Role: {perspective}. Evaluate read-only. Do not spawn internal subagents."
```
→ Save returned `threadId` to `state.json workers.codex.thread_id`.

**Codex** (MCP tool — Round 2+, cross-examination):
```
tool: mcp__plugin_codex-harness_codex__codex-reply
threadId: <state.json workers.codex.thread_id>
prompt: "<cross-examination prompt with opposing arguments>"
```

**Gemini** (Agent tool → Bash):
```
prompt: "Run Gemini CLI to evaluate the debate topic"
subagent_type: "general-purpose"
description: "Debate round {N} Gemini evaluation"
```
The sub-agent runs: `gemini -p "<prompt with Gemini perspective>"`

## Synthesis Comparison Table Template

```markdown
### Decision Point: {name}

| Aspect | Claude | Codex | Gemini |
|--------|--------|-------|--------|
| Recommendation | ... | ... | ... |
| Key argument | ... | ... | ... |
| Confidence | ... | ... | ... |

**Status**: Agreement (3:0) / Majority (2:1) / Disagreement (1:1:1)
```

## Final Report Structure (`report.md`)

```markdown
# Debate Report: {topic}

**Date**: {date}
**Rounds**: {N}
**Participants**: Claude ({perspective}), Codex ({perspective}), Gemini ({perspective})

## Executive Summary
{2-3 sentence overview of the debate outcome}

## Decision Points

### {Decision Point 1}
| | Claude | Codex | Gemini |
|---|---|---|---|
| Final Position | ... | ... | ... |
| Confidence | ... | ... | ... |

**Verdict**: {Unanimous / Majority / No consensus}
**Recommendation**: {final recommendation}
**Rationale**: {key reasoning}

## Consensus Items
{List of decisions where all agents agreed, with brief rationale}

## Contested Items
{List of decisions where disagreement remained, with each position summarized}

## Recommended Actions
1. {Concrete next step}
2. {Concrete next step}
```
