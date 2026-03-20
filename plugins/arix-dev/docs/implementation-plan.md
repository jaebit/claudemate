# arix-dev Plugin — Implementation Plan

## Context

arix-ai는 6-Layer 아키텍처의 엔터프라이즈 AI Agent 플랫폼이다. 현재 설계 문서 4개(architecture-v3, tech-stack, repo-design, review)가 완성되어 있고, 구현 단계 진입을 앞두고 있다.

기존 Claude Code 도구들(Superpowers, gstack, CAW, OMC, OMO)은 바이브 코딩에 최적화되어 있어 **설계 문서 기반의 엔터프라이즈 시스템 구현을 강제·검증·추적**하는 도구가 없다. 이 gap을 채우는 Claude Code 플러그인을 `/Volumes/External/projects/arix-ai`에 개발한다.

## Plugin Identity

- **Name**: `arix-dev`
- **Philosophy**: "설계 문서가 코드의 법이다"
- **Target**: arix-ai 프로젝트 전용 (추후 범용화 가능)
- **Repo**: `/Volumes/External/projects/arix-ai`

## Directory Structure

```
/Volumes/External/projects/arix-ai/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── spec-sync/
│   │   └── SKILL.md          # 설계문서 → 구현 체크리스트 생성
│   ├── scaffold/
│   │   └── SKILL.md          # 설계서 기반 .NET 프로젝트 스캐폴딩
│   ├── arch-check/
│   │   └── SKILL.md          # 레이어 경계 위반 탐지
│   ├── impl-review/
│   │   └── SKILL.md          # 설계 적합성 리뷰
│   ├── track/
│   │   └── SKILL.md          # 로드맵 Phase 진행률 추적
│   ├── integration-map/
│   │   └── SKILL.md          # 교차 레이어 변경 영향 분석
│   ├── contract-first/
│   │   └── SKILL.md          # Contracts 프로젝트 우선 개발 강제
│   └── adr/
│       └── SKILL.md          # ADR 자동 생성
├── agents/
│   └── arch-reviewer.md      # 아키텍처 적합성 서브에이전트
├── hooks/
│   └── hooks.json            # PreToolUse: Write/Edit 시 arch-check 경고
├── _shared/
│   └── arix-rules.md         # 6-Layer 규칙, 금지 패턴, 기술 스택 규칙 통합 참조
├── docs/                     # 기존 설계 문서 (이미 존재)
│   ├── architecture-v3.md
│   ├── architecture-v3-review.md
│   ├── repo-design-v1.md
│   └── tech-stack-standard-v1.md
└── README.md                 # (기존 유지, 수정하지 않음)
```

## Implementation Steps

### Step 1: Plugin Foundation
**파일**: `.claude-plugin/plugin.json`

```json
{
  "name": "arix-dev",
  "version": "0.1.0",
  "description": "설계 문서 기반 엔터프라이즈 시스템 개발 도구 — 아키텍처 적합성 검증, 레이어 경계 강제, 계약 우선 개발"
}
```

### Step 2: 공유 규칙 문서 (`_shared/arix-rules.md`)
설계 문서에서 추출한 **강제 가능한 규칙**을 하나의 참조 문서로 통합. 모든 스킬이 이 문서를 참조.

포함 내용:
- 6-Layer 허용 호출 경로 매트릭스
- 프로젝트→레이어 매핑 테이블
- 기술 스택 필수/금지 테이블
- 14영역 State Schema 목록
- 8 Workflow Step Type + Phase
- 4 Action Class 분류 규칙
- Source Authority 등급 (A1-A4)
- 절대 금지 패턴 목록

### Step 3: 핵심 스킬 3개 (Phase 1)

#### 3-A: `/spec-sync` — 설계→체크리스트
- 설계 문서(architecture-v3.md, repo-design-v1.md)를 읽고 파싱
- 현재 소스 디렉토리 구조와 비교
- 구현 상태 체크리스트 생성 (존재/미존재/불일치)
- 로드맵 Phase별 Exit Criteria 매핑

