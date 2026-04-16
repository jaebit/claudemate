# External Orchestration for Crew Plugin

## Context

`crew:go`의 9-stage 파이프라인은 모든 서브에이전트 호출을 메인 에이전트 컨텍스트 내에서 수행한다.
5-step task 기준 ~23회 서브에이전트 호출, ~53,000자의 오케스트레이션 오버헤드가 메인 컨텍스트에 누적된다.

Aethra 실험으로 검증된 사실: 외부 Python 스크립트가 오케스트레이션을 담당하면 메인 에이전트 컨텍스트 비용이 **3.2배 감소 (68.9% 절약)**. 핵심 원인은 의존성 주입에 의한 데이터 중복 제거.

이 스펙은 crew 플러그인에 외부 오케스트레이션을 단계적으로 도입하는 계획이다.

**구현 시 첫 작업**: 이 문서를 `/Users/urd_book/Projects/claudemate/plugins/crew/docs/design/05_external_orchestration.md`로 복사할 것.

---

## Phase 1: Execution Orchestrator (Stage 4)

Stage 4(Execution)는 전체 파이프라인에서 컨텍스트 비용이 가장 높다 (5-step 기준 ~25,000자, 전체의 47%).
루프 구조가 결정론적이므로 스크립트 오케스트레이션에 가장 적합하다.

### 신규 파일

#### 1. `hooks/scripts/task_plan_parser.py`

`.caw/task_plan.md` 마크다운을 구조화된 데이터로 변환하는 파서.

**입력**: `tests/fixtures/sample_task_plan.md`와 동일한 형식의 마크다운
```markdown
### Phase 2: Core Implementation
| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 2.1 | Create JWT utility module | ⏳ Pending | Builder | 1.* | `src/auth/jwt.ts` |
```

**출력**: StepNode 리스트
```python
@dataclass
class StepNode:
    id: str              # "2.1"
    phase: int           # 2
    description: str     # "Create JWT utility module"
    status: str          # "pending" | "complete" | "in_progress" | "skipped"
    agent: str           # "Builder"
    deps: list[str]      # ["1.*"] → resolved to ["1.1", "1.2"]
    notes: str           # "`src/auth/jwt.ts`"
    context_files: list[str]  # phase-level Active Context에서 추출
```

**핵심 로직**:
- 마크다운 테이블 행 파싱 (정규식 기반)
- 상태 이모지 매핑: ✅→complete, 🔄→in_progress, ⏳→pending
- 의존성 해석: `1.*` → Phase 1의 모든 step ID, `2.1,2.2` → 개별 참조
- completed/skipped step 필터링 (실행 대상만 반환)

#### 2. `hooks/scripts/execution_orchestrator.py`

Aethra의 `orchestrate.py`를 crew 파이프라인에 맞게 확장한 실행 엔진.

**호출 방식** (메인 에이전트가 Stage 4에서):
```bash
python3 "$CREW_PLUGIN_DIR/hooks/scripts/execution_orchestrator.py" \
    --plan .caw/task_plan.md \
    --state .caw/auto-state.json \
    --cwd "$(pwd)"
```

**핵심 클래스**:

```
ExecutionOrchestrator
├── TaskPlanParser        # task_plan.md → StepNode[]
├── WaveCalculator        # StepNode[] → Wave[] (위상 정렬)
├── BuilderRunner         # claude -p로 Builder 서브에이전트 실행
├── PostStepCycle         # git commit → simplify → tidy commit
├── RecoveryCascade       # 5-level 에러 복구
└── StateManager          # .caw/auto-state.json 읽기/쓰기
```

**실행 흐름**:
```
1. task_plan.md 파싱 → pending steps 추출
2. 의존성 해석 → Wave 계산 (위상 정렬)
3. 각 Wave 순차 실행 (Wave 내부는 현재 순차, Phase 3에서 병렬화)
   3a. Builder 서브에이전트 실행 (claude -p)
   3b. Post-Step Cycle (git commit → simplifier → tidy commit)
   3c. auto-state.json 업데이트
   3d. 실패 시 5-level recovery cascade
4. JSON 결과를 stdout으로 출력
```

