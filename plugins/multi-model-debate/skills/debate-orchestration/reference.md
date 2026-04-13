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

> **Architecture Note**: These dispatch patterns are used by `debate-start` (inline context),
> NOT by `debate-orchestration`. The orchestration skill only performs synthesis and consensus
> — it reads pre-collected round files and never dispatches agents or calls MCP tools.

**Claude** (Agent tool, sub-agent):
```
prompt: "<prompt with Claude perspective>"
subagent_type: "general-purpose"
description: "Debate round {N} Claude evaluation"
```
The sub-agent may use Read/Glob/Grep to research the codebase if context is relevant.

**Codex** (MCP tool — Round 1, initial call):
```
tool: mcp__plugin_codex-cli_codex__codex
prompt: "<prompt with Codex perspective>"
sandbox: "read-only"
approval-policy: "never"
developer-instructions: "Role: {perspective}. Evaluate read-only. Do not spawn internal subagents."
```
→ Save returned `threadId` to `state.json workers.codex.thread_id`.

**Codex** (MCP tool — Round 2+, cross-examination):
```
tool: mcp__plugin_codex-cli_codex__codex-reply
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

**Codex CLI Fallback** (MCP 미지원 세션):
```bash
# run_in_background=true 시 반드시 > file 리디렉션을 명령에 직접 포함
# 미포함 시 round-N-codex.md 생성 실패 (gen-048 사례)
codex exec -s read-only "<prompt>" > .debate/<id>/round-N-codex.md
# 금지: -q 플래그, --full-auto 플래그
# Round 2+: threadId 연속 불가 — 이전 컨텍스트를 프롬프트에 직접 포함
```

> **Gemini 품질 기준**: 줄 수가 짧아도 (예: 55줄) 바이트 기준으로 충분할 수 있음.
> AC 설계 시 줄 수 대신 바이트 기준 권고: `[ $(wc -c < file | tr -d ' ') -ge 2000 ]`

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

## Contested Items / Unresolved Items
{List of decisions where disagreement remained, with each position summarized.
모든 DP가 합의에 도달했더라도 이 섹션을 유지 — 가장 약한 합의 항목을 "잠재적 재검토 후보"로 기록.}

## Recommended Actions
1. **[P0]** {즉시 실행 가능하거나 다른 액션의 선행 조건}
2. **[P0]** {동시 진행 가능한 핵심 작업}
3. **[P1]** {P0 완료 후 실행} (depends: #1)
4. **[P2]** {선택적 개선·검증} (depends: #3)

<!-- P0: 선행 조건·즉시 고임팩트 | P1: P0 후 핵심 기능 | P2: 선택적 개선 -->
```
