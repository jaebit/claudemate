# Arix 플랫폼 강제 규칙 (Single Source of Truth)

> 이 문서는 `docs/architecture-v3.md`, `docs/repo-design-v1.md`, `docs/tech-stack-standard-v1.md`에서
> 추출한 **강제 가능한 규칙**을 통합한 참조 문서다. 모든 arix-dev 스킬은 이 문서를 기준으로 검증한다.

---

## 1. 6-Layer 허용 호출 경로 매트릭스

| 출발 | 허용 도착 | 금지 도착 |
|------|-----------|-----------|
| L1 Interaction | L3 App Runtime, L4 Gateway (기존 MCP Clients만) | L2 직접, L5 직접, L6 직접 |
| L2 Discovery | (피호출 전용 — L3에서 호출) | L1, L4, L5, L6 직접 호출 |
| L3 Execution | L2 (manifest resolve), L4 (ToolStep), L5 (Approval Policy 조회) | L1 직접, L6 직접 |
| L4 Gateway | L5 (IAM introspect), L6 (route to services) | L1, L2, L3 직접 |
| L5 Governance | (피호출 전용 — L3, L4에서 조회) | L1, L2, L6 직접 호출 |
| L6 Capability Services | (피호출 전용 — L4 Gateway 경유) | 어떤 레이어도 직접 호출 불가 |

**핵심 원칙**: L6 서비스는 **반드시 L4 Gateway를 경유**해서만 접근한다. L3→L6 직접 호출은 금지.

---

## 2. 프로젝트→레이어 매핑 테이블

| .NET 프로젝트 | 레이어 | 역할 |
|---------------|--------|------|
| `Arix.BuildingBlocks.*` | Cross-cutting | 공통 유틸 (Result, Clock, OTel, Polly, 인증 모델) |
| `Arix.Registry.Api` | L2 | Registry HTTP API |
| `Arix.Registry.Application` | L2 | App/Skill/Agent 비즈니스 로직 |
| `Arix.Registry.Domain` | L2 | Registry 도메인 모델 |
| `Arix.Registry.Infrastructure` | L2 | Registry 영속성 |
| `Arix.Registry.Contracts` | L2 | Registry 공개 계약 |
| `Arix.Execution.AppRuntime` | L3 | App Runtime (manifest load, context, lifecycle) |
| `Arix.Execution.Workflow` | L3 | Workflow Engine (step orchestration) |
| `Arix.Execution.Eval` | L3 | Eval Suite (rule/model-based 평가) |
| `Arix.Execution.StateStore` | L3 | State Store (PG + JSONB) |
| `Arix.Execution.AgentRuntime` | L3 | LLM 실행 추상화 |
| `Arix.Execution.Approval` | L3 | Approval Runner (실행) |
| `Arix.Execution.Release` | L3 | Release Orchestrator (배포 실행) |
| `Arix.Execution.Notifications` | L3 | 알림 서비스 |
| `Arix.Execution.Contracts` | L3 | Execution 공개 계약 |
| `Arix.Gateway.Api` | L4 | Gateway HTTP 엔드포인트 |
| `Arix.Gateway.Policy` | L4 | Action Classifier + PDP + Budget |
| `Arix.Gateway.Routing` | L4 | YARP 라우팅 |
| `Arix.Gateway.SurfaceRegistry` | L4 | MCP Surface 동적 등록 |
| `Arix.Gateway.Contracts` | L4 | Gateway 공개 계약 |
| `Arix.Knowledge.*` | L6 (Knowledge) | RAG, 검색, Citation |
| `Arix.Knowledge.Contracts` | L6 | Knowledge 공개 계약 |
| `Arix.Governance.ApprovalPolicy` | L5 | 승인 정책 정의 |
| `Arix.Governance.Audit` | L5 | 감사 정책 |
| `Arix.Governance.DataClassification` | L5 | 데이터 분류 |
| `Arix.Governance.Contracts` | L5 | Governance 공개 계약 |
| `Arix.Hosts.*` | Deploy | 배포 엔트리포인트 (Program.cs) |

