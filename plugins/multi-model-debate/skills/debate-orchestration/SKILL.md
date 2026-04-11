---
name: debate-orchestration
description: "Orchestrate a structured multi-model debate using Claude, Codex, and Gemini as participants. Use when the user wants multiple AI perspectives on a software engineering decision, structured evaluation of technical options, or consensus building across AI agents."
user-invocable: false
context: fork
agent: general-purpose
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
---

# Debate Orchestration

5-phase structured debate process using Claude, Codex, and Gemini as independent evaluators.

For detailed prompt templates and report structure, see [reference.md](reference.md).

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
     "rounds": "<N>",
     "currentRound": 0,
     "lastCompletedPhase": "setup",
     "status": "in-progress",
     "workers": {
       "claude": { "role": "...", "thread_id": null },
       "codex":  { "role": "...", "thread_id": null },
       "gemini": { "role": "...", "thread_id": null }
     }
   }
   ```
   Populate `workers[*].role` from the assigned perspectives above.

## Phase 2: ROUND 1 — Independent Evaluation

Dispatch all 3 agents **in parallel** (single message, 3 tool calls) using the shared prompt template from [reference.md](reference.md).

- **Codex**: use the initial `codex` MCP tool call (see reference.md for params). After the call completes, save the returned `threadId` → `state.json workers.codex.thread_id`.
- **Claude / Gemini**: Agent tool as usual.

> **Codex CLI Fallback** (MCP 미지원 세션): ToolSearch로 `mcp__plugin_codex-cli_codex__codex` 미확인 시:
> 1. `state.json`에 `"codex_mode": "cli_fallback"` 기록
> 2. `codex exec -s read-only "<prompt>" > .debate/<id>/round-N-codex.md` 실행
>    - `-s read-only` 필수 (미지정 시 실패), `-q` / `--full-auto` 금지
>    - **`run_in_background: true` 시 반드시 `> <file>` 리디렉션을 명령에 직접 포함** — 미포함 시 파일 생성 실패 (gen-048 사례)
>    - Round 2+에서는 이전 컨텍스트를 프롬프트에 직접 포함 (threadId 연속 불가)

### Save Results
- `round-{N}-claude.md`, `round-{N}-codex.md`, `round-{N}-gemini.md`
- Update `state.json`: `currentRound: 1`, `lastCompletedPhase: "round-1"`, `workers.codex.thread_id: <saved>`

## Phase 3: SYNTHESIS — Comparative Analysis

The orchestrator performs this directly (no sub-agents).

1. **Read all round files** for the current round
2. **Build comparison table** per decision point (see template in [reference.md](reference.md))
3. **Classify each decision point**:
   - **Agreement (3:0)**: All three align — mark as resolved
   - **Majority (2:1)**: Two agree, one dissents — carry to next round
   - **Disagreement (1:1:1)**: No alignment — carry to next round
4. **Save**: `synthesis-round-{N}.md`
   - **분리 규칙**: `synthesis-round-{N}.md`는 반드시 `report.md`와 **별도 파일**로 저장. report.md에 synthesis 내용을 복사·통합 금지.
   - Round 2가 단일 DP 집중이더라도 `synthesis-round-2.md` 별도 파일 필수.
5. **Update `state.json`**: `lastCompletedPhase: "synthesis-{N}"`

**Early exit**: If ALL decision points reach Agreement, skip remaining rounds and go directly to Phase 5.

## Phase 4: ROUND 2+ — Cross-Examination

Only runs for Majority/Disagreement items. Skipped items marked as resolved.

Use cross-examination prompt template from [reference.md](reference.md). Dispatch 3 agents in parallel (same pattern as Phase 2).

- **Codex**: if `state.json workers.codex.thread_id` is set, use `codex-reply` with that threadId (maintains context from round 1). If null (e.g., round 1 failed to save), fall back to a new `codex` call.

### Save Results
- `round-{N}-claude.md`, `round-{N}-codex.md`, `round-{N}-gemini.md`
- Run Phase 3 (Synthesis) again for this round
- If more rounds remain AND unresolved items exist, repeat Phase 4
- If round count exceeds 3, ask user before continuing

## Phase 5: FINAL CONSENSUS

Generate the final report using the structure from [reference.md](reference.md).

**필수 규칙**:
- `report.md`에 **Contested Items / Unresolved Items 섹션 필수** — 모든 DP가 합의에 도달했더라도 가장 약한 합의 항목을 "잠재적 재검토 후보"로 명시
- Recommended Actions에 **P0/P1/P2 우선순위 레이블**과 의존성 명시 필수

### Finalize
- Save `report.md`
- Update `state.json`: `status: "completed"`, `lastCompletedPhase: "final-consensus"`
- Display summary to user with path to full report
