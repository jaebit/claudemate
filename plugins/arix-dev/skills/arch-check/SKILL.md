---
name: arch-check
description: >
  This skill should be used when the user asks "아키텍처 검사해줘", "레이어 위반 확인",
  "arch-check", "참조 규칙 위반 있어?", "교차 레이어 참조 검증", or wants to detect layer boundary
  violations by analyzing using statements and ProjectReference entries against arix-rules.
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /arch-check — 레이어 경계 위반 탐지

`using` 문과 `.csproj` 프로젝트 참조를 분석하여 `_shared/arix-rules.md`의 레이어 간 참조 규칙 위반을 탐지한다.

## 참조

이 스킬을 실행하기 전에 반드시 `_shared/arix-rules.md`를 읽어 규칙 전체를 파악한다.

## 절차

### Step 1: 프로젝트 매핑 수집

`src/` 아래의 모든 `.csproj` 파일을 찾아 프로젝트 목록을 구성한다.

각 프로젝트에 대해:
1. 프로젝트명에서 레이어를 식별 (`_shared/arix-rules.md` §2 참조)
2. 프로젝트 유형을 식별 (Contracts, Domain, Application, Infrastructure, Api, Hosts)

### Step 2: ProjectReference 분석

각 `.csproj` 파일에서 `<ProjectReference>` 항목을 추출한다.

```bash
grep -r '<ProjectReference' src/ --include='*.csproj'
```

각 참조에 대해 `_shared/arix-rules.md` §3의 규칙을 적용:

#### 체크 2-A: 절대 금지 참조

다음 패턴을 탐지하면 **CRITICAL** 위반:
- Infrastructure 프로젝트 → Domain 프로젝트 참조
- L6 프로젝트 → L3 프로젝트 참조
- L4 프로젝트 → L3 프로젝트 참조
- L5 프로젝트 → L3 프로젝트 참조
- 어떤 프로젝트 → Hosts 프로젝트 참조
- Contracts 프로젝트 → Application/Infrastructure 프로젝트 참조

#### 체크 2-B: 교차 레이어 참조 검증

교차 레이어 참조가 `_shared/arix-rules.md` §3.2 허용 목록에 있는지 확인:
- `Arix.Execution.*` → `Arix.Registry.Contracts` ✅
- `Arix.Execution.*` → `Arix.Registry.Application` ❌ (Contracts만 허용)

#### 체크 2-C: Contracts-through 원칙

교차 레이어 참조는 반드시 상대 레이어의 **Contracts 프로젝트**만 참조해야 한다. Application, Domain, Infrastructure를 직접 참조하면 위반.

### Step 3: using 문 분석

`src/` 아래의 모든 `.cs` 파일에서 `using` 문을 추출한다.

```bash
grep -rn '^using Arix\.' src/ --include='*.cs'
```

각 `using` 문의 네임스페이스를 프로젝트에 매핑하여 Step 2와 동일한 규칙을 적용한다.

예:
- `src/Arix.Gateway.Routing/` 안에서 `using Arix.Execution.Workflow;` → **CRITICAL** (L4→L3 참조)
- `src/Arix.Execution.Workflow/` 안에서 `using Arix.Registry.Contracts;` → **OK** (허용된 교차 레이어)

### Step 4: 금지 패턴 검사

`_shared/arix-rules.md` §9 절대 금지 패턴에 기반한 추가 검사:

#### 체크 4-A: Gateway 우회

L3 Execution 프로젝트에서 L6 Knowledge/Capability 프로젝트를 직접 참조하는지 탐지.

#### 체크 4-B: 배포 직접 실행

App 코드에서 배포 명령을 직접 실행하는 패턴 탐지:
```bash
grep -rn 'Process.Start\|ShellExecute\|kubectl\|docker push\|helm' src/ --include='*.cs'
```
이런 패턴이 `Arix.Execution.Release` 외부에 존재하면 경고.

#### 체크 4-C: Local Runtime 경계 위반

`Arix.Execution.AppRuntime` 내에서 `ApprovalStep`이나 `ReleaseStep`을 직접 실행하는 코드가 있는지 탐지.

### Step 5: 위반 보고서 출력

```
## Arch-Check 보고서

### CRITICAL 위반 (즉시 수정 필요)
1. ❌ Arix.Gateway.Routing → Arix.Execution.Workflow (L4→L3 금지)
   파일: src/Arix.Gateway.Routing/Arix.Gateway.Routing.csproj:12
   규칙: §3.3 절대 금지 참조

2. ❌ Arix.Knowledge.Search 내에서 using Arix.Execution.StateStore
   파일: src/Arix.Knowledge.Search/Services/Searcher.cs:3
   규칙: §3.3 L6→L3 참조 금지

### WARNING (검토 필요)
1. ⚠️ Arix.Execution.Workflow → Arix.Knowledge.Contracts
   파일: src/Arix.Execution.Workflow/Arix.Execution.Workflow.csproj:15
   규칙: §3.2에 명시되지 않은 교차 레이어 참조

### INFO
1. ℹ️ 총 프로젝트: 18개
2. ℹ️ 총 ProjectReference: 45개
3. ℹ️ 교차 레이어 참조: 8개 (허용 7개, 위반 1개)

### 금지 패턴
- Gateway 우회: 0건
- 배포 직접 실행: 0건
- Local Runtime 경계 위반: 0건

### 요약
- CRITICAL: 2건
- WARNING: 1건
- 위반율: 2/45 참조 (4.4%)
```

## Severity 기준

| Severity | 조건 | 조치 |
|----------|------|------|
| CRITICAL | §3.3 절대 금지 참조, §9 금지 패턴 | 즉시 수정. PR 머지 차단 |
| WARNING | §3.2에 없는 교차 레이어 참조, 의심 패턴 | 팀 리뷰 후 판단 |
| INFO | 통계, 정상 참조 | 참고용 |