#### 3-B: `/scaffold` — 모듈 스캐폴딩
- 사용자가 모듈명(e.g. "Arix.Execution.Workflow") 지정
- repo-design-v1에 따라 프로젝트 구조 생성 (.csproj, 폴더, 기본 인터페이스)
- 해당 모듈이 속한 레이어의 Contracts 프로젝트 존재 여부 확인 (없으면 먼저 생성 요구)
- 기본 테스트 프로젝트도 함께 생성

#### 3-C: `/arch-check` — 레이어 경계 검증
- `using` 문과 프로젝트 참조(.csproj `<ProjectReference>`)를 분석
- 허용되지 않은 레이어 간 참조 탐지
- 금지 패턴 위반 보고 (Gateway 우회, 직접 배포, 상태 불일치 등)
- Infrastructure → Domain 역참조 탐지

### Step 4: 보조 스킬 (Phase 2)
- `/impl-review`: 구현 코드를 설계 문서 §참조와 대조
- `/track`: git log + 소스 구조로 Phase 진행률 산출
- `/integration-map`: 변경 모듈의 교차 레이어 영향 경로 표시
- `/contract-first`: Contracts 프로젝트 먼저 정의하지 않으면 구현 차단
- `/adr`: 설계 결정에 대한 ADR 문서 자동 생성

### Step 5: 에이전트 (`agents/arch-reviewer.md`)
- 서브에이전트로 아키텍처 적합성 심층 분석
- impl-review, arch-check 결과를 종합하여 설계 적합성 점수 산출
- 위반 사항에 대한 구체적 수정 방안 제시

### Step 6: 훅 (`hooks/hooks.json`)
- `PreToolUse` (Write|Edit): .cs 파일 수정 시 해당 프로젝트가 어느 레이어인지 표시
- `SessionStart`: arix-rules.md 요약 주입

## Execution Order

| # | 산출물 | 의존성 |
|---|--------|--------|
| 1 | `.claude-plugin/plugin.json` | 없음 |
| 2 | `_shared/arix-rules.md` | docs/ 설계 문서 |
| 3 | `skills/spec-sync/SKILL.md` | arix-rules.md |
| 4 | `skills/scaffold/SKILL.md` | arix-rules.md |
| 5 | `skills/arch-check/SKILL.md` | arix-rules.md |
| 6 | `hooks/hooks.json` | 없음 |
| 7 | `agents/arch-reviewer.md` | arch-check, impl-review |
| 8 | 나머지 5개 스킬 | 핵심 3개 완성 후 |

## Key Design Decisions

1. **arix 전용으로 시작** — 규칙이 arix-ai 설계서에 하드코딩됨. 범용화는 규칙을 config로 분리하는 후속 작업.
2. **프롬프트 기반** — Python/JS 훅보다 SKILL.md 프롬프트로 먼저 구현. 프로그래매틱 검증은 arch-check에서만 bash 스크립트 병행.
3. **_shared/arix-rules.md가 single source of truth** — 설계 문서 전체를 매번 읽지 않고, 강제 가능한 규칙만 추출해 놓음.
4. **hooks는 최소** — SessionStart에서 컨텍스트 주입, PreToolUse는 경량 경고만.

## Verification

1. 플러그인 설치: `cd /Volumes/External/projects/arix-ai && ls .claude-plugin/plugin.json`
2. 스킬 목록 확인: Claude Code에서 `/arix-dev:spec-sync` 호출 가능한지 확인
3. spec-sync 실행: 설계 문서 대비 현재 디렉토리 상태 체크리스트 출력되는지 확인
4. scaffold 실행: `Arix.Execution.Contracts` 스캐폴딩 후 올바른 구조 생성되는지 확인
5. arch-check 실행: 의도적 위반 코드에 대해 경고 발생하는지 확인
