---
name: integration-map
description: >
  This skill should be used when the user asks "이거 변경하면 어디 영향 가?", "영향 분석해줘",
  "integration-map", "의존성 맵", "변경 영향 범위", or wants to trace how a module change propagates
  across layers via the project reference graph.
argument-hint: "<module-or-file> e.g. Arix.Execution.Contracts"
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /integration-map — 교차 레이어 변경 영향 분석

특정 모듈의 변경이 다른 레이어에 미치는 영향을 프로젝트 참조 그래프 기반으로 분석한다.

## 사용법

```
/integration-map Arix.Execution.Contracts
/integration-map src/Arix.Gateway.Policy/ActionClassifier.cs
```

## 참조

이 스킬을 실행하기 전에 반드시 `_shared/arix-rules.md`를 읽어 규칙 전체를 파악한다.

## 절차

### Step 1: 대상 모듈 식별

사용자가 지정한 모듈/파일의 레이어와 프로젝트를 `_shared/arix-rules.md` §2로 식별한다.

### Step 2: 역방향 의존성 그래프

변경 대상 프로젝트를 **참조하고 있는** 프로젝트를 모두 찾는다.

```bash
grep -rl 'Arix.Execution.Contracts' src/ --include='*.csproj'
```

이 과정을 재귀적으로 반복하여 영향 범위를 전파한다.

### Step 3: 교차 레이어 경로 식별

`_shared/arix-rules.md` §1 호출 경로 매트릭스를 기준으로, 변경이 다른 레이어로 전파되는 경로를 식별한다.

예: `Arix.Execution.Contracts` 변경 시
- L3 내부: `Arix.Execution.Workflow`, `Arix.Execution.AppRuntime` 등 (직접 영향)
- 교차 레이어: 이 Contracts를 참조하는 L4 프로젝트가 있는지 확인

### Step 4: 영향 보고서

```
## Integration Map: Arix.Execution.Contracts

### 직접 영향 (같은 레이어)
- Arix.Execution.Workflow (L3)
- Arix.Execution.AppRuntime (L3)
- Arix.Execution.Eval (L3)
- Arix.Execution.StateStore (L3)
- Arix.Execution.Approval (L3)
- Arix.Execution.Release (L3)

### 교차 레이어 영향
- (없음 — 이 Contracts는 L3 내부에서만 참조됨)

### 영향 경로
L3.Contracts → L3.Workflow → L3.AppRuntime
                           → L3.Eval

### 권장 테스트 범위
- Arix.Execution.Tests.Unit/
- Arix.Execution.Tests.Integration/
- Arix.Architecture.Tests/ (참조 방향 재검증)
```
