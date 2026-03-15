---
name: debate-orchestration
description: "Orchestrate a structured multi-model debate using Claude, Codex, and Gemini as participants. Use when the user wants multiple AI perspectives on a software engineering decision, structured evaluation of technical options, or consensus building across AI agents."
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
---

# Debate Orchestration

5-phase structured debate process using Claude, Codex, and Gemini as independent evaluators.

## Phase 1: SETUP

1. **Generate debate-id** if not provided: `YYYYMMDD-HHMMSS-<topic-slug>`
2. **Create output directory**: `.debate/<debate-id>/`
3. **Assign perspectives** (if user didn't specify via `--perspectives`):

   | Topic Category | Claude | Codex | Gemini |
   |---|---|---|---|
   | Architecture decisions | Scalability-focused | Developer experience | Cost realism |
   | Library/framework choice | Performance/benchmarks | Ecosystem/community | Long-term maintenance |
   | General | Advocate | Skeptic | Pragmatist |

   Auto-detect category from topic keywords. Default to General if unclear.

4. **Extract decision points**: Analyze the topic and identify 1-5 specific decision points that need resolution
5. **Initialize `state.json`**:
   ```json
   {
     "debateId": "<debate-id>",
     "topic": "<topic>",
     "perspectives": { "claude": "...", "codex": "...", "gemini": "..." },
     "decisionPoints": ["..."],
     "rounds": <N>,
     "currentRound": 0,
     "lastCompletedPhase": "setup",
     "status": "in-progress"
   }
   ```

## Phase 2: ROUND 1 — Independent Evaluation

Dispatch all 3 agents **in parallel** (single message, 3 tool calls):

### Shared Prompt Template

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

### Agent Dispatch

**Claude** (Agent tool, sub-agent):
```
prompt: "<shared prompt with Claude perspective>"
subagent_type: "general-purpose"
description: "Debate round {N} Claude evaluation"
```
The sub-agent may use Read/Glob/Grep to research the codebase if context is relevant.

**Codex** (MCP tool):
```
tool: mcp__plugin_codex-harness_codex__codex
prompt: "<shared prompt with Codex perspective>"
sandbox: "read-only"
```

**Gemini** (Agent tool → Bash):
```
prompt: "Run Gemini CLI to evaluate the debate topic"
subagent_type: "general-purpose"
description: "Debate round {N} Gemini evaluation"
```
The sub-agent runs: `gemini -p "<shared prompt with Gemini perspective>"`

### Save Results
- `round-{N}-claude.md`
- `round-{N}-codex.md`
- `round-{N}-gemini.md`
- Update `state.json`: `currentRound: 1`, `lastCompletedPhase: "round-1"`

## Phase 3: SYNTHESIS — Comparative Analysis

The orchestrator performs this directly (no sub-agents).

1. **Read all round files** for the current round
2. **Build comparison table** per decision point:

   ```markdown
   ### Decision Point: {name}

   | Aspect | Claude | Codex | Gemini |
   |--------|--------|-------|--------|
   | Recommendation | ... | ... | ... |
   | Key argument | ... | ... | ... |
   | Confidence | ... | ... | ... |

   **Status**: Agreement (3:0) / Majority (2:1) / Disagreement (1:1:1)
   ```

3. **Classify each decision point**:
   - **Agreement (3:0)**: All three align — mark as resolved
   - **Majority (2:1)**: Two agree, one dissents — carry to next round
   - **Disagreement (1:1:1)**: No alignment — carry to next round

4. **Save**: `synthesis-round-{N}.md`
5. **Update `state.json`**: `lastCompletedPhase: "synthesis-{N}"`

**Early exit**: If ALL decision points reach Agreement, skip remaining rounds and go directly to Phase 5 (Final Consensus).

## Phase 4: ROUND 2+ — Cross-Examination

Only runs for Majority/Disagreement items. Skipped items marked as resolved.

### Cross-Examination Prompt Template

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

Dispatch 3 agents in parallel (same pattern as Phase 2).

### Save Results
- `round-{N}-claude.md`, `round-{N}-codex.md`, `round-{N}-gemini.md`
- Run Phase 3 (Synthesis) again for this round
- If more rounds remain AND unresolved items exist, repeat Phase 4
- If round count exceeds 3, ask user before continuing

## Phase 5: FINAL CONSENSUS

The orchestrator generates the final report.

### Report Structure (`report.md`)

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

### {Decision Point 2}
...

## Consensus Items
{List of decisions where all agents agreed, with brief rationale}

## Contested Items
{List of decisions where disagreement remained, with each position summarized}

## Recommended Actions
1. {Concrete next step}
2. {Concrete next step}
...
```

### Finalize
- Save `report.md`
- Update `state.json`: `status: "completed"`, `lastCompletedPhase: "final-consensus"`
- Display summary to user with path to full report
