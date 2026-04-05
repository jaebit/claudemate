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
