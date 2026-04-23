# CLAUDE.md — arch-guard

## 목적 (Purpose)

arch-guard는 레이어드 아키텍처 프로젝트의 설계 준수를 강제하는 플러그인입니다. `arch-guard.json` 설정 파일을 단일 진실 원천으로 삼아 레이어 경계 규칙, Contracts-first 개발 원칙, 설계 결정 기록(ADR)을 관리합니다. 버전 0.2.2 기준으로 .NET을 주 대상으로 지원하며, Java, TypeScript, Python 확장 포인트를 갖추고 있습니다.

플러그인은 "절대 차단하지 않는다(never-block)" 원칙을 따릅니다. 모든 훅은 위반 사항을 경고로 전달하되 Claude의 액션을 중단시키지 않습니다. 강제 실행이 아닌 지속적인 컨텍스트 주입으로 설계 준수를 유도합니다.

---

## 스킬 카테고리 (Skills)

모든 스킬은 `user_invocable: false`로 선언되어 있습니다. Claude가 내부적으로 호출하는 도구이며 사용자가 직접 `/스킬명`으로 실행하는 것이 아닙니다.

### 설계 및 기록 (Design & Documentation)

| 스킬 | 목적 |
|------|------|
| `setup` | codebase를 분석해 `arch-guard.json` 초기 설정 파일을 대화형으로 생성 |
| `adr` | 설계 결정을 맥락·근거·대안·결과 포함 ADR 문서로 기록 |
| `contract-first` | 구현 전 해당 레이어의 Contracts 프로젝트와 인터페이스 존재 여부 검증 |

### 스캐폴딩 (Scaffolding)

| 스킬 | 목적 |
|------|------|
| `scaffold` | `arch-guard.json` 규칙에 따라 신규 모듈/프로젝트 구조 생성 |

### 구현 지원 (Implementation)

| 스킬 | 목적 |
|------|------|
| `implement` | Contracts 인터페이스로부터 구현 클래스 및 단위 테스트 스텁 생성 |
| `tdd` | RED-GREEN-REFACTOR + Tidy First 커밋 규율로 아키텍처 인식 TDD 가이드 제공 |
| `test-gen` | `arch-guard.json` 레이어 규칙을 xUnit 아키텍처 가드레일 테스트로 코드화 |

### 검토 및 분석 (Review & Analysis)

| 스킬 | 목적 |
|------|------|
| `arch-check` | 소스 참조를 파싱해 레이어 경계 위반을 정적 스캔 |
| `impl-review` | 구현 코드를 아키텍처 문서 대비 책임 경계·인터페이스 준수 관점으로 리뷰 |
| `integration-map` | 모듈 변경이 프로젝트 참조 그래프를 통해 전파되는 영향 범위 추적 |

### 진행 추적 (Tracking)

| 스킬 | 목적 |
|------|------|
| `spec-sync` | 설계 문서 컴포넌트가 소스 트리에 실제로 존재하는지 구조적 체크리스트 생성 |
| `track` | 페이즈 기반 진행률(%) 및 완료 기준 충족율 보고 |

---

## 훅 동작 조건 (Hook Activation)

훅은 `hooks.json`에 등록되어 있으며, 세 가지 이벤트에 바인딩됩니다.

### 범위 가드 (Scope Guard)

`session-init.mjs`를 제외한 모든 훅은 `loadConfig(cwd)`를 통해 `arch-guard.json` 존재 여부를 확인합니다. `stop-reminder.mjs`는 `isConfiguredProject(cwd)` 함수를 직접 호출합니다. 두 방법 모두 현재 디렉토리에서 최대 4단계 상위 디렉토리까지 `arch-guard.json`을 탐색하며, 발견되지 않으면 즉시 `process.exit(0)`으로 조용히 종료합니다.

이 설계는 arch-guard가 설정되지 않은 프로젝트에서 훅이 전역적으로 개입하는 것을 방지합니다 (과거 S533 회귀 원인이었던 전역 간섭 문제 해결).

### 훅 목록

| 훅 이름 | 이벤트 | 스크립트 | 동작 |
|---------|--------|----------|------|
| `session-init` | `SessionStart` | `hooks/session-init.mjs` | `arch-guard.json`을 읽어 레이어 규칙·금지 참조·Contracts 설정 요약을 `additionalContext`로 세션에 주입 |
| `layer-check` | `PreToolUse` (Write\|Edit) | `hooks/layer-check.mjs` | 작성 중인 파일의 레이어를 식별하고 내용에서 금지된 레이어 간 참조를 실시간 감지해 경고 메시지 반환 |
| `contract-guard` | `PreToolUse` (Write only) | `hooks/contract-guard.mjs` | 신규 소스 파일 생성 시 해당 레이어의 Contracts 프로젝트가 존재하는지 확인, 없으면 `/scaffold` 실행 권고 |
| `stop-reminder` | `Stop` | `hooks/stop-reminder.mjs` | 소스 파일(.cs, .java, .py, .ts 등) 수정 후 세션 종료 시 `/arch-check` 또는 `/contract-first` 실행 권고 메시지 출력 (exit 2로 Claude에 전달) |

---

## Golden Rules

### 1. plugin.json 엄격 스키마 (claudemate 전역 규칙)

`plugin.json`에는 `name`, `version`, `description`, `mcpServers` 네 필드만 허용됩니다. `author`, `features`, `commands`, `agents`, `skills`, `hooks` 필드 추가 시 유효성 검사 실패가 발생합니다.

### 2. 모든 스킬은 `user_invocable: false`

arch-guard의 12개 스킬은 모두 내부 도구입니다. 사용자가 직접 스킬 이름으로 호출하는 것이 아니라, Claude가 컨텍스트에 따라 자동 활성화합니다. SKILL.md에 `user_invocable: false` 선언이 반드시 유지되어야 합니다.

### 3. Stop 훅의 필수 가드 조건

`stop-reminder.mjs`는 반드시 `isConfiguredProject()` 확인을 첫 번째 동작으로 실행해야 합니다. 이 조건 없이 사이드 이펙트(메시지 출력, exit 2)를 발생시키면 arch-guard 미설정 프로젝트에서 전역 간섭이 재발합니다.

### 4. 크로스플랫폼 경로/명령 규칙

- 경로 구분자: `/` 사용 또는 `path.join()` / `os.path.join()` 활용
- 실행 명령: `node` 또는 `python3` 사용 (OS 고유 명령 금지)
- 플러그인 루트 참조: `"${CLAUDE_PLUGIN_ROOT}/path"` 형식 (환경 변수가 아닌 런타임 치환)

### 5. Never-block 원칙

모든 훅은 오류 발생 시에도 `{ result: "continue" }`를 반환하고 종료해야 합니다. `.catch(() => { console.log(JSON.stringify({ result: "continue" })); })` 패턴이 모든 비동기 훅에 적용되어야 합니다.

---

## 관련 문서 (References)

- [프로젝트 루트 CLAUDE.md](../../CLAUDE.md) — claudemate 전역 규칙 및 Golden Rules
- [플러그인 README](./README.md) — arch-guard 간략 소개
- [아키텍처 결정 기록](./docs/architecture-decisions.md) — 설계 변경 이력