**Builder 서브에이전트 호출**:
```python
cmd = [
    "claude", "-p", prompt,
    "--output-format", "text",
    "--allowedTools", "Read,Write,Edit,Bash,Grep,Glob",
    "--permission-mode", "auto",
    "--effort", "medium",
]
# MCP 서버가 필요한 경우
if mcp_config_path:
    cmd += ["--mcp-config", mcp_config_path]
# 비용 제한
if max_budget:
    cmd += ["--max-budget-usd", str(max_budget)]
```

**Builder 프롬프트 구성**:
- `_shared/templates/builder-prompt.md`에서 축약된 Builder 지침 로드
- step description, context files, project CLAUDE.md 주입
- "SIGNAL 출력 금지" 지시 (오케스트레이터가 시그널 관리)
- "완료 후 반드시 commit" 지시

**Post-Step Cycle** (직접 subprocess, claude 호출 아님):
```python
async def post_step_cycle(step):
    # 1. Commit (git 직접 실행)
    if has_changes():
        git_add_all()
        git_commit(f"[feat] Step {step.id}: {step.description}")

    # 2. Simplify (claude -p, --effort low)
    run_simplifier(modified_files)

    # 3. Tidy commit
    if has_changes():
        git_add_all()
        git_commit(f"[tidy] Simplify Step {step.id}")
```

**5-Level Error Recovery**:
```
Level 0: 첫 실행
Level 1: 재시도 (동일 프롬프트 + 이전 에러 메시지 주입)
Level 2: Fixer 에이전트 (claude -p --model haiku, 수정 전용)
Level 3: Planner 재계획 (claude -p, step 재분해)
Level 4: non-blocking step이면 skip
Level 5: abort + 에러 JSON 반환
```

**출력 JSON** (메인 에이전트가 받는 유일한 데이터):
```json
{
    "status": "success|error",
    "steps_completed": 5,
    "steps_total": 5,
    "steps_failed": 0,
    "total_time_s": 245.3,
    "commits": [
        {"step": "2.1", "hash": "abc1234", "message": "[feat] Step 2.1: ..."}
    ],
    "step_results": {
        "2.1": {"status": "complete", "duration_s": 45.7, "recovery_level": 0}
    },
    "files_created": [],
    "files_modified": [],
    "errors": []
}
```

#### 3. `_shared/templates/builder-prompt.md`

`agents/builder.md`(264행)의 축약 버전 (~80행). claude -p 프롬프트에 인라인 주입용.

포함 내용:
- TDD 워크플로우 (test → implement → verify)
- 커밋 규율 (tidy/feat/fix/test 분리)
- Serena-first 편집 우선순위
- 복잡도 자기 평가 (low/medium/high)
- 테스트 자동 실행 규칙

제외 내용:
- YAML frontmatter, 스킬 목록, MCP 서버 참조
- 상세한 예시 (서브에이전트가 직접 탐색)

### 수정 파일

#### 4. `skills/go/SKILL.md` — Stage 4 섹션 (89~204행)

기존 인라인 오케스트레이션 코드 앞에 외부 오케스트레이션 분기 추가:

```markdown
### Stage 4: Execution

**IF NOT --no-external-orch:**

1. Run: `python3 "$CREW_PLUGIN_DIR/hooks/scripts/execution_orchestrator.py" --plan .caw/task_plan.md --state .caw/auto-state.json --cwd "$(pwd)"`
2. Parse JSON result from stdout
3. If status == "success": continue to Stage 5
4. If status == "error": report failure, check if --continue possible

**ELSE (--no-external-orch, legacy mode):**
[기존 89~204행 로직 그대로 유지]
```

새 플래그: `--no-external-orch` — 기존 동작 보존용

#### 5. `_shared/schemas/auto-state.schema.json` — config 객체 확장

```json
"external_orchestration": {
    "type": "boolean",
    "default": true,
    "description": "Use external Python orchestrators for execution and review stages"
},
"codex_mode": {
    "type": "boolean",
    "default": false,
    "description": "Use Codex for step execution"
}
```

execution 객체에 추가:
```json
"orchestrator_artifacts": {
    "type": ["string", "null"],
    "description": "Path to orchestrator temp artifacts directory"
}
```

### auto_enforcer.py 호환성

변경 불필요. 이유:
- 오케스트레이터는 SIGNAL을 출력하지 않음
- 메인 에이전트가 오케스트레이터 결과 수신 후 `SIGNAL: EXECUTION_COMPLETE` 출력
- auto_enforcer는 메인 에이전트의 transcript에서 시그널 감지 → 정상 전이
- 오케스트레이터가 auto-state.json의 execution 필드를 직접 업데이트하므로 데이터 일관성 유지

### 미지원 (Phase 1)

- `--team` 모드: Agent Teams는 `claude -p`로 구동 불가. 기존 인라인 오케스트레이션 유지
- 크로스-phase 병렬: Wave 내 step은 순차 실행. Phase 3에서 병렬화
- MCP 서버 자동 감지: `--mcp-config` 경로를 수동 지정 필요

---

## Phase 2: Review Orchestrator (Stage 6-7)

### 신규 파일

#### `hooks/scripts/review_orchestrator.py`

3 Reviewer 병렬 → Advisor triage → Fixer의 Diamond DAG를 외부 스크립트로 실행.

**호출 방식**:
```bash
python3 "$CREW_PLUGIN_DIR/hooks/scripts/review_orchestrator.py" \
    --state .caw/auto-state.json \
    --cwd "$(pwd)" \
    --max-rounds 3
```

**DAG 구조**:
```
review-functional ──┐
review-security  ──┼──▶ aggregate ──▶ [contested?] ──▶ advisor-triage ──▶ fixer
review-quality   ──┘                   [unanimous?] ──▶ done
```

**모델 라우팅**:
- Reviewer: 기본 모델 (Sonnet)
- Advisor triage: `--model opus`
- Fixer: `--model haiku`

**Review → Fix 루프**: 최대 3라운드, 각 라운드마다 전체 DAG 재실행

### 수정 파일

- `skills/go/SKILL.md` — Stage 6-7 섹션에 외부 오케스트레이션 분기 추가
- `_shared/parallel-validation.md` — reviewer 프롬프트 템플릿을 오케스트레이터용으로 추출

### 공유 라이브러리 추출

#### `hooks/scripts/crew_orch_lib.py`

Phase 1의 코드를 리팩터링하여 공유 모듈 생성:
- `TaskPlanParser` — task_plan.md 파서
- `StateManager` — auto-state.json 읽기/쓰기
- `SubAgentRunner` — claude -p 실행 래퍼
- `WaveCalculator` — 위상 정렬 (Aethra의 `_topological_levels()` 포팅)

---

## Phase 3: Unified Pipeline Orchestrator (Stage 1-8)

### 신규 파일

#### `hooks/scripts/pipeline_orchestrator.py`

Phase 1 + Phase 2를 통합. Stage 1-8을 하나의 스크립트로 실행.

```bash
python3 "$CREW_PLUGIN_DIR/hooks/scripts/pipeline_orchestrator.py" \
    --task "Add logout button" \
    --state .caw/auto-state.json \
    --cwd "$(pwd)"
```

**Stage 매핑**:
| Stage | 실행 방법 | 모델 |
|-------|---------|------|
| 1 (Expansion) | claude -p + Analyst 프롬프트 → `.caw/spec.md` | sonnet |
| 2 (Init) | claude -p + Bootstrapper 프롬프트 (조건부) | haiku |
| 3 (Planning) | claude -p + Planner 프롬프트 → `.caw/task_plan.md` | sonnet |
| 4 (Execution) | execution_orchestrator 로직 위임 | sonnet |
| 5 (QA) | claude -p QA loop (최대 2 cycle) | sonnet |
| 6-7 (Review+Fix) | review_orchestrator 로직 위임 | sonnet/opus/haiku |
| 8 (Check) | claude -p + ComplianceChecker 프롬프트 | sonnet |

**Stage 9 (Reflect)는 제외**: Ralph Loop는 세션 전체 컨텍스트가 필요하므로 메인 에이전트에서 실행.

### 수정 파일

- `skills/go/SKILL.md` — 전체 파이프라인을 외부 오케스트레이터에 위임하는 모드 추가
- `hooks/scripts/auto_enforcer.py` — `config.external_orchestration`이 true일 때 continuation prompt injection 억제

