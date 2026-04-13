---
name: debate-orchestration
description: "Perform synthesis and consensus analysis for multi-model debate rounds. Invoked by debate-start after each round's agent results are saved. Reads round files, builds comparison tables, and generates final reports."
user-invocable: false
context: fork
agent: general-purpose
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Debate Orchestration — Synthesis & Consensus

Analysis-only orchestration for multi-model debates. Reads pre-collected round result files and produces synthesis or final reports.
**No MCP tools required** — all model outputs are provided as files by `debate-start`.

For detailed templates and report structure, see [reference.md](reference.md).

## Mode Detection

Read `state.json` in the debate directory to determine which phase to execute:

| `lastCompletedPhase` | Action |
|---|---|
| `round-{N}` | Run **Synthesis** for round N |
| `synthesis-{N}` + (`status: "all-resolved"` OR `currentRound >= rounds`) | Run **Final Consensus** |
| `status: "completed"` | Inform — debate already finished |

## Phase: SYNTHESIS — Comparative Analysis

1. **Read all round files** for the current round:
   - `round-{N}-claude.md`, `round-{N}-codex.md`, `round-{N}-gemini.md`

2. **Build comparison table** per decision point (see template in [reference.md](reference.md))

3. **Classify each decision point**:
   - **Agreement (3:0)**: All three align — mark as resolved
   - **Majority (2:1)**: Two agree, one dissents — carry to next round
   - **Disagreement (1:1:1)**: No alignment — carry to next round

4. **Save**: `synthesis-round-{N}.md`
   - **분리 규칙**: `synthesis-round-{N}.md`는 반드시 `report.md`와 **별도 파일**로 저장. report.md에 synthesis 내용을 복사·통합 금지.
   - Round 2가 단일 DP 집중이더라도 `synthesis-round-2.md` 별도 파일 필수.

5. **Update `state.json`**: `lastCompletedPhase: "synthesis-{N}"`
   - If ALL decision points reached Agreement → set `status: "all-resolved"`

## Phase: FINAL CONSENSUS

Generate the final report using the structure from [reference.md](reference.md).

**필수 규칙**:
- `report.md`에 **Contested Items / Unresolved Items 섹션 필수** — 모든 DP가 합의에 도달했더라도 가장 약한 합의 항목을 "잠재적 재검토 후보"로 명시
- Recommended Actions에 **P0/P1/P2 우선순위 레이블**과 의존성 명시 필수

### Finalize
- Save `report.md`
- Update `state.json`: `status: "completed"`, `lastCompletedPhase: "final-consensus"`
- Display summary with path to full report
