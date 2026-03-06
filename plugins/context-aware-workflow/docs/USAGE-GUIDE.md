# CW 플러그인 효율적 사용 가이드

Context-Aware Workflow (CW) v2.1.0 플러그인의 기능을 효율적으로 조합하여 사용하는 방법을 안내합니다.

---

## 목차

1. [핵심 워크플로우 패턴](#핵심-워크플로우-패턴)
2. [실행 모드](#실행-모드)
3. [효율적인 기능 조합](#효율적인-기능-조합)
4. [모델 티어링 전략](#모델-티어링-전략)
5. [학습 및 지속성 활용](#학습-및-지속성-활용)
6. [컨텍스트 관리](#컨텍스트-관리)
7. [추천 워크플로우 시나리오](#추천-워크플로우-시나리오)
8. [핵심 팁](#핵심-팁)

---

## 핵심 워크플로우 패턴

### 1. 완전 자동화 (`/cw:auto`)

가장 포괄적인 단일 명령어로 8단계 파이프라인을 실행합니다:

```
Expansion → Init → Planning → Execution → QA → Review → Fix → Check
```

**사용 시나리오**: 새 기능 구현, 명확한 요구사항이 있을 때

```bash
/cw:auto "JWT 인증 시스템 구현"
/cw:auto "대규모 리팩토링"
```

### 2. 수동 단계별 실행 (`/cw:start` + `/cw:next`)

세밀한 제어가 필요할 때 사용합니다:

```bash
/cw:start "복잡한 리팩토링"  # Planner가 task_plan.md 생성
/cw:next                      # 다음 단계 실행
/cw:next --step 2.1           # 특정 단계 실행
/cw:next --parallel           # 병렬 실행 가능한 단계들 동시 실행
```

---

## 실행 모드

v2.1에서 추가된 다양한 실행 모드를 활용할 수 있습니다.

### Pipeline 모드 (`/cw:pipeline`)

정의된 순서로 단계를 실행하며, 체크포인트와 게이트를 지원합니다.

```bash
/cw:pipeline --stages "plan,build,review,deploy"   # 인라인 지정
/cw:pipeline --config pipeline.yaml                # YAML 설정 파일
/cw:pipeline --resume                              # 중단 지점 재개
/cw:pipeline --from build --to review              # 구간 실행
```

---

## 효율적인 기능 조합

### 조합 1: 연구 → 설계 → 구현

불확실한 요구사항이나 새로운 도메인에서 작업할 때:

```bash
/cw:research "기존 인증 패턴 분석"     # 코드베이스 + 외부 문서 연구
/cw:brainstorm                         # 요구사항 명확화 (Socratic dialogue)
/cw:design                             # UX/아키텍처 설계 문서 생성
/cw:auto "설계 기반 구현"              # 전체 워크플로우 실행
```

### 조합 2: 빠른 구현 + 품질 검증

간단한 작업을 빠르게 처리할 때:

```bash
/cw:start "간단한 버그 수정" --haiku   # Haiku로 빠른 계획
/cw:next                               # 단계별 실행
/cw:ultraqa                            # 지능형 QA (build/test/lint 자동 진단)
```

### 조합 3: QA 집중 워크플로우

코드 품질에 집중할 때:

```bash
/cw:qaloop --max-cycles 5 --severity major   # Review-Fix 반복
/cw:review --opus                            # Opus로 심층 리뷰
/cw:fix --deep                               # 깊은 문제 해결
/cw:check                                    # CLAUDE.md 규칙 준수 검증
/cw:tidy                                     # Kent Beck Tidy First 분석
```

### 조합 4: Pipeline 기반 단계 실행

명시적 단계와 게이트가 필요할 때:

```bash
/cw:pipeline --stages "plan,build,review"       # 기본 파이프라인
/cw:pipeline --config pipeline.yaml --eco       # YAML 설정 + Eco 모드
/cw:pipeline --resume                           # 중단 지점에서 재개
```

---

## 모델 티어링 전략

CW 플러그인은 작업 복잡도에 따라 3가지 모델 티어를 제공합니다:

| 복잡도 | 플래그 | 모델 | 용도 |
|--------|--------|------|------|
| ≤0.3 | `--haiku` | Claude Haiku | 보일러플레이트, 간단한 수정, 빠른 작업 |
| 0.3-0.7 | (기본값) | Claude Sonnet | 표준 TDD, 일반 기능 구현 |
| >0.7 | `--opus` | Claude Opus | 아키텍처 결정, 보안, 복잡한 리팩토링 |

**사용 예시**:

```bash
/cw:start "config 파일 추가" --haiku      # 간단한 작업은 Haiku로
/cw:review --opus                          # 복잡한 코드는 Opus로 심층 리뷰
/cw:next --sonnet                          # 표준 복잡도는 Sonnet으로
```

---

## 학습 및 지속성 활용

### 인사이트 캡처

코드 작성 중 학습한 내용을 `★ Insight:` 블록으로 저장할 수 있습니다:

```markdown
★ Insight: 이 프로젝트는 모든 API 호출에 retry 로직을 사용한다
```

→ `.caw/insights/`에 자동 저장됨

### 고신뢰도 패턴 진화

반복되는 패턴을 재사용 가능한 컴포넌트로 변환합니다:

```bash
/cw:evolve  # 반복 패턴을 명령어/스킬/에이전트로 변환
```

### 세션 간 지속성

```bash
/cw:sync    # Serena 메모리와 양방향 동기화
```

다음 세션에서 이전 학습이 자동으로 로드됩니다.

---

## 컨텍스트 관리

효율적인 컨텍스트 관리로 토큰 사용을 최적화합니다:

```bash
/cw:context add src/auth/**/*.ts    # 관련 파일 추가
/cw:context remove src/legacy/      # 불필요한 파일 제거
/cw:context pack                    # 긴 세션에서 컨텍스트 압축
/cw:context view                    # 현재 컨텍스트 확인
```

**컨텍스트 유형**:
- **Active Context**: 현재 수정 중인 파일
- **Project Context**: 읽기 전용 참조 파일
- **Packed Context**: 압축된 시그니처 (긴 세션용)
- **Pruned Context**: 아카이브/제거된 파일

---

## 추천 워크플로우 시나리오

| 시나리오 | 추천 조합 |
|----------|----------|
| 새 기능 (명확한 요구사항) | `/cw:auto` |
| 새 기능 (불명확한 요구사항) | `/cw:brainstorm` → `/cw:design` → `/cw:auto` |
| 버그 수정 | `/cw:start --haiku` → `/cw:next` → `/cw:ultraqa` |
| 대규모 리팩토링 | `/cw:start --opus` → `/cw:next` → `/cw:tidy` |
| 순차 파이프라인 | `/cw:pipeline --stages "plan,build,review"` |
| 코드 리뷰 집중 | `/cw:review --opus` → `/cw:fix --deep` → `/cw:check` |
| QA 반복 검증 | `/cw:qaloop --max-cycles 5` → `/cw:tidy` |
| 학습 및 개선 | `/cw:evolve` → `/cw:sync` |
| 빠른 프로토타이핑 | `/cw:start --haiku` → `/cw:next` → `/cw:ultraqa` |
| 보안 중심 개발 | `/cw:auto` → `/cw:review --opus` (보안 집중) |

---

## 핵심 팁

### 1. 항상 상태 확인
```bash
/cw:status  # 현재 Phase, Step, 진행률 시각화
```

### 2. QA 플래그 활용
```bash
/cw:qaloop --severity major  # major 이상만 수정
```

### 3. Hooks 자동 작동
- `Edit`/`Write` 시 → Gemini 리뷰 자동 실행
- 커밋 시 → Tidy First 검증 자동 실행
- `TaskCompleted` → 품질 게이트 검증

### 4. 실패 시 상태 보존
- `auto-state.json`, `pipeline_state.json`에서 재개 가능
- `/cw:status`로 중단 지점 확인

### 5. 분석 확인
```bash
/cw:analytics  # 토큰 사용량, 비용, 최적화 인사이트
```

### 6. 초기화 옵션
```bash
/cw:init --with-guidelines  # 프로젝트별 가이드라인 생성
/cw:init --deep             # 계층적 AGENTS.md 문서 생성
```

---

## 명령어 빠른 참조

| 명령어 | 설명 |
|--------|------|
| `/cw:auto` | 전체 8단계 자동화 |
| `/cw:start` | 워크플로우 시작 (계획 생성) |
| `/cw:next` | 다음 단계 실행 |
| `/cw:status` | 현재 상태 확인 |
| `/cw:pipeline` | 순차 파이프라인 실행 |
| `/cw:review` | 코드 리뷰 |
| `/cw:qaloop` | Review-Fix 반복 QA |
| `/cw:ultraqa` | 지능형 QA (자동 진단) |
| `/cw:fix` | 리뷰 문제 수정 |
| `/cw:check` | 규칙 준수 검증 |
| `/cw:tidy` | Tidy First 분석 |
| `/cw:research` | 통합 연구 |
| `/cw:brainstorm` | 요구사항 발견 |
| `/cw:design` | 설계 문서 생성 |
| `/cw:context` | 컨텍스트 관리 |
| `/cw:evolve` | 패턴 진화 |
| `/cw:sync` | Serena 동기화 |
| `/cw:analytics` | 분석 대시보드 |

---

## 관련 문서

- [AGENTS.md](../AGENTS.md) - 에이전트 상세 문서
- [README.md](../README.md) - 플러그인 개요
