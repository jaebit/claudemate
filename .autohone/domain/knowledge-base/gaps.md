# 도메인 지식 갭 기록

## GAP-001 — 숨김 디렉토리 탐색 패턴 (2026-04-11, gen-049)

**발견 경위**: technical-analysis 태스크에서 Worker가 `.claude-plugin/` 숨김 디렉토리를
미탐색하여 plugin.json 전면 누락이라는 허위 양성 생성 → accuracy 0.65

**갭 내용**: 파일시스템 분석 태스크에서 dot-prefix 디렉토리(`.claude-plugin/`, `.autohone/` 등)를
포함한 완전 탐색 패턴이 Worker 프롬프트에 명시되지 않음

**해결 상태**: ✅ domain-expert SKILL.md v1.2.0에 반영 (2026-04-11)
- 체크리스트 항목 1: `fd -H` / `eza -a` 의무화
- 체크리스트 항목 6: Critical Claim 교차 검증 추가

**재발 방지**: Sprint Contract AC에 `fd -H -t f` 기반 검증 명령 포함 권장

Reflector가 태스크 실패 시 도메인 지식 부족을 감지하면 이 파일에 기록합니다.

## 형식

```
### [날짜] [태스크 ID]
- **부족한 지식**: 어떤 지식이 필요했는지
- **영향**: 어떤 실패로 이어졌는지
- **해결 방안**: 어떤 문서/자료가 필요한지
- **상태**: pending | resolved
```

## 기록

### [2026-04-05] Contract Validation 품질 기준 갭 (GAP-001)
- **부족한 지식**: Contract Validation에서 요구하는 acceptance_criteria 품질 기준
- **영향**: 두 태스크에서 동일한 패턴으로 REVISION_NEEDED 반복 발생
- **해결 방안**: 
  - task-planner 스킬에 주관적 기준 금지 가이드라인 추가
  - contract-criteria-validator 스킬로 자동 검증 체계 구축
  - planner-qa-gate 스킬로 사전 품질 검증 수행
- **상태**: resolved (스킬 3개 생성으로 해결)

### [2026-04-10] 언어별 Import 패턴 도메인 지식 갭 (GAP-002)
- **부족한 지식**: Rust/Python/JS의 import aliasing/grouping 패턴이 grep 리터럴 매칭에 미치는 영향
- **영향**: gen-044 Sprint 4에서 `criterion::criterion_group` grep이 `use criterion::{..., criterion_group}` 패턴과 미매칭 → false-negative 1건
- **해결 방안**: 
  - task-planner v1.6.0에 언어별 import 패턴 주의 섹션 추가 (완료)
  - planner-qa-gate v1.2.0에 import 패턴 안전성 검증 단계 추가 (완료)
  - 핵심 규칙: acceptance_criteria에서 심볼 이름만 grep, fully-qualified 경로 지양
- **상태**: resolved (task-planner v1.6.0 + planner-qa-gate v1.2.0으로 해결)

### [2026-04-10] Codex CLI exec 서브커맨드 + 플래그 호환성 갭 (GAP-003)
- **부족한 지식**: Codex CLI의 정확한 서브커맨드 인터페이스 (`codex exec` 필수, `-q` 플래그 미지원)
- **영향**: debate-codebase-wiki 태스크에서 `-q` 플래그 시도 후 실패 → `exec` 서브커맨드로 재시도. 13분 지연 발생
- **해결 방안**:
  - multi-model-debate 스킬 SETUP 섹션에 `codex exec -p <prompt>` 사용법 명시
  - MCP 가용성 우선 체크, unavailable 시 CLI fallback 경고 로그 절차 추가
  - `-q`/`--quiet` 플래그 없이 실행 → 표준 출력 파싱으로 결과 추출
- **상태**: resolved (multi-model-debate 스킬 v1.0.0의 "Codex CLI Fallback 절차" 섹션으로 해결)

### [2026-04-10] macOS wc -l 출력 공백 처리 갭 (GAP-004)
- **부족한 지식**: macOS `wc -l` 명령어가 앞쪽 공백을 포함한 숫자를 출력 (Linux와 동작 차이)
- **영향**: debate-codebase-wiki 태스크에서 `grep '^[1-9]'` acceptance criteria가 ` 55` 형태 출력에 실패
- **해결 방안**:
  - acceptance_criteria에서 `wc -l | tr -d ' '` 파이프 적용 규칙 수립
  - task-planner 스킬에 "macOS wc 공백" 주의 항목 추가 (언어별 import 패턴 절 옆에 병기)
  - 또는 `wc -l | awk '{print $1}'` 대안 패턴 제시
- **상태**: resolved (multi-model-debate 스킬 v1.0.0의 "Acceptance Criteria 패턴" 섹션으로 해결)

### [2026-04-11] 외부 지식 Vault Pre-loading 패턴 갭 (GAP-005)
- **부족한 지식**: 다중 모델 토론에서 도메인 지식을 사전 로딩하여 합의율을 높이는 패턴
- **영향**: gen-045(0.86), gen-046(0.90) — vault 없이 추상적 논거에 의존, DP-3 2:1 미해결 유지
- **해결 방안**:
  - multi-model-debate SKILL.md v1.3.0에 "외부 지식 Pre-loading 패턴" 섹션 추가
  - context.md SETUP 단계에서 Obsidian MCP 또는 이전 debate 결과를 Pre-loaded Knowledge로 포함
- **상태**: resolved (multi-model-debate SKILL.md v1.3.0에 절차 문서화)

### [2026-04-11] DEFERRED 항목 자동 전달 갭 (GAP-006)
- **부족한 지식**: 반성 기록의 DEFERRED action_items를 다음 세대 계획에 자동으로 포함하는 메커니즘
- **영향**: gen-046 DEFERRED 2개 항목이 gen-047에서 동일하게 재발 → 효율성 저하, 중복 실패
- **해결 방안**:
  - task-planner SKILL.md에 "DEFERRED 항목 전달 패턴" 섹션 추가
  - 계획 생성 시 최신 세대 아카이브의 deferred_items 블록 확인 의무화
- **상태**: resolved (task-planner SKILL.md에 체크리스트 항목 및 절차 추가)
