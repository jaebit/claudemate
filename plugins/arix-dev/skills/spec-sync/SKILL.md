---
name: spec-sync
description: >
  This skill should be used when the user asks "설계 대비 구현 상태 확인해줘", "spec sync 해줘",
  "뭐가 구현됐어?", "구현 체크리스트 만들어줘", "설계서랑 소스 비교해줘", or wants to check which
  design-doc components actually exist in the source tree. Generates a structural presence checklist
  (exists / not exists) — for phase progress percentages use track instead.
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /spec-sync — 설계 문서 → 구현 상태 체크리스트

설계 문서(architecture-v3, repo-design-v1)에 정의된 구조와 현재 소스 디렉토리를 비교하여 구현 상태 체크리스트를 생성한다.

## 참조

이 스킬을 실행하기 전에 반드시 `_shared/arix-rules.md`를 읽어 규칙 전체를 파악한다.

## 절차

### Step 1: 설계 문서 로드

다음 파일들을 읽는다:
- `docs/architecture-v3.md` — 6-Layer 아키텍처, 컴포넌트 정의
- `docs/repo-design-v1.md` — 프로젝트 구조, 솔루션 레이아웃
- `_shared/arix-rules.md` — 강제 규칙 통합 참조

### Step 2: 프로젝트 구조 매핑

`_shared/arix-rules.md`의 §2 "프로젝트→레이어 매핑 테이블"에 나열된 모든 프로젝트를 대상으로 한다.

각 프로젝트에 대해:
1. `src/` 디렉토리 아래에 해당 프로젝트 폴더가 존재하는지 확인
2. `.csproj` 파일이 존재하는지 확인
3. 솔루션 파일(`.sln`)에 포함되어 있는지 확인

### Step 3: App 구조 확인

`docs/repo-design-v1.md` §6에 따라 `apps/` 디렉토리의 App 패키지를 확인한다.

각 App에 대해:
- `app.yaml` 존재 여부
- `CONTEXT.md` 존재 여부
- `workflows/` 디렉토리 존재 여부
- `eval-suites/` 디렉토리 존재 여부

### Step 4: SDK/Schema 확인

`sdk/` 디렉토리의 manifest schema 존재 여부:
- `sdk/manifest-schema/app.schema.json`
- `sdk/manifest-schema/workflow.schema.json`
- `sdk/manifest-schema/eval-suite.schema.json`
- `sdk/manifest-schema/state.schema.json`

### Step 5: Infra/Tests 확인

- `tests/Arix.Architecture.Tests/` 존재 여부 (참조 방향 검증 테스트)
- `infra/docker/` 디렉토리 존재 여부
- `infra/compose/` 디렉토리 존재 여부

### Step 6: 로드맵 Phase별 매핑

`_shared/arix-rules.md`의 §13 로드맵 Phase 요약을 기준으로, 현재 존재하는 프로젝트들이 어느 Phase에 해당하는지 매핑한다.

Phase 1 필수 프로젝트:
- `Arix.Execution.Contracts`
- `Arix.Execution.StateStore`
- `Arix.Execution.Workflow`
- `Arix.Registry.Contracts`
- `Arix.Registry.Api`
- `Arix.BuildingBlocks.Core`
- `Arix.BuildingBlocks.Contracts`

### Step 7: 체크리스트 출력

아래 형식으로 결과를 출력한다:

```
## Spec-Sync 체크리스트

### 솔루션 기반
- [x] Arix.Platform.sln 존재
- [ ] Arix.Execution.Contracts — 미생성

### Phase 1 필수 (Pilot MVP)
- [x] Arix.Execution.StateStore — 존재, .csproj 확인
- [ ] Arix.Execution.Workflow — 미생성

### Phase 2 (Team)
...

### App 패키지
- [ ] apps/interview-coach — 미생성
...

### SDK/Schema
- [ ] sdk/manifest-schema/app.schema.json — 미생성
...

### 불일치 사항
- ⚠️ src/Arix.Foo/ 존재하지만 설계 문서에 정의되지 않음
...

### 요약
- 전체: 35개 중 12개 구현 (34%)
- Phase 1: 7개 중 3개 구현 (43%)
- Phase 2: 15개 중 5개 구현 (33%)
```

## 주의사항

- 설계 문서에 없는 프로젝트가 `src/`에 존재하면 "불일치" 섹션에 보고
- `.csproj`만 있고 실질적 코드가 없는 경우 "(빈 프로젝트)" 표시
- Contracts 프로젝트는 항상 해당 레이어의 다른 프로젝트보다 먼저 생성되어야 함을 강조
