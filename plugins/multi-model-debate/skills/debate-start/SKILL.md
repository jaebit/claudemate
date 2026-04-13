---
name: debate-start
description: "Start a multi-model debate on a software engineering topic. Use when the user invokes /debate:start with a topic to evaluate using Claude, Codex, and Gemini in parallel."
argument-hint: "<topic> [--context <files>] [--perspectives <p1,p2,p3>] [--rounds <N>]"
disable-model-invocation: true
---

# Debate Start

Launch and orchestrate a structured multi-model debate with Claude, Codex, and Gemini.
Round dispatch runs inline (MCP accessible), synthesis/consensus delegates to `debate-orchestration` (fork).

## Instructions

1. **Parse arguments:**
   - `topic` (required): The debate topic or decision question
   - `--context <files>`: Comma-separated file paths or glob patterns to include as context
   - `--perspectives <p1,p2,p3>`: Custom perspective labels for each agent (Claude, Codex, Gemini)
   - `--rounds <N>`: Number of debate rounds (default: 2)

2. **Verify prerequisites:**
   - Check Codex MCP tool: ToolSearch로 `mcp__plugin_codex-cli_codex__codex` 확인
   - Check Gemini CLI: run `which gemini` via Bash
   - If Codex MCP unavailable → set `codex_mode: "cli_fallback"` (see Fallback section)
   - If Gemini missing → report and stop

3. **Read context files** (if `--context` provided):
   - Resolve glob patterns with Glob tool
   - Read each file with Read tool
   - Concatenate as shared context for all agents

3.5. **External Knowledge Pre-loading** (선택적 — 도메인 지식 의존 토론 시):
   - 토픽이 사회정책·법제·기술 트렌드 등 외부 지식에 의존하는 경우, 모델 디스패치 전에 관련 지식을 수집
   - 다음 Tavily 검색 3개를 병렬 실행:
     ```
     Query 1: "<topic> latest research/regulation [year]"
     Query 2: "<topic> empirical evidence impact study [year]"
     Query 3: "한국 <topic> 현황 법제 [year]"  (한국 관련 시)
     ```
   - 수집한 핵심 정보(300-500단어)를 `## Pre-loaded Knowledge` 섹션으로 정리
   - 모든 모델 프롬프트에 동일하게 포함 → 공통 사실 기반 확보

4. **SETUP:**
   - Generate debate-id: `YYYYMMDD-HHMMSS-<topic-slug>` (slug: lowercase, hyphens, max 30 chars)
   - Create `.debate/<debate-id>/`
   - Assign perspectives (if not provided via `--perspectives`):

     | Topic Category | Claude | Codex | Gemini |
     |---|---|---|---|
     | Architecture decisions | Scalability-focused | Developer experience | Cost realism |
     | Library/framework choice | Performance/benchmarks | Ecosystem/community | Long-term maintenance |
     | General | Advocate | Skeptic | Pragmatist |

     Auto-detect category from topic keywords. Default to General if unclear.

   - Extract 1-5 decision points from topic
   - Initialize `state.json`:
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
       "codex_mode": "mcp",
       "workers": {
         "claude": { "role": "..." },
         "codex":  { "role": "...", "thread_id": null },
         "gemini": { "role": "..." }
       }
     }
     ```

5. **ROUND DISPATCH** (repeat for each round 1 to N):

   Dispatch all 3 agents **in parallel** (single message, 3 tool calls).
   Use prompt templates from `skills/debate-orchestration/reference.md`.

   - **Codex** (MCP mode):
     - Round 1: `mcp__plugin_codex-cli_codex__codex` with `sandbox: "read-only"`, `approval-policy: "never"`
     - Round 2+: `mcp__plugin_codex-cli_codex__codex-reply` with saved `threadId`
     - Save returned `threadId` → `state.json workers.codex.thread_id`
   - **Claude**: Agent tool (sub-agent with Read/Glob/Grep for codebase research)
   - **Gemini**: Agent tool → sub-agent runs `gemini -p "<prompt>"` via Bash

   Round 2+ uses cross-examination prompts — include opposing arguments from synthesis.

   **Save results:** `round-{N}-claude.md`, `round-{N}-codex.md`, `round-{N}-gemini.md`
   **Update state.json:** `currentRound: N`, `lastCompletedPhase: "round-N"`

6. **SYNTHESIS** (after each round):
   - Execute the `debate-orchestration` skill — reads round files, produces synthesis
   - Read `synthesis-round-{N}.md` to check resolution status
   - **Early exit**: If ALL decision points reached Agreement → skip remaining rounds
   - If round count exceeds 3 → ask user before continuing

7. **FINAL CONSENSUS** (after all rounds or early exit):
   - Ensure `state.json` reflects readiness for consensus
   - Execute the `debate-orchestration` skill for final report generation
   - Display summary to user with path to full report

## Codex CLI Fallback (Windows / MCP 미지원 세션)

ToolSearch로 `mcp__plugin_codex-cli_codex__codex` 미확인 시:
1. `state.json`에 `"codex_mode": "cli_fallback"` 기록
2. Codex 실행: `codex exec -s read-only "<prompt>"` (Bash tool, `run_in_background: false`)
   - **출력을 Bash 결과로 받아 Write tool로 파일 저장** (셸 리디렉션 비사용 — Windows 호환)
   - `-s read-only` 필수, `-q` / `--full-auto` 금지
   - Round 2+: threadId 연속 불가 — 이전 라운드 컨텍스트를 프롬프트에 직접 포함

## Usage Examples

```
/debate:start "Should we use REST or GraphQL for our API?"
/debate:start "Monorepo vs polyrepo" --context src/package.json,docs/architecture.md
/debate:start "Next.js vs Remix vs Astro" --perspectives "Performance,DX,Ecosystem" --rounds 3
```
