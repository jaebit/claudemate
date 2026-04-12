# Plugin Hooks Architecture Matrix

## 1. Plugin × Hooks 구현 현황 매트릭스

| Plugin | hooks.json | Hook 항목 수 | 이벤트 유형 | 주요 매처 |
|--------|------------|-------------|-------------|-----------|
| **arch-guard** | ✅ | 4 | SessionStart, PreToolUse, Stop | Write\|Edit |
| **autopilot** | ✅ | 3 | SessionStart, SubagentStop | - |
| **codex-cli** | ❌ | 0 | - | - |
| **crew** | ✅ | 8 | SessionStart, Stop, PreToolUse, PostToolUse, SessionEnd | *, Edit\|Write, Bash |
| **gemini-cli** | ✅ | 1 | SessionStart | - |
| **multi-model-debate** | ❌ | 0 | - | - |
| **worktree** | ❌ | 0 | - | - |

## 2. 이벤트 유형별 집계

**SessionStart (4개 플러그인)**:
- arch-guard: session-init.mjs
- autopilot: verify-build.mjs + session-init.mjs  
- crew: rate_limit_handler.py (async)
- gemini-cli: session-init.mjs

**PreToolUse (2개 플러그인)**:
- arch-guard: Write|Edit 매처로 layer-check + contract-guard
- crew: 3개 매처(*, Edit|Write, Bash)로 관찰, 계획 준수, 검증 실행

**PostToolUse (1개 플러그인)**:
- crew: * 매처로 observe_and_hud.py (async)

**Stop (2개 플러그인)**:
- arch-guard: stop-reminder.mjs
- crew: auto_enforcer.py

**SubagentStop (1개 플러그인)**:
- autopilot: verify-build.mjs

**SessionEnd (1개 플러그인)**:
- crew: session_end.py

## 3. 아키텍처 패턴 및 아웃라이어

**공통 패턴**:
- SessionStart 초기화: 4/4 구현 플러그인이 SessionStart 사용
- Node.js 기반: arch-guard, autopilot, gemini-cli가 .mjs 스크립트 사용  
- Command 타입: 모든 hook이 type: "command" 사용 (prompt 타입 없음)

**플러그인별 특화 패턴**:
- **crew (복합형)**: 6개 이벤트 유형 + async 처리 + timeout 설정
- **arch-guard (가드형)**: PreToolUse로 쓰기 작업 사전 검증
- **autopilot (검증형)**: 빌드 검증을 SessionStart/SubagentStop에서 실행  
- **gemini-cli (최소형)**: SessionStart만으로 최소 초기화

**아웃라이어**:
- crew: 유일한 PostToolUse 사용자, Python 기반, async/timeout 설정
- autopilot: 유일한 SubagentStop 사용자
- 미구현 3개 플러그인: codex-cli, multi-model-debate, worktree

## 4. 요약 통계

- **구현율**: 4/7 플러그인 (57%)
- **총 hook 항목**: 16개  
- **이벤트 유형 다양성**: 6종 (SessionStart, PreToolUse, PostToolUse, Stop, SubagentStop, SessionEnd)
- **가장 활발한 플러그인**: crew (8개 hook, 50%)
- **가장 단순한 플러그인**: gemini-cli (1개 hook)
- **주요 매처 패턴**: *, Edit|Write, Bash, Write|Edit
- **실행 환경**: Node.js (3개), Python (1개)