---

## 3. 레이어 간 허용 프로젝트 참조 규칙

### 3.1 허용 참조 방향

```
*.Domain       → BuildingBlocks.Core, 자기 레이어 Contracts만
*.Application  → 자기 Domain, 자기 Contracts, BuildingBlocks.*
*.Infrastructure → 자기 Application, 자기 Domain, BuildingBlocks.*
*.Api          → 자기 Application, 자기 Contracts, BuildingBlocks.*
*.Contracts    → BuildingBlocks.Contracts만 (또는 의존 없음)
*.Hosts.*      → 자기 레이어 Api, Infrastructure, BuildingBlocks.*
```

### 3.2 교차 레이어 참조 허용

| 참조하는 프로젝트 | 참조 가능 대상 |
|-------------------|----------------|
| `Arix.Execution.*` | `Arix.Registry.Contracts`, `Arix.Gateway.Contracts`, `Arix.Governance.Contracts` |
| `Arix.Gateway.*` | `Arix.Governance.Contracts` |
| `Arix.Registry.*` | (외부 Contracts 참조 없음) |
| `Arix.Governance.*` | (외부 Contracts 참조 없음) |
| `Arix.Knowledge.*` | `Arix.BuildingBlocks.*`만 |

### 3.3 절대 금지 참조

- **Infrastructure → Domain 역참조** 금지 (어떤 레이어든)
- **L6 → L3 참조** 금지 (Capability Services가 Execution을 참조하면 안 됨)
- **L4 → L3 참조** 금지 (Gateway가 Execution을 참조하면 안 됨)
- **L5 → L3 참조** 금지 (Governance가 Execution을 참조하면 안 됨)
- **어떤 프로젝트든 → Hosts 참조** 금지 (Hosts는 최종 조립점)
- **Contracts → Application/Infrastructure 참조** 금지

---

## 4. 기술 스택 필수/금지 테이블

### 4.1 필수 기술

| 영역 | 기술 | 비고 |
|------|------|------|
| Platform Core | ASP.NET Core Minimal API | 모든 API 프로젝트 |
| Worker | .NET Worker Service | 백그라운드 처리 |
| Gateway | YARP | 리버스 프록시 |
| ORM | Dapper + EF Core 혼합 | 상황별 선택 |
| Resilience | Polly | Circuit Breaker, Retry |
| Observability | OpenTelemetry → Jaeger + Prometheus | 분산 트레이싱 |
| Primary DB | PostgreSQL + JSONB | State + 메타데이터 |
| Vector | pgvector | RAG |
| Storage | MinIO | 파일 저장 |
| Protocol | MCP (Streamable HTTP) | 서비스 간 통신 |
| Embedding | bge-m3 | 임베딩 모델 |

### 4.2 금지 사항

| 금지 | 이유 |
|------|------|
| Core 분산 구현 (Registry→Node, Workflow→Python 등) | 운영 불가 |
| Workflow/State를 언어별로 다르게 구현 | Contract 깨짐 |
| 배포를 App 내부 CLI로 직접 실행 | 반드시 Workflow → Release Orchestrator |
| Gateway 우회 (L3→L6 직접 호출) | 정책 집행 우회 |
| Desktop Agent OS에 workflow worker/release orchestrator 내장 | Local/Server 분리 원칙 위반 |

### 4.3 Polyglot 허용 영역

| 언어 | 허용 영역 |
|------|-----------|
| Go | CLI 도구, MCP bridge, lightweight tools |
| Python | RAG, Eval (일부), 데이터 파이프라인 |
| Rust | 보안, 고성능 컴포넌트 |
| TypeScript | UI (Electron Agent OS), 플러그인 |
| .NET | 플랫폼 코어 (필수) |

---

## 5. 14영역 State Schema

