# claudemate 플러그인 Hooks 아키텍처 심층 분석 보고서

## 1. 공유 패턴 분석

**구현 4개 플러그인의 공통 이벤트 패턴**
**arch-guard**: 3개 이벤트 (SessionStart, PreToolUse, Stop) — 아키텍처 보호 중심
**crew**: 5개 이벤트 (SessionStart, Stop, PreToolUse, PostToolUse, SessionEnd) — 가장 복합적
**autopilot**: 2개 이벤트 (SessionStart, SubagentStop) — 빌드 검증 중심  
**gemini-cli**: 1개 이벤트 (SessionStart) — 최소 구성

**공통 패턴**:
- 모든 플러그인이 SessionStart 이벤트를 사용하여 초기화 수행
- Node.js(arch-guard, autopilot, gemini-cli) vs Python(crew) 스크립트 언어 이분화
- `${CLAUDE_PLUGIN_ROOT}` 경로 변수를 일관되게 사용
- PreToolUse는 가드 역할(arch-guard: layer-check, crew: plan adherence)

**차이점**:
- crew만 PostToolUse/SessionEnd 사용하여 완전한 라이프사이클 관리
- async/timeout 속성은 crew만 활용 (rate_limit_handler.py: 5초, gemini_edit_review.py: 45초)
- autopilot만 SubagentStop 사용하여 서브에이전트 종료 시점 후킹

**이벤트 타입 분석** (`cat hooks.json | jq '.hooks | keys'` 결과):
총 6개 이벤트 유형 발견:
1. **SessionStart** (4/4) — 범용 초기화
2. **PreToolUse** (2/4) — 실행 전 검증/가드 
3. **Stop** (2/4) — 세션 종료 처리
4. **PostToolUse** (1/4) — 실행 후 관찰/기록
5. **SessionEnd** (1/4) — 완전 세션 종료
6. **SubagentStop** (1/4) — 서브에이전트 전용

## 2. 미구현 원인 분석

**commands/ 기반 플러그인의 구조적 특성**
`fd -H -t f` 결과 분석:

**codex-cli**: commands/apply.md, commands/cloud.md — 단순 명령어 래핑
**multi-model-debate**: skills/* 만 보유 — 토론 orchestration 중심
**worktree**: skills/cleanup, skills/create, skills/merge — git 워크트리 관리

**Hooks가 불필요한 이유**:
1. **순수 명령어 플러그인** (codex-cli): 외부 CLI 도구 래핑만 수행. 실행 전후 가드나 상태 변경이 불필요
2. **스킬 중심 플러그인** (multi-model-debate, worktree): 사용자 요청 시에만 동작하는 일회성 작업. 세션 라이프사이클과 무관
3. **상태 비저장**: 이들 플러그인은 claudemate 세션 상태를 변경하지 않아 hooks로 감시할 필요 없음

대조적으로 구현된 4개는:
- **arch-guard**: 아키텍처 규칙 위반 방지 필요
- **crew**: 복잡한 멀티모델 워크플로우 관리 필요
- **autopilot**: 빌드 상태 지속 검증 필요
- **gemini-cli**: 외부 AI 서비스 초기화 필요

## 3. 리스크 목록

**[P0] crew 플러그인 복잡도 과부하**
**근거**: `cat plugins/crew/hooks/hooks.json | python3 -m json.tool` → 8개 hook, 6개 이벤트 유형
**상세**: PreToolUse에서 "*" matcher 사용 → 모든 도구 호출마다 observe.py 실행
**위험성**: 성능 저하, 디버깅 복잡도 증가, 단일 장애점

**[P1] async/timeout 설정 불일치** 
**근거**: crew만 async:true, timeout:5~45초 사용. 다른 플러그인은 동기식
**상세**: `gemini_edit_review.py: timeout:45`, `rate_limit_handler.py: timeout:5`
**위험성**: 타임아웃 시 hooks 체인 중단, 비일관적 사용자 경험

**[P1] Node.js/Python 혼재 환경**
**근거**: arch-guard/autopilot/gemini-cli는 Node.js, crew는 Python
**상세**: 의존성 관리 분산, 에러 처리 패턴 불일치
**위험성**: 환경 설정 복잡도, 크로스 플랫폼 호환성 이슈

**[P2] 이벤트 타입 표준화 부재**
**근거**: SubagentStop(autopilot만), SessionEnd vs Stop 혼용
**상세**: 6개 이벤트 중 절반이 1개 플러그인에서만 사용
**위험성**: 플러그인 간 상호운용성 저하, 학습 곡선 증가

## 4. 공유 리소스 충돌 분석

**파일 시스템 경합**:
- crew: `skills/insight-collector/hooks/observe.py` — 세션 전역 관찰
- arch-guard: `layer-check.mjs` — Write/Edit 도구 사용 시마다 실행
- 잠재적 경합: 두 플러그인 모두 PreToolUse:Edit에서 파일 검사 수행

**성능 오버헤드**: 
- crew PostToolUse "*" matcher → 모든 도구 후 실행
- arch-guard PreToolUse "Write|Edit" → 파일 작업 시마다 검증
- 복합 시: 파일 편집 1회당 최소 3개 hook 실행 (observe.py, check_plan_adherence.py, layer-check.mjs)

## 5. 개선 로드맵

**Phase 1 (P0 대응): crew 복잡도 경감**
**액션**: "*" matcher를 구체적 도구명으로 제한
**기준**: `grep -c "\"matcher\": \"\*\"" plugins/*/hooks/hooks.json` → 0
**효과**: 불필요한 hook 실행 50% 이상 감소

**Phase 2 (P1 대응): 실행 환경 표준화**
**액션**: Node.js 또는 Python 중 하나로 통일. 추천: Node.js (3/4 다수)
**기준**: `fd hooks.json | xargs grep "python3\|node" | cut -d: -f3 | sort | uniq -c`
**효과**: 의존성 관리 단순화, 에러 처리 일관성

**Phase 3 (P2 대응): 이벤트 타입 정리**
**액션**: SubagentStop → Stop 통합, SessionEnd 사용 가이드라인 수립
**기준**: 6개 이벤트 타입 → 4개 이하로 축소
**효과**: 개발자 경험 개선, 문서화 부담 경감

**검증 메트릭**:
```bash
# 리스크 해결 확인
find plugins -name "hooks.json" -exec jq -r '.hooks | keys[]' {} \; | sort | uniq -c
grep -r "async.*true" plugins/*/hooks/ | wc -l
fd hooks.json | xargs grep -c "python3\|node" | awk -F: '{s+=$2} END {print s}'
```