# arix-dev Skill Inventory

## 핵심 스킬 (Phase 1) — 구현 완료

### `/spec-sync` — 설계 문서 → 구현 상태 체크리스트

| 항목 | 내용 |
|------|------|
| 파일 | `skills/spec-sync/SKILL.md` |
| 용도 | 설계 문서(architecture-v3, repo-design-v1) 대비 현재 소스 디렉토리 비교 |
| 입력 | 없음 (자동으로 설계 문서와 소스 구조 비교) |
| 출력 | Phase별 체크리스트 (존재/미존재/불일치), 진행률 요약 |
| 참조 | `_shared/arix-rules.md` §2, §13, §14 |

### `/scaffold` — 설계서 기반 .NET 프로젝트 스캐폴딩

| 항목 | 내용 |
|------|------|
| 파일 | `skills/scaffold/SKILL.md` |
| 용도 | 모듈명 지정 시 repo-design에 따른 프로젝트 구조 생성 |
| 입력 | 모듈명 (예: `Arix.Execution.Workflow`) |
| 출력 | `.csproj`, 폴더 구조, 테스트 프로젝트, 솔루션 등록 |
| 핵심 규칙 | Contracts-first 강제 — 해당 레이어의 Contracts 없으면 먼저 생성 요구 |
| 참조 | `_shared/arix-rules.md` §2, §3 |

### `/arch-check` — 레이어 경계 위반 탐지

| 항목 | 내용 |
|------|------|
| 파일 | `skills/arch-check/SKILL.md` |
| 용도 | `using` 문과 `<ProjectReference>` 분석으로 레이어 간 참조 규칙 위반 탐지 |
| 입력 | 없음 (전체 `src/` 스캔) |
| 출력 | CRITICAL/WARNING/INFO 분류된 위반 보고서 |
| 검사 항목 | 절대 금지 참조, 교차 레이어 허용 검증, Contracts-through, Gateway 우회, 배포 직접 실행, Local Runtime 경계 |
| 참조 | `_shared/arix-rules.md` §1, §3, §9 |

---

## 보조 스킬 (Phase 2) — 구현 완료

### `/impl-review` — 설계 적합성 리뷰

| 항목 | 내용 |
|------|------|
| 파일 | `skills/impl-review/SKILL.md` |
| 용도 | 구현 코드를 설계 문서 §참조와 대조하여 적합성 리뷰 |
| 입력 | 프로젝트명, 파일 경로, 또는 없음(최근 git diff) |
| 검증 항목 | 컴포넌트 책임 경계, 인터페이스 계약, State Schema 준수, Step Type 준수, Action Class 분류 |
| 참조 | `_shared/arix-rules.md` §5, §6, §7, §10 |

### `/track` — 로드맵 Phase 진행률 추적

| 항목 | 내용 |
|------|------|
| 파일 | `skills/track/SKILL.md` |
| 용도 | git log + 소스 구조로 Phase별 Exit Criteria 충족 여부 산출 |
| 입력 | 없음 |
| 출력 | Phase별 진행률 바, Exit Criteria 상태 테이블, 블로커 식별 |
| 참조 | `_shared/arix-rules.md` §13, `docs/architecture-v3.md` §14 |

### `/integration-map` — 교차 레이어 변경 영향 분석

| 항목 | 내용 |
|------|------|
| 파일 | `skills/integration-map/SKILL.md` |
| 용도 | 특정 모듈 변경이 다른 레이어에 미치는 영향 경로 분석 |
| 입력 | 프로젝트명 또는 파일 경로 |
| 출력 | 직접 영향, 교차 레이어 영향, 영향 경로 그래프, 권장 테스트 범위 |
| 참조 | `_shared/arix-rules.md` §1, §3 |

### `/contract-first` — Contracts 우선 개발 강제

| 항목 | 내용 |
|------|------|
| 파일 | `skills/contract-first/SKILL.md` |
| 용도 | 구현 프로젝트 작업 전 해당 레이어의 Contracts 존재 및 인터페이스 정의 확인 |
| 입력 | 프로젝트명 또는 없음(최근 git diff) |
| 출력 | 진행 가능/차단 판정, 미정의 인터페이스 목록 |
| 참조 | `_shared/arix-rules.md` §2 |

### `/adr` — Architecture Decision Record 자동 생성

| 항목 | 내용 |
|------|------|
| 파일 | `skills/adr/SKILL.md` |
| 용도 | 설계 결정에 대한 ADR 문서를 표준 포맷으로 생성 |
| 입력 | 결정 주제 (예: "왜 Control Plane을 .NET으로 가는가") |
| 출력 | `docs/adr/ADR-{번호}-{slug}.md` |
| 포맷 | 컨텍스트, 결정, 근거, 고려 대안, 결과, 관련 문서 |

---

## 에이전트

### `arch-reviewer` — 아키텍처 적합성 심층 분석

| 항목 | 내용 |
|------|------|
| 파일 | `agents/arch-reviewer.md` |
| 유형 | 서브에이전트 (Read, Grep, Glob, Bash) |
| 용도 | arch-check + impl-review 결과 종합, 설계 적합성 점수 산출, 수정 방안 제시 |
| 점수 체계 | 5개 영역 가중 평균 → A/B/C/D 등급 |
| 제약 | 분석/보고만 수행, 코드 직접 수정 불가 |

---

## 훅

### `hooks/hooks.json` — PreToolUse 레이어 표시

| 항목 | 내용 |
|------|------|
| 트리거 | Write 또는 Edit 도구 사용 시 |
| 조건 | 대상 파일이 `.cs` 또는 `.csproj` |
| 동작 | 해당 프로젝트의 레이어 (L2~L6) 표시 + `_shared/arix-rules.md §3` 참조 안내 |
| 결과 | `continue` (차단하지 않음, 정보 제공만) |

---

## 공유 참조

### `_shared/arix-rules.md` — 강제 규칙 통합 참조

설계 문서 4개에서 추출한 14개 섹션:

1. 6-Layer 허용 호출 경로 매트릭스
2. 프로젝트→레이어 매핑 테이블 (28개 프로젝트)
3. 레이어 간 허용 프로젝트 참조 규칙 (허용/금지 방향)
4. 기술 스택 필수/금지 테이블
5. 14영역 State Schema
6. 8 Workflow Step Types + Phase
7. 4 Action Class 분류
8. Source Authority 등급 (A1–A4)
9. 절대 금지 패턴 목록 (9개)
10. 4자 역할 분담표
11. Workflow 상태 모델
12. Eval 적용 위치 (5곳)
13. 로드맵 Phase 요약
14. 구현 우선순위
