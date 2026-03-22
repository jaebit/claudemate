# CW 플러그인 사용 가이드

Context-Aware Workflow (CW) v3.0 플러그인 사용법을 안내합니다.

---

## 목차

1. [핵심 워크플로우](#핵심-워크플로우)
2. [명령어 참조](#명령어-참조)
3. [실행 패턴](#실행-패턴)
4. [품질 보증](#품질-보증)
5. [병렬 실행](#병렬-실행)
6. [유틸리티](#유틸리티)
7. [Hooks 자동 동작](#hooks-자동-동작)
8. [추천 시나리오](#추천-시나리오)

---

## 핵심 워크플로우

### `/crew:go` — 자동화 실행

가장 포괄적인 명령어로 9단계 파이프라인을 실행합니다:

```
Expansion → Init → Planning → Execution → QA → Review → Fix → Check → Reflect
```

```bash
/crew:go "JWT 인증 시스템 구현"                  # 기본 실행
/crew:go --team --team-size 3                    # Agent Teams 병렬 실행
/crew:go --continue                              # 중단된 작업 재개
/crew:go --max-iterations 5                      # 반복 횟수 제한
/crew:go --from-plan                             # 기존 Plan Mode 출력에서 시작
/crew:go --skip-review                           # 리뷰 단계 생략
```

**Plan 자동 감지**: Plan Mode 출력(`.claude/plans/*.md`)이 있으면 자동으로 사용합니다.
Plan이 없고 task description이 있으면 자동으로 계획을 생성합니다.

---

## 명령어 참조

| 명령어 | 설명 |
|--------|------|
| `/crew:go` | 전체 9단계 자동화 파이프라인 |
| `/crew:dashboard` | 진행 상태 + 비용/토큰 분석 |
| `/crew:review` | 통합 QA (리뷰, 빌드 검증, 규칙 준수, 수정) |
| `/crew:parallel` | 병렬 실행 (Swarm 기본, `--team` Agent Teams) |
| `/crew:explore` | 탐색/발견 (브레인스토밍, 설계, 연구) |
| `/crew:manage` | 유틸리티 (context, sync, merge, worktree, tidy, init, evolve, reflect) |

---

## 실행 패턴

### 패턴 1: 완전 자동화

명확한 요구사항이 있을 때:

```bash
/crew:go "새 API 엔드포인트 추가"
```

### 패턴 2: 탐색 → 실행

요구사항이 불명확할 때:

```bash
/crew:explore --research "기존 인증 패턴 분석"
/crew:explore "요구사항 정리"                    # 브레인스토밍
/crew:explore --ui                               # UI/UX 설계
/crew:go "설계 기반 구현"
```

### 패턴 3: 팀 기반 대규모 개발

```bash
/crew:go "대규모 인증 시스템" --team --team-size 3
```

또는 수동 제어:

```bash
/crew:parallel --team create auth --size 3
/crew:parallel --team assign --from-plan
/crew:parallel --team status
/crew:parallel --team gate
/crew:parallel --team synthesize
/crew:parallel --team cleanup
```

### 패턴 4: 독립 작업 병렬 처리

```bash
/crew:parallel "로그인 API" "로그아웃 버튼" "인증 리뷰"
/crew:parallel --workers 4 "taskA" "taskB"
/crew:parallel --worktrees "feature-A" "feature-B"
```

---

## 품질 보증

### `/crew:review` 플래그

```bash
/crew:review                    # 기본 코드 리뷰
/crew:review --loop             # Review-Fix 반복 (구 /crew:qaloop)
/crew:review --build            # 빌드+테스트 자동 진단 (구 /crew:ultraqa)
/crew:review --compliance       # CLAUDE.md 규칙 준수 (구 /crew:check)
/crew:review --fix              # 발견된 문제 자동 수정 (구 /crew:fix)
/crew:review --gemini           # Cross-model Gemini 리뷰
/crew:review --all              # 모든 QA 단계 실행
```

### QA 집중 워크플로우

```bash
/crew:review --loop --max-cycles 5    # 최대 5회 Review-Fix 반복
/crew:review --all                     # 전체 QA 파이프라인
/crew:manage tidy                      # Kent Beck Tidy First 분석
```

---

## 병렬 실행

### Swarm vs Agent Teams

| 측면 | Swarm (기본) | Agent Teams (`--team`) |
|------|-------------|------------------------|
| 메커니즘 | Task 서브에이전트 | 다중 세션 |
| 에이전트 간 통신 | 결과 보고만 | `SendMessage` 직접 메시징 |
| 격리 | 선택 (`--worktrees`) | 자동 worktree 격리 |
| 비용 | 낮음 | 높음 |
| 적합 대상 | 독립적 단순 작업 | 협업 필요한 복잡한 작업 |

---

## 유틸리티

`/crew:manage` 서브커맨드:

```bash
/crew:manage context add src/auth/**/*.ts    # 컨텍스트 파일 추가
/crew:manage context remove src/legacy/      # 컨텍스트 파일 제거
/crew:manage context pack                    # 컨텍스트 압축
/crew:manage sync                            # 메모리 동기화
/crew:manage merge                           # Worktree 결과 병합
/crew:manage worktree create phase 2,3       # Worktree 생성
/crew:manage worktree clean                  # Worktree 정리
/crew:manage tidy                            # Tidy First 분석
/crew:manage init --with-guidelines          # 프로젝트 초기화
/crew:manage evolve                          # 패턴 진화
/crew:manage reflect                         # Ralph Loop 개선 사이클
```

---

## Hooks 자동 동작

- `Edit`/`Write` 시 → Plan adherence 확인 + Gemini 리뷰 (설치 시)
- 커밋 시 → Tidy First 검증 + Gemini 커밋 리뷰 (설치 시)
- `WorktreeCreate` → `.caw/` 파일 자동 복사
- `TeammateIdle` → 다음 태스크 자동 배정
- `TaskCompleted` → 품질 게이트 검증

---

## 추천 시나리오

| 시나리오 | 추천 |
|----------|------|
| 새 기능 (명확한 요구사항) | `/crew:go` |
| 새 기능 (불명확) | `/crew:explore` → `/crew:go` |
| 버그 수정 | `/crew:go "fix: ..."` |
| 대규모 리팩토링 | `/crew:go --team` |
| 독립 작업 병렬 | `/crew:parallel "t1" "t2" "t3"` |
| 코드 리뷰 집중 | `/crew:review --all` |
| QA 반복 | `/crew:review --loop` |
| 학습 및 개선 | `/crew:manage reflect` → `/crew:manage evolve` |

---

## 관련 문서

- [MIGRATION-v2-to-v3.md](./MIGRATION-v2-to-v3.md) — v2 → v3 마이그레이션 가이드
- [README.md](../README.md) — 플러그인 개요
