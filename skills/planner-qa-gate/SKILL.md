# Planner QA Gate

Planner가 계획을 완성한 직후, Worker 실행 전에 acceptance_criteria 품질을 검증합니다.

> **목적**: Contract Validation에서 REVISION_NEEDED 반복을 사전 방지.

---

## 실행 절차

### 1. 주관적 문구 스캔

`data/current-task.yaml`을 열고 모든 `acceptance_criteria` 항목에서 다음 패턴을 검색:

```
정확히 | 완전히 | 적절히 | 올바르게 | 제대로 | 충분히
correctly | properly | accurately | completely
```

발견되면 → **즉시 수정** (아래 변환 규칙 적용).

### 2. 이진 검증 가능성 확인

각 기준이 아래 형식 중 하나인지 확인:

| 형식 | 예시 |
|------|------|
| 패턴 부재 | `grep -c 'X' file = 0` |
| 패턴 존재 | `grep -c 'X' file > 0` |
| 파일 존재 | `test -f path` |
| 파일 부재 | `test ! -f path` |
| 심볼 부재 | `grep -c 'function foo' file = 0` |
| 임포트 확인 | `grep -c 'import.*X' file = 1` |

형식 불일치 → **구체적 명령어로 재작성**.

### 3. 범위 명확성 확인

- "제거됨" → 어느 파일에서? 파일 경로 명시
- "추가됨" → 어느 파일에? 패턴은 무엇?
- "유지됨" → 무엇이? `> 0` 조건 명시

---

## 변환 규칙 (Before → After)

### 문서 수정

```yaml
# Before (거부됨)
- "README.md에서 arix-dev 참조가 완전히 제거됨"

# After (통과)
- "grep -c 'arix-dev' plugins/X/README.md = 0"
```

### 코드 변경

```yaml
# Before (거부됨)
- "stop-reminder.mjs에서 중복 함수가 적절히 제거됨"

# After (통과)
- "grep -c 'function isConfiguredProject' plugins/X/hooks/stop-reminder.mjs = 0"
- "grep -c 'detect-project.mjs' plugins/X/hooks/stop-reminder.mjs = 1"
```

### 설정 수정

```yaml
# Before (거부됨)
- "plugin.json의 description이 codex CLI 방식을 정확히 반영"

# After (통과)
- "grep -c 'codex-harness' plugins/X/.claude-plugin/plugin.json = 0"
- "grep -c 'codex' plugins/X/.claude-plugin/plugin.json > 0"
```

### 유지 확인 (의도적 보존)

```yaml
# Before (불명확)
- "docs/architecture-decisions.md의 arix-dev 참조는 유지 (역사적 맥락)"

# After (명확)
- "grep -c 'arix-dev' plugins/X/docs/architecture-decisions.md > 0"
```

---

## 판정

모든 항목 통과 시 → `QA_GATE: PASSED` — Worker 실행 진행  
하나라도 실패 시 → 즉시 수정 후 재검증 (최대 1회)

---

## 이 스킬이 필요한 상황

- Planner 출력 직후, Contract Validation 이전
- 이전 세션에서 REVISION_NEEDED가 발생한 경우
- 스프린트 계획을 수동으로 작성한 경우
