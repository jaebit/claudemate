# Multi-Model Debate 스킬

multi-model-debate 플러그인(`plugins/multi-model-debate/`)을 사용한 토론 태스크에서
출력 아티팩트 규격, CLI fallback 절차, acceptance criteria 패턴을 정의합니다.

## 적용 시점

- autohone Worker가 multi-model-debate 플러그인의 토론 스킬을 실행할 때
  (플러그인 스킬: `plugins/multi-model-debate/skills/debate-start/`, `debate-orchestration/` — autohone 미등록)
- Sprint Contract에 `skills_needed`로 `multi-model-debate`가 포함된 경우

## 출력 아티팩트 규격

### 필수 파일 (모두 `.debate/<debate-id>/` 디렉토리 내)

| 파일 | 설명 | 생성 시점 |
|------|------|----------|
| `state.json` | 진행 상태 추적 (status, currentRound, lastCompletedPhase) | SETUP |
| `round-{N}-claude.md` | Claude 라운드 N 응답 | ROUND N |
| `round-{N}-codex.md` | Codex 라운드 N 응답 | ROUND N |
| `round-{N}-gemini.md` | Gemini 라운드 N 응답 | ROUND N |
| `synthesis-round-{N}.md` | 라운드 N 비교 분석 | SYNTHESIS N |
| `report.md` | 최종 합의 보고서 | FINAL CONSENSUS |

### synthesis-round-{N}.md 분리 규칙

`synthesis-round-{N}.md`는 **반드시** `report.md`와 별도 파일로 생성해야 합니다.
- Round 1 synthesis: `synthesis-round-1.md`
- Round 2 synthesis: `synthesis-round-2.md` (report.md에 통합하지 않음)
- report.md는 최종 합의만 포함. synthesis 내용을 참조하되 복사하지 않음.

### report.md 필수 섹션

1. Executive Summary
2. Decision Points (결정 포인트별 3-모델 비교 테이블)
3. **Consensus Items** (합의 항목)
4. **Contested Items / Unresolved Items** (미해결 항목 — 아래 참조)
5. Recommended Actions

### unresolved_items 섹션 (필수)

Round 2에서도 합의에 도달하지 못한 항목을 명시적으로 기록합니다.
모든 결정 포인트가 합의에 도달하더라도 이 섹션을 유지하고, 다음 중 하나를 기록:
- 실제 미해결 이견 (있는 경우)
- "모든 결정 포인트가 Round 2에서 합의에 도달. 잠재적 재검토 후보:" + 가장 약한 합의 항목

이유: Round 2 만장일치 수렴이 프롬프트에 의한 과도한 합의인지, 실질적 합의인지 구분.

## Codex CLI Fallback 절차

### SETUP 단계 필수 체크

```
1. Codex MCP 도구 확인: ToolSearch로 mcp__plugin_codex-cli_codex__codex 검색
2. 사용 가능 → MCP 도구 사용 (SKILL.md 원래 규격)
3. 사용 불가 → CLI fallback:
   a. `codex --version` 확인
   b. state.json에 "codex_mode": "cli_fallback" 기록
   c. Round N에서 `codex exec "<prompt>"` 사용
      - `-q` 플래그 사용 금지 (미지원)
      - 출력 파싱: "tokens used" 이전까지가 실제 응답
      - timeout: 300초 (웹 리서치 포함 시 지연 가능)
```

### CLI vs MCP 차이점

| 항목 | MCP | CLI fallback |
|------|-----|-------------|
| threadId 연속 대화 | 지원 | 미지원 — Round 2에서 이전 컨텍스트를 프롬프트에 직접 포함 |
| 웹 검색 | 미지원 | 자동 수행 (GPT-5.4 기본 동작) |
| 병렬 디스패치 | Agent 도구와 동일 메시지 | Bash background (`run_in_background: true`) |

## Acceptance Criteria 패턴

### macOS 호환 패턴 (필수)

macOS의 `wc -l`은 앞쪽 공백을 포함한 숫자를 출력합니다.
`grep '^[1-9]'` 패턴이 실패하므로, 다음 패턴을 사용합니다:

```bash
# 파일 존재 확인 (macOS 호환)
[ $(ls .debate/20260410-*/state.json 2>/dev/null | wc -l | tr -d ' ') -ge 1 ]

# 파일 개수 확인 (macOS 호환)
[ $(ls .debate/20260410-*/round-1-*.md 2>/dev/null | wc -l | tr -d ' ') -eq 3 ]

# 대안 패턴
ls .debate/20260410-*/state.json 2>/dev/null | wc -l | awk '{exit($1<1)}'
```

### 콘텐츠 검증 기준 (필수 포함)

파일 존재만 확인하면 빈 파일도 PASS. 반드시 다음을 포함:
- round 파일 최소 크기: `[ $(wc -l < "$f" | tr -d ' ') -ge 10 ]`
- report.md 결정 포인트 키워드: `grep -qE '(키워드1|키워드2|...) report.md'`
- report.md 결론 섹션: `grep -qiE '(결론|합의|consensus|recommendation)' report.md`
- synthesis 키워드 커버리지: `grep -cE '(키워드)' synthesis.md` >= 2

## 응답 품질 기준 (v1.1.0)

### 각 모델 Round 1 응답 최소 분량

모든 참여 모델(Claude, Codex, Gemini)의 Round 1 응답은 **결정 포인트(DP)당 최소 150단어** 이상이어야 합니다.

Gemini CLI(`gemini -p`)의 응답이 짧은 경향이 있으므로, 프롬프트에 다음을 명시합니다:
```
Be thorough — at least 300 words per decision point.
```

Round 1 파일이 기준 미달 시 프롬프트를 보강하여 재실행하거나, synthesis에서 해당 모델의 분석이 얕음을 명시합니다.

### report.md Recommended Actions 우선순위

Recommended Actions에 **P0/P1/P2 우선순위 레이블**과 **의존성**을 명시합니다:

```markdown
## Recommended Actions

1. **[P0]** Vault PoC 초기화 — 다른 모든 액션의 전제
2. **[P0]** Frontmatter 표준 문서화 — vault 구조와 동시 진행 가능
3. **[P1]** Zone-Based Editing 구현 — vault PoC 완료 후 (depends: #1)
4. **[P1]** MCP Server 프로토타입 — vault PoC 완료 후 (depends: #1)
5. **[P2]** 벤치마크 — MCP 완료 후 (depends: #4)
```

## 병렬 디스패치 규칙

Round 1 및 Round 2에서 3개 모델을 **단일 메시지에서 동시 디스패치**:

```
# 동일 메시지에서 3개 도구 호출
1. Agent(description="Round N: Claude", run_in_background=true)
2. Bash(command="codex exec ...", run_in_background=true)  # 또는 MCP 도구
3. Agent(description="Round N: Gemini → gemini -p", run_in_background=true)
```

Codex CLI가 Bash로 실행되므로 Agent 도구와 완전한 병렬은 아닐 수 있으나,
`run_in_background: true`로 비동기 실행하여 대기 시간을 최소화합니다.

## 골든 예제 참조

- `multi-model-debate-gen-001.yaml` (score: 0.86)
- 성공 요인: synthesis-round-1.md의 명확한 의결 구조(2:1/3:0), Round 2 MODIFY의 증거 기반 수렴
- 개선 필요: synthesis-round-2.md 별도 생성, unresolved_items 섹션 추가
