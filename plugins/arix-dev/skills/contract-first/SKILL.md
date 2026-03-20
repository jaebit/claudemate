---
name: contract-first
description: >
  This skill should be used when the user asks "Contracts 먼저 있어?", "구현 시작해도 돼?",
  "contract-first 확인", "인터페이스 정의됐어?", or wants to verify that the layer's Contracts
  project exists and required interfaces are defined before writing implementation code.
  Blocks work if Contracts are missing.
argument-hint: "<project-name> e.g. Arix.Execution.Workflow"
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /contract-first — Contracts 우선 개발 강제

구현 프로젝트에 코드를 작성하기 전에 해당 레이어의 Contracts 프로젝트가 존재하고, 필요한 인터페이스가 정의되어 있는지 확인한다.

## 사용법

```
/contract-first Arix.Execution.Workflow
```

인자 없이 실행하면 최근 변경된 파일(git diff)의 프로젝트를 대상으로 한다.

## 참조

이 스킬을 실행하기 전에 반드시 `_shared/arix-rules.md`를 읽어 규칙 전체를 파악한다.

## 절차

### Step 1: 대상 프로젝트의 레이어 식별

`_shared/arix-rules.md` §2로 대상 프로젝트의 레이어와 해당 Contracts 프로젝트를 식별한다.

| 대상 프로젝트 | 필요한 Contracts |
|---------------|-----------------|
| `Arix.Execution.*` | `Arix.Execution.Contracts` |
| `Arix.Registry.*` | `Arix.Registry.Contracts` |
| `Arix.Gateway.*` | `Arix.Gateway.Contracts` |
| `Arix.Governance.*` | `Arix.Governance.Contracts` |
| `Arix.Knowledge.*` | `Arix.Knowledge.Contracts` |

### Step 2: Contracts 존재 여부 확인

1. Contracts `.csproj` 파일 존재 여부
2. 솔루션 파일에 등록 여부
3. 최소 1개 이상의 인터페이스 또는 모델이 정의되어 있는지

### Step 3: 인터페이스 커버리지 확인

대상 프로젝트가 구현하려는 기능에 필요한 인터페이스가 Contracts에 정의되어 있는지 확인한다.

예: `Arix.Execution.Workflow`가 `IStepExecutor`를 구현하려면 `Arix.Execution.Contracts/Interfaces/IStepExecutor.cs`가 먼저 존재해야 한다.

### Step 4: 결과 보고

```
## Contract-First 점검

### 대상: Arix.Execution.Workflow (L3)
### Contracts: Arix.Execution.Contracts

### 상태: ✅ 진행 가능
- Contracts 프로젝트 존재
- IWorkflowEngine 정의됨
- IStepExecutor 정의됨
- ITransitionResolver 정의됨

### 미정의 인터페이스 (구현 전 정의 필요):
- ⚠️ IStateManager — Workflow에서 사용하지만 Contracts에 미정의
```

또는 차단하는 경우:

```
### 상태: ❌ 차단
- Arix.Execution.Contracts 프로젝트가 존재하지 않습니다.
- 먼저 `/scaffold Arix.Execution.Contracts`를 실행하세요.
```
