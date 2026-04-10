# 도메인 지식 갭 기록

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
