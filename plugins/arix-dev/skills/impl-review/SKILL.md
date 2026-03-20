---
name: impl-review
description: >
  This skill should be used when the user asks "구현 리뷰해줘", "설계 적합성 확인", "impl-review",
  "이 코드 설계랑 맞아?", "책임 경계 위반 없어?", or wants to verify implementation code against
  architecture docs — checking component responsibility boundaries, interface contracts, state schema
  compliance, and workflow step type correctness.
argument-hint: "<project-or-file> e.g. Arix.Execution.Workflow or path to .cs file"
user_invocable: true
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# /impl-review — 설계 적합성 리뷰

구현 코드를 설계 문서(architecture-v3, repo-design-v1)와 대조하여 설계 적합성을 리뷰한다.

## 참조

이 스킬을 실행하기 전에 반드시 `_shared/arix-rules.md`를 읽어 규칙 전체를 파악한다.

## 사용법

```
/impl-review Arix.Execution.Workflow
/impl-review src/Arix.Execution.Workflow/Services/StepExecutor.cs
```

인자 없이 실행하면 최근 변경된 파일(git diff)을 대상으로 한다.

## 절차

### Step 1: 대상 식별

- 인자가 프로젝트명이면 해당 프로젝트 전체를 대상으로 함
- 인자가 파일 경로면 해당 파일과 관련 파일을 대상으로 함
- 인자가 없으면 `git diff --name-only HEAD~1` 결과를 대상으로 함

### Step 2: 설계 문서 매핑

대상 프로젝트/파일이 속한 레이어와 컴포넌트를 `_shared/arix-rules.md` §2로 식별한다.

해당 컴포넌트의 설계 명세를 `docs/architecture-v3.md`에서 찾아 읽는다:
- L3 Execution 컴포넌트: §5 (App Runtime, Workflow Engine, Eval Suite, State Store 등)
- L4 Gateway: §6
- L5 Governance: §7
- L2 Registry: §4

### Step 3: 검증 항목

#### 3-A: 컴포넌트 책임 경계

`_shared/arix-rules.md` §10 4자 역할 분담표 기준:
- Registry가 실행을 수행하고 있지 않은지
- App Runtime이 step orchestration을 하고 있지 않은지
- Gateway가 실행 객체를 materialize하고 있지 않은지

#### 3-B: 인터페이스 계약

- Contracts 프로젝트에 정의된 인터페이스를 구현하고 있는지
- 구현이 계약의 의미를 벗어나지 않는지

#### 3-C: State Schema 준수

State 관련 코드가 `_shared/arix-rules.md` §5 14영역 State Schema를 따르는지:
- 각 영역의 데이터가 올바른 영역에 저장되는지
- Output merge 규칙(§5 하단)을 따르는지
- `input` 영역의 immutability가 보장되는지

#### 3-D: Workflow Step Type 준수

Workflow 관련 코드가 `_shared/arix-rules.md` §6 Step Types를 따르는지:
- Phase에 맞는 Step만 구현하고 있는지
- 각 Step의 역할이 설계와 일치하는지

#### 3-E: Action Class 분류

Gateway 관련 코드가 `_shared/arix-rules.md` §7 Action Class를 따르는지:
- Read/Write/Deploy/Dangerous 분류가 올바른지
- 채널 제한이 적용되었는지

### Step 4: 보고서 출력

```
## Impl-Review 보고서

### 대상: Arix.Execution.Workflow
### 레이어: L3 Execution
### 설계 참조: architecture-v3.md §5.3

### 적합
- ✅ Step Executor가 step type별 runner 분기를 올바르게 구현
- ✅ Transition Resolver가 다음 step 계산 책임만 수행

### 위반
- ❌ WorkflowService가 manifest resolve를 직접 수행 (App Runtime 책임)
  참조: §10 4자 역할 분담표 — "런타임 메타 resolve"는 Registry API 제공, App Runtime 호출

### 주의
- ⚠️ State Manager에서 input 영역을 수정하는 코드 발견
  참조: §5 Output merge 규칙 3번 — "input은 수정 금지"
```
