---
name: debate-start
description: "Start a multi-model debate on a software engineering topic. Use when the user invokes /debate:start with a topic to evaluate using Claude, Codex, and Gemini in parallel."
argument-hint: "<topic> [--context <files>] [--perspectives <p1,p2,p3>] [--rounds <N>]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
---

# Debate Start

Launch a structured multi-model debate with Claude, Codex, and Gemini.

## Instructions

1. **Parse arguments:**
   - `topic` (required): The debate topic or decision question
   - `--context <files>`: Comma-separated file paths or glob patterns to include as context
   - `--perspectives <p1,p2,p3>`: Custom perspective labels for each agent (Claude, Codex, Gemini)
   - `--rounds <N>`: Number of debate rounds (default: 2)

2. **Verify prerequisites:**
   - Check Codex MCP tool exists: confirm `mcp__plugin_codex-cli_codex__codex` is available
   - Check Gemini CLI: run `which gemini` via Bash
   - If either fails, report what's missing and stop

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
   - 수집한 핵심 정보(300–500단어)를 `## Pre-loaded Knowledge` 섹션으로 정리
   - 모든 모델 프롬프트에 동일하게 포함 → 공통 사실 기반 확보
   - **효과 실증 (gen-047, gen-048)**: Pre-loading 없이 추상 논거만 사용 시 입장 변경 근거 부족으로 분열 지속.
     법령·판례·실증 보고서 사전 로딩 후 만장일치 수렴 달성.

4. **Create output directory:**
   - Generate debate-id: `YYYYMMDD-HHMMSS-<topic-slug>` (slug: lowercase, hyphens, max 30 chars)
   - Create `.debate/<debate-id>/`

5. **Execute the `debate-orchestration` skill**, passing:
   - topic, context, perspectives, rounds, debate-id, output directory path

## Usage Examples

```
/debate:start "Should we use REST or GraphQL for our API?"
/debate:start "Monorepo vs polyrepo" --context src/package.json,docs/architecture.md
/debate:start "Next.js vs Remix vs Astro" --perspectives "Performance,DX,Ecosystem" --rounds 3
```
