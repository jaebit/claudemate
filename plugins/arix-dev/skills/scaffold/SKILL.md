---
name: scaffold
description: >
  This skill should be used when the user asks "프로젝트 생성해줘", "스캐폴딩 해줘", "scaffold",
  "모듈 만들어줘", "Arix.Execution.Workflow 생성", or wants to create a new .NET project following
  the repo-design and 6-layer architecture rules. Creates project structure, .csproj with correct
  references, test project, and registers in solution.
argument-hint: "<module-name> e.g. Arix.Execution.Workflow"
user_invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# /scaffold — 설계서 기반 모듈 스캐폴딩

사용자가 모듈명(예: `Arix.Execution.Workflow`)을 지정하면, `docs/repo-design-v1.md`와 `_shared/arix-rules.md`에 따라 프로젝트 구조를 생성한다.

## 사용법

```
/scaffold Arix.Execution.Workflow
```

## 참조

이 스킬을 실행하기 전에 반드시 `_shared/arix-rules.md`를 읽어 규칙 전체를 파악한다.

## 절차

### Step 1: 모듈 검증

1. 사용자가 지정한 모듈명이 `_shared/arix-rules.md` §2 프로젝트→레이어 매핑 테이블에 존재하는지 확인
2. 존재하지 않으면 사용자에게 확인: "설계 문서에 정의되지 않은 프로젝트입니다. 계속하시겠습니까?"
3. 해당 모듈이 속한 레이어를 식별 (예: `Arix.Execution.*` → L3)

### Step 2: Contracts 우선 확인

해당 레이어의 Contracts 프로젝트가 존재하는지 확인한다.

예: `Arix.Execution.Workflow`를 스캐폴딩하려면 `Arix.Execution.Contracts`가 먼저 존재해야 한다.

- Contracts가 없으면: "Contracts 프로젝트가 먼저 필요합니다. `Arix.Execution.Contracts`를 먼저 생성하시겠습니까?"
- 사용자가 동의하면 Contracts를 먼저 생성한 후 원래 모듈 생성 진행

### Step 3: 프로젝트 구조 생성

모듈 유형에 따라 생성할 구조가 다르다:

#### Contracts 프로젝트 (`*.Contracts`)

```
src/{모듈명}/
├── {모듈명}.csproj
├── Interfaces/
└── Models/
```

`.csproj` 내용:
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
```

Contracts 프로젝트는 `Arix.BuildingBlocks.Contracts` 참조만 허용.

#### API 프로젝트 (`*.Api`)

```
src/{모듈명}/
├── {모듈명}.csproj
├── Endpoints/
├── Middleware/
└── Program.cs (Hosts 프로젝트가 아닌 경우 생략)
```

#### Application/Domain/Infrastructure 프로젝트

```
src/{모듈명}/
├── {모듈명}.csproj
└── (빈 — 내부 구조는 구현 시 추가)
```

#### 일반 실행 컴포넌트 (AppRuntime, Workflow, Eval 등)

```
src/{모듈명}/
├── {모듈명}.csproj
├── Abstractions/
└── Services/
```

### Step 4: 프로젝트 참조 설정

`_shared/arix-rules.md` §3 레이어 간 허용 프로젝트 참조 규칙에 따라 `.csproj`에 `<ProjectReference>`를 추가한다.

필수 참조:
- 자기 레이어의 Contracts 프로젝트
- `Arix.BuildingBlocks.Core` (Contracts 제외)

교차 레이어 참조가 필요한 경우 (`_shared/arix-rules.md` §3.2 참조):
- `Arix.Execution.*` → `Arix.Registry.Contracts`, `Arix.Gateway.Contracts`, `Arix.Governance.Contracts` 허용

### Step 5: 테스트 프로젝트 생성

```
tests/{모듈명}.Tests.Unit/
├── {모듈명}.Tests.Unit.csproj
└── (빈)
```

테스트 `.csproj`에는 대상 프로젝트 참조 + xUnit 패키지 참조 추가.

### Step 6: 솔루션 등록

```bash
dotnet sln Arix.Platform.sln add src/{모듈명}/{모듈명}.csproj
dotnet sln Arix.Platform.sln add tests/{모듈명}.Tests.Unit/{모듈명}.Tests.Unit.csproj
```

솔루션 파일이 없으면 먼저 생성한다:
```bash
dotnet new sln -n Arix.Platform
```

### Step 7: 결과 보고

```
## Scaffold 완료

### 생성된 프로젝트
- src/Arix.Execution.Workflow/Arix.Execution.Workflow.csproj
- tests/Arix.Execution.Workflow.Tests.Unit/...

### 프로젝트 참조
- → Arix.Execution.Contracts
- → Arix.BuildingBlocks.Core
- → Arix.Registry.Contracts (교차 레이어)

### 레이어: L3 Execution
### 금지 참조 확인: ✅ 위반 없음
```

## 주의사항

- **Contracts-first 원칙**: 해당 레이어의 Contracts가 없으면 다른 프로젝트를 생성하지 않는다
- **설계 문서 외 프로젝트**: 사용자 확인 후에만 생성. 생성 시 경고 메시지 포함
- **Hosts 프로젝트**: `Arix.Hosts.*`는 별도 패턴 — `Program.cs` + DI 설정 포함
- `net9.0` 타겟 프레임워크 사용 (프로젝트에 맞게 조정)
