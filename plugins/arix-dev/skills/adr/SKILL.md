---
name: adr
description: >
  This skill should be used when the user asks "ADR 작성해줘", "설계 결정 기록", "adr",
  "왜 이렇게 결정했는지 문서화해줘", "아키텍처 결정 기록", or wants to create an Architecture
  Decision Record documenting a design choice with context, rationale, alternatives, and consequences.
argument-hint: "<decision-title> e.g. \"왜 PostgreSQL JSONB를 선택했는가\""
user_invocable: true
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---

# /adr — Architecture Decision Record 생성

설계 결정에 대한 ADR(Architecture Decision Record)을 표준 포맷으로 생성한다.

## 사용법

```
/adr "왜 Control Plane을 .NET으로 가는가"
/adr "State Store에 PostgreSQL JSONB를 선택한 이유"
```

## 참조

이 스킬을 실행하기 전에 반드시 `_shared/arix-rules.md`를 읽어 규칙 전체를 파악한다.

## 절차

### Step 1: 기존 ADR 확인

`docs/adr/` 디렉토리의 기존 ADR 목록을 확인하여 번호를 채번한다.

```bash
ls docs/adr/ADR-*.md 2>/dev/null | sort | tail -1
```

다음 번호를 자동 할당한다. 기존 ADR이 없으면 ADR-001부터 시작.

### Step 2: 관련 설계 문서 참조

사용자가 제시한 결정 주제와 관련된 설계 문서 섹션을 찾는다:
- `docs/architecture-v3.md`
- `docs/tech-stack-standard-v1.md`
- `docs/repo-design-v1.md`
- `_shared/arix-rules.md`

### Step 3: ADR 문서 생성

`docs/adr/ADR-{번호}-{slug}.md` 형식으로 파일을 생성한다.

### ADR 표준 포맷

```markdown
# ADR-{번호}: {제목}

- **상태**: Accepted | Proposed | Deprecated | Superseded by ADR-XXX
- **일자**: {오늘 날짜}
- **결정자**: {사용자에게 질문}

## 컨텍스트

{이 결정이 필요한 배경. 어떤 문제를 해결하려 하는가.}

## 결정

{무엇을 결정했는가. 명확하고 간결하게.}

## 근거

{왜 이 결정을 했는가. 대안과 비교.}

### 고려한 대안

| 대안 | 장점 | 단점 | 탈락 이유 |
|------|------|------|-----------|
| ... | ... | ... | ... |

## 결과

{이 결정으로 인해 발생하는 영향. 긍정적/부정적 모두.}

## 관련 문서

- architecture-v3.md §{관련 섹션}
- tech-stack-standard-v1.md §{관련 섹션}
- arix-rules.md §{관련 섹션}
```

### Step 4: 사용자에게 내용 확인

ADR 초안을 보여주고 수정 사항을 확인한다.

### Step 5: 결과

```
## ADR 생성 완료

- 파일: docs/adr/ADR-003-state-store-postgresql-jsonb.md
- 상태: Accepted
- 관련 설계: architecture-v3.md §5.5, tech-stack-standard-v1.md §2.4
```