| # | 영역 | 용도 | Phase |
|---|------|------|-------|
| 1 | `identity` | instanceId, workflowId, appId, version | Phase 1 |
| 2 | `status` | phase, result, currentStepId, retryable | Phase 1 |
| 3 | `input` | 사용자 원본 요청 (immutable) | Phase 1 |
| 4 | `data` | 단계별 핵심 산출물 | Phase 1 |
| 5 | `control` | revision, visitedSteps, retry count, branch path | Phase 1 |
| 6 | `errors` | 실패 이력 누적 | Phase 1 |
| 7 | `audit` | traceId, spanId, tags, refs | Phase 1 (traceId만) |
| 8 | `channel` | 시작 채널 정보 | Phase 2 |
| 9 | `actor` | initiatedBy, owner, runAs | Phase 2 |
| 10 | `approval` | required, policyId, state, approvers | Phase 2 |
| 11 | `evaluation` | latest, history | Phase 2 |
| 12 | `notifications` | requested, sent | Phase 2 |
| 13 | `release` | mode, state, target, artifact, strategy | Phase 3 |
| 14 | `artifacts` | outputs, citations | Phase 3 |

**Output merge 규칙**:
1. 각 step은 `data.<outputKey>`로 저장
2. `control`/`approval`/`release`는 전용 runner만 수정 가능
3. `input`은 수정 금지 (변경은 `userCorrections`로 관리)
4. LLM 출력은 schema validation → normalization → typed projection 후 state 반영

---

## 6. 8 Workflow Step Types + Phase

| Step Type | 용도 | Phase |
|-----------|------|-------|
| `AgentStep` | LLM/Agent Runtime 수행 | Phase 1 |
| `ToolStep` | 명시적 도구 실행 (L4 Gateway 경유) | Phase 1 |
| `WaitInputStep` | 사용자 입력 대기 | Phase 1 |
| `EvalStep` | 결과 품질·정책·근거 평가 | Phase 1 |
| `BranchStep` | 조건 분기 | Phase 1 |
| `ApprovalStep` | 사람 승인 대기 (L5 Policy 연동) | Phase 2 |
| `LoopStep` | 반복 수행 | Phase 2 |
| `ReleaseStep` | 배포 실행 (Release Orchestrator 호출) | Phase 3 |

---

## 7. 4 Action Class 분류

| Class | 설명 | 채널 제한 |
|-------|------|-----------|
| `Read` | 정보 조회 | 모든 채널 허용 |
| `Write` | 외부 시스템 변경 | Agent OS, Mattermost |
| `Deploy` | 배포 트리거 | Server Runtime 전용, Approval 필수 |
| `Dangerous` | 고위험 실행 | Server Runtime 전용, Approval + Eval 필수 |

**기존 MCP Clients 정책**: Deploy/Dangerous class action은 Gateway에서 차단.

---

## 8. Source Authority 등급 (A1–A4)

| 등급 | 소스 | 제한 |
|------|------|------|
| **A1 — Authoritative** | docs, approval policy, 공식 스키마, 운영 매뉴얼 | 없음 |
| **A2 — Operational** | issues, deploy history, audit log, 변경 티켓 | 정책 재정의 불가 |
| **A3 — Contextual** | mattermost 대화, 회의록 | 의사결정 원천으로 단독 사용 금지 |
| **A4 — Diagnostic** | logs, traces, metrics | 의사결정 근거 아님, 진단 보조만 |

**적용 규칙**:
- 배포 계획 근거가 A3 단독이면 evidence check fail → retry
- 승인 판단 근거는 A1 소스 1개 이상 필수
- A4는 장애 분석 워크플로우에서만 primary 근거 허용
- Gateway deploy.plan.validate: A1 근거 1개 이상 첨부 강제 (Hard deny)
- Approval Runner 승인 요청: A1/A2 근거 필수, A3-only이면 요청 거부 (Hard deny)
- PDP high-risk action: A3-only 근거이면 자동 escalate (Soft escalate)

