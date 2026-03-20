---
name: track
description: >
  This skill should be used when the user asks "진행률 보여줘", "Phase 어디까지 왔어?", "track",
  "로드맵 현황", "Sprint 진행 상태", or wants phase-based progress percentages with Exit Criteria
  fulfillment rates — for structural presence checklists (exists/not exists) use spec-sync instead.
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /track — 로드맵 Phase 진행률

git log, 소스 구조, 테스트 상태를 분석하여 로드맵 Phase별 진행률을 산출한다.

## 참조

이 스킬을 실행하기 전에 반드시 `_shared/arix-rules.md`를 읽어 규칙 전체를 파악한다.

## 절차

### Step 1: Phase 정의 로드

`_shared/arix-rules.md` §13 로드맵 Phase 요약과 `docs/architecture-v3.md` §14 통합 로드맵에서 각 Phase/Sprint의 Exit Criteria를 추출한다.

### Step 2: Exit Criteria별 상태 확인

각 Exit Criteria를 검증 가능한 조건으로 분해하여 확인한다.

**Phase 1-A Foundation:**
- [ ] State Schema 7영역 PG 테이블 → `src/Arix.Execution.StateStore/` 내 마이그레이션/스키마 파일 존재 여부
- [ ] Registry manifest resolve API → `src/Arix.Registry.Api/` 내 resolve 엔드포인트 존재 여부
- [ ] OTel 기본 → `Arix.BuildingBlocks.Observability` 내 OTel 설정 존재 여부

**Phase 1-B Core Engine:**
- [ ] WF Engine core + 5 step runner → `src/Arix.Execution.Workflow/` 내 AgentStep, ToolStep, WaitInputStep, EvalStep, BranchStep runner 존재 여부
- [ ] Eval Suite MVP → `src/Arix.Execution.Eval/` 내 schema + policy check 존재 여부

**Phase 1-C App Shell:**
- [ ] App Runtime lifecycle → `src/Arix.Execution.AppRuntime/` 내 ManifestLoader, ContextLoader 등 존재 여부
- [ ] Interview Coach App → `apps/interview-coach/` 내 app.yaml + workflow 존재 여부

### Step 3: git log 분석

최근 커밋 내역에서 각 Phase 관련 작업 빈도를 분석한다:

```bash
git log --oneline --since="2 weeks ago" -- src/Arix.Execution.*
git log --oneline --since="2 weeks ago" -- src/Arix.Registry.*
```

### Step 4: 진행률 보고서

```
## Phase 진행률 보고서

### Phase 1-A Foundation (목표: ~3주)
진행률: ██████░░░░ 60%

| Exit Criteria | 상태 | 근거 |
|--------------|------|------|
| PG State 테이블 | ✅ 완료 | 마이그레이션 파일 존재 |
| manifest resolve API | 🔧 진행중 | 엔드포인트 존재, 테스트 미완 |
| OTel 기본 | ❌ 미시작 | |

### Phase 1-B Core Engine (목표: ~4주)
진행률: ██░░░░░░░░ 20%
...

### 전체 요약
- Phase 1 전체: 40% (10/25 criteria 충족)
- 가장 큰 블로커: Eval Suite MVP 미시작
- 최근 2주 활동: Registry 관련 커밋 12건, Execution 관련 커밋 8건
```