---

## 예상 효과

| 구간 | 현재 (인라인) | Phase 1 적용 후 | Phase 3 적용 후 |
|------|-------------|---------------|---------------|
| Stage 1-3 | ~6,000 chars | ~6,000 chars | ~2,000 chars |
| Stage 4 (5 steps) | ~25,000 chars | **~2,000 chars** | ~2,000 chars |
| Stage 5-7 | ~18,000 chars | ~18,000 chars | **~3,000 chars** |
| Stage 8-9 | ~4,000 chars | ~4,000 chars | ~4,000 chars |
| **총계** | **~53,000 chars** | **~30,000 chars (43% 감소)** | **~11,000 chars (79% 감소)** |

---

## 구현 순서

### Phase 1 (이번 구현 대상)

```
Step 1: 이 스펙을 crew/docs/design/05_external_orchestration.md로 복사
Step 2: task_plan_parser.py 생성 + 단위 테스트
Step 3: execution_orchestrator.py 핵심 엔진 (Aethra 기반)
Step 4: Post-Step Cycle 구현 (git commit + simplify)
Step 5: 5-level error recovery 구현
Step 6: StateManager (auto-state.json 읽기/쓰기)
Step 7: builder-prompt.md 템플릿 생성
Step 8: skills/go/SKILL.md 수정 (--no-external-orch 분기)
Step 9: auto-state.schema.json 확장
Step 10: 통합 테스트 (sample_task_plan.md 대상 실행)
```

---

## 검증 방법

### 단위 테스트
```bash
cd /Users/urd_book/Projects/claudemate/plugins/crew
python -m pytest tests/test_task_plan_parser.py -v
python -m pytest tests/test_execution_orchestrator.py -v
```

### 통합 테스트
```bash
# sample task plan으로 오케스트레이터 직접 실행
python3 hooks/scripts/execution_orchestrator.py \
    --plan tests/fixtures/sample_task_plan.md \
    --state tests/fixtures/sample_auto_state.json \
    --cwd /tmp/test-project \
    --dry-run  # claude -p 호출 없이 파이프라인 구조만 검증
```

### 컨텍스트 비용 측정
Aethra의 비용 측정 스크립트를 적용하여 인라인 vs 외부 오케스트레이션 비교:
```bash
# 오케스트레이터 실행 후 아티팩트 분석
python3 /Users/urd_book/Projects/Aethra/measure_cost.py \
    --artifacts /tmp/crew_exec_*/
```

### 기존 테스트 호환성
```bash
python -m pytest tests/test_plugin_structure.py -v  # 플러그인 구조 검증
```

---

## 핵심 파일 참조

| 파일 | 역할 | 작업 |
|------|------|------|
| `hooks/scripts/execution_orchestrator.py` | 실행 엔진 | **신규 생성** |
| `hooks/scripts/task_plan_parser.py` | task_plan.md 파서 | **신규 생성** |
| `_shared/templates/builder-prompt.md` | Builder 축약 프롬프트 | **신규 생성** |
| `skills/go/SKILL.md` | 메인 파이프라인 스킬 | **수정** (89~204행) |
| `_shared/schemas/auto-state.schema.json` | 상태 스키마 | **수정** (config 확장) |
| `hooks/scripts/auto_enforcer.py` | Stop hook | 변경 없음 (호환성 확인만) |
| `tests/fixtures/sample_task_plan.md` | 테스트 fixture | 참조용 |
| `/Users/urd_book/Projects/Aethra/orchestrate.py` | 레퍼런스 구현 | Aethra에서 포팅 |

---

## 리스크 및 완화

| 리스크 | 심각도 | 완화 |
|--------|--------|------|
| MCP 서버(Serena, Context7) 접근 불가 | 높음 | `.mcp.json` 존재 시 `--mcp-config`로 전달, 없으면 기본 도구만 사용 |
| `claude -p` 권한 거부 | 중간 | `--permission-mode auto` 기본, 테스트 시 확인 |
| task_plan.md 형식 변형 | 낮음 | 파서를 관대하게 구현, fixture 기반 테스트 |
| `--team` 모드 미지원 | 낮음 | `--no-external-orch`로 폴백, 명시적 문서화 |
