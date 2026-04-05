# Task Planner 스킬

사용자 요청을 구조화된 태스크 계획으로 변환하는 스킬입니다.

## 핵심 규칙: acceptance_criteria는 반드시 이진 검증 가능

**모든 기준은 `grep`/`test`/`wc` 명령어로 Pass/Fail 판정 가능해야 한다.**

### ❌ 즉시 거부되는 표현

| 주관적 문구 | 이유 |
|------------|------|
| "정확히 반영됨" | 반영 정도를 측정할 방법 없음 |
| "완전히 제거됨" | 어느 범위에서 제거했는지 불명확 |
| "적절히 수정됨" | 적절함의 기준이 주관적 |
| "올바르게 설정됨" | 올바름의 기준이 없음 |
| "패턴 적용됨" | 어떤 패턴인지 불명확 |

### ✅ 허용되는 기준 형식

```yaml
# 패턴 부재 확인
- "grep -c 'old_pattern' file.txt = 0"

# 패턴 존재 확인
- "grep -c 'new_pattern' file.txt > 0"

# 파일 존재/부재
- "test -f path/to/file → exits 0"
- "test ! -f path/to/file → exits 0"

# 함수/심볼 제거 확인
- "grep -c 'function foo' file.js = 0"

# 임포트 추가 확인
- "grep -c 'import.*module' file = 1"
```

---

## 골든 예제 (실제 REVISION_NEEDED → PASS 케이스)

### 케이스 1 (2026-04-05, autopilot 최정화)

**REVISION_NEEDED 원인:**
```yaml
# 거부된 기준
- "description이 현재 사용하는 codex CLI 방식을 정확히 반영"
- "multi-model-debate 플러그인의 codex -q 패턴 적용"
- "업데이트된 로직이 기존 autopilot 워크플로우와 호환"
```

**PASS로 수정된 기준:**
```yaml
- "plugins/autopilot/.claude-plugin/plugin.json description에 'codex-harness' 없음"
- "plugins/autopilot/.claude-plugin/plugin.json description에 'codex' 포함"
- "plugins/autopilot/skills/autopilot/SKILL.md에 'codex -q' 패턴 포함"
- "plugins/autopilot/skills/autopilot/SKILL.md에 '## Phase 4: REVIEW' 섹션 헤더 유지됨"
```

### 케이스 2 (2026-04-05, arch-guard 리뷰)

**REVISION_NEEDED 원인:**
```yaml
# 거부된 기준
- "README.md에서 'arix-dev' 섹션이 완전히 제거됨"
- "README.md에서 '../arix-dev/' 링크가 제거됨"
```

**PASS로 수정된 기준:**
```yaml
- "grep -c 'arix-dev' plugins/arch-guard/README.md = 0"
- "grep -c '\\.\\./' plugins/arch-guard/README.md = 0"
- "grep -c 'arix-dev' plugins/arch-guard/docs/architecture-decisions.md > 0 (유지 확인)"
```

---

## 스프린트 설계 원칙

1. **단일 책임**: 스프린트 하나 = 목표 하나
2. **독립성**: 가능하면 병렬 실행 가능하게 설계
3. **파일 명시**: `files:` 필드에 수정 대상 파일 목록
4. **의존성 명시**: `dependencies: ["sprint-N"]`

### 스프린트 크기

- 파일 1-2개 변경: 단일 스프린트
- 파일 3개+: 스프린트 분리 고려
- 의존 관계 있으면 순차, 없으면 병렬

---

## 자체 검토 체크리스트 (계획 완성 후)

계획을 저장하기 전 반드시 확인:

- [ ] 모든 acceptance_criteria가 grep/test/wc 명령어로 확인 가능한가?
- [ ] "정확히", "완전히", "적절히", "올바르게" 같은 부사가 없는가?
- [ ] 삭제 확인 기준에 `= 0`이 명시되어 있는가?
- [ ] 유지 확인 기준에 `> 0`이 명시되어 있는가?
- [ ] 각 스프린트의 `files:` 필드가 채워져 있는가?

체크리스트 하나라도 미통과 시 기준 수정 후 저장.
