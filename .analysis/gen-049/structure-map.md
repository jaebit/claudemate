# Claude Mate Plugins Structure Map

**Analysis Date**: 2026-04-11  
**Total Plugins**: 7  
**Analysis Scope**: plugins/ directory structure and architectural patterns

## 1. Plugin × 구성요소 매트릭스

| Plugin | commands | agents | skills | hooks | schemas | tests | _shared | docs | README | CLAUDE.md |
|--------|----------|--------|---------|-------|---------|-------|---------|------|--------|-----------|
| arch-guard | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| autopilot | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| codex-cli | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| crew | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| gemini-cli | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| multi-model-debate | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| worktree | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |

## 2. plugin.json 스키마 준수 여부

**Critical Finding**: **모든 플러그인에서 plugin.json 파일이 누락됨**

- arch-guard: ❌ plugin.json 없음
- autopilot: ❌ plugin.json 없음  
- codex-cli: ❌ plugin.json 없음
- crew: ❌ plugin.json 없음
- gemini-cli: ❌ plugin.json 없음
- multi-model-debate: ❌ plugin.json 없음
- worktree: ❌ plugin.json 없음

**스키마 위반 현황**: Golden Rules에 따르면 plugin.json은 필수 파일이며 `name`, `version`, `description`, `mcpServers` 필드만 허용되나, 모든 플러그인에서 해당 파일이 존재하지 않음.

## 3. 아키텍처 패턴 분석

### 공통 패턴 (5개 이상에서 발견)

1. **README.md 표준화**: 7/7 플러그인 (100%) - 모든 플러그인이 문서화를 위한 README.md 보유
2. **CLAUDE.md 프로젝트 지침**: 6/7 플러그인 (86%) - arch-guard 제외한 모든 플러그인에서 Claude 전용 지침 파일 보유
3. **Skills 중심 아키텍처**: 5/7 플러그인 (71%) - 대부분 플러그인이 skills/ 디렉토리 활용

### 이상치 (Outlier) 패턴

1. **Commands 중심**: codex-cli, gemini-cli만 commands/ 디렉토리 활용 (CLI 도구 특성)
2. **Full-Stack 플러그인**: crew만 모든 구성요소(agents, skills, hooks, schemas, tests, _shared, docs) 보유
3. **Hooks 활용**: arch-guard, autopilot, crew, gemini-cli만 hooks/ 디렉토리 보유
4. **테스트 커버리지**: crew만 tests/ 디렉토리 보유
5. **Minimal 플러그인**: multi-model-debate, worktree는 skills/만 보유 (최소 구성)

### 특이사항

- **crew**: 유일한 "kitchen-sink" 플러그인으로 모든 가능한 구성요소 포함
- **arch-guard**: 유일하게 CLAUDE.md 없는 플러그인
- **codex-cli, gemini-cli**: 유일하게 commands/ 중심의 CLI 플러그인
- **crew**: skills/ 내부에 nested hooks/ 구조 (`skills/insight-collector/hooks`) 보유

## 4. 요약 통계

- **총 플러그인 수**: 7개
- **평균 구성요소 수**: 3.4개/플러그인
- **가장 복잡한 플러그인**: crew (8개 구성요소)
- **가장 단순한 플러그인**: multi-model-debate, worktree (2개 구성요소)
- **plugin.json 준수율**: 0% (모든 플러그인에서 누락)
- **README.md 보유율**: 100%
- **CLAUDE.md 보유율**: 86%

### 구성요소별 채택률

| 구성요소 | 채택 플러그인 수 | 채택률 |
|----------|------------------|--------|
| README.md | 7 | 100% |
| CLAUDE.md | 6 | 86% |
| skills | 5 | 71% |
| hooks | 4 | 57% |
| _shared | 3 | 43% |
| commands | 2 | 29% |
| agents | 2 | 29% |
| docs | 2 | 29% |
| schemas | 1 | 14% |
| tests | 1 | 14% |

**핵심 발견**: claudemate 플러그인 생태계는 Skills-driven 아키텍처를 따르며, 문서화는 우수하나 plugin.json 표준 준수가 전혀 이루어지지 않고 있음.