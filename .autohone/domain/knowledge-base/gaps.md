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