---

## 9. 절대 금지 패턴 목록

1. **Gateway 우회**: L3 Execution에서 L6 Capability Services 직접 호출
2. **배포 직접 실행**: App CLI에서 직접 배포 — 반드시 Workflow → ReleaseStep → Release Orchestrator
3. **Local Runtime에서 ApprovalStep/ReleaseStep 실행**: Server Runtime 전용
4. **Mattermost → Local App Runtime 직접 연결**: Mattermost는 반드시 Server App Runtime 경유
5. **Infrastructure → Domain 역참조**: 어떤 레이어든 Infrastructure가 Domain을 참조하면 안 됨
6. **Contracts → Application/Infrastructure 참조**: Contracts는 하위 계층만 참조
7. **Core 분산 구현**: Platform Core를 여러 언어로 나눠 구현
8. **Agent OS에 workflow worker/release orchestrator 내장**
9. **A3-only 근거로 배포/승인 진행**: Source Authority 위반

---

## 10. 4자 역할 분담표

| 책임 | Registry (L2) | App Runtime (L3) | Workflow Engine (L3) | Gateway (L4) |
|------|---------------|-------------------|----------------------|---------------|
| 계약 원본 저장 | ✓ | | | |
| 심사/서명 검증 | ✓ | | | |
| 런타임 메타 resolve | ✓ API 제공 | ✓ 호출자 | | |
| 실행 객체 materialize | | ✓ | | |
| 실행 순서/상태 전이 | | | ✓ | |
| 실행 권한/접근 통제 | | | | ✓ |
| 크리덴셜 주입 | | | | ✓ |

**원칙**: Registry = "무엇을 실행할 수 있는가", App Runtime = "어떻게 올리는가", Workflow Engine = "어떤 순서로 진행하는가", Gateway = "접근해도 되는가". 이 경계를 넘는 책임 이동은 금지.

---

## 11. Workflow 상태 모델

```
pending → running → (waiting_input | waiting_approval | paused) → running → succeeded
                                                                           → failed
                                                                           → cancelled
                                                                           → rolled_back
```

---

## 12. Eval 적용 위치 (5곳)

| 위치 | 시점 | Phase |
|------|------|-------|
| Step Gate | 매 step output 후 | Phase 1 |
| Deploy Gate | ReleaseStep 진입 전 | Phase 3 |
| Content Gate | 보고서/문서 게시 전 | Phase 2 |
| Escalation Trigger | 고위험 실행 감지 시 | Phase 2 |
| Publish Review | App 등록/업데이트 시 (L2 연동) | Phase 2 |

---

## 13. 로드맵 Phase 요약

| Phase | 목표 | 핵심 Sprint |
|-------|------|-------------|
| Phase 1 — Pilot MVP (~10 users) | 단일 App workflow-first 실행 | 1-A Foundation, 1-B Core Engine, 1-C App Shell |
| Phase 2 — Team (~30 users) | Mattermost 협업 + 승인 + 비동기 | 2-A Approval, 2-B MM 통합, 2-C Eval 고도화 |
| Phase 3 — Enterprise (~500 users) | 배포 통제, 멀티테넌트, 거버넌스 | 3-A Release, 3-B Governance, 3-C Analytics, 3-D UX |

---

## 14. 구현 우선순위

| 순위 | 프로젝트 |
|------|----------|
| 1순위 | `Arix.Execution.Contracts`, `Arix.Execution.StateStore`, `Arix.Execution.Workflow`, `Arix.Registry.Contracts`, `Arix.Registry.Api` |
| 2순위 | `Arix.Execution.AppRuntime`, `Arix.Execution.Eval`, `Arix.Gateway.Contracts`, `Arix.Gateway.Api` |
| 3순위 | `Arix.Execution.Approval`, `Arix.Execution.Release`, `Arix.Knowledge.*` |

**첫 App**: `apps/interview-coach` → 그 다음 `apps/deploy-assistant`
