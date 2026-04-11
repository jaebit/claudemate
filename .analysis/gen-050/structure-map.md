# Plugin Structure Analysis Map (gen-050)

## 1. Plugin × 구성요소 매트릭스

| Plugin | `.claude-plugin/` | `commands/` | `agents/` | `skills/` | `hooks/` | `schemas/` | `tests/` | `_shared/` | `docs/` | `README.md` | `CLAUDE.md` |
|--------|------------------|-------------|-----------|-----------|----------|------------|----------|------------|---------|-------------|-------------|
| arch-guard | ✓ | ❌ | ✓ (1) | ✓ (12) | ✓ | ❌ | ❌ | ✓ | ✓ | ✓ | ❌ |
| autopilot | ✓ | ❌ | ❌ | ✓ (1) | ✓ | ❌ | ❌ | ✓ | ❌ | ✓ | ✓ |
| codex-cli | ✓ | ✓ (2) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✓ | ✓ |
| crew | ✓ | ❌ | ✓ (8) | ✓ (16) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| gemini-cli | ✓ | ✓ (5) | ❌ | ❌ | ✓ | ❌ | ❌ | ❌ | ❌ | ✓ | ✓ |
| multi-model-debate | ✓ | ❌ | ❌ | ✓ (3) | ❌ | ❌ | ❌ | ❌ | ❌ | ✓ | ✓ |
| worktree | ✓ | ❌ | ❌ | ✓ (3) | ❌ | ❌ | ❌ | ❌ | ❌ | ✓ | ✓ |

**구성요소 개수 요약:**
- **Total Skills**: 35 (arch-guard: 12, crew: 16, autopilot: 1, multi-model-debate: 3, worktree: 3)
- **Total Agents**: 9 (arch-guard: 1, crew: 8)
- **Total Commands**: 7 (codex-cli: 2, gemini-cli: 5)

## 2. plugin.json 스키마 준수 현황

**발견 경로**: 모든 플러그인이 `.claude-plugin/plugin.json` 경로 사용 (7/7 = 100%)

### 2.1. 완전 준수 (허용 필드만 사용)
```yaml
# 허용 필드: name, version, description, mcpServers
arch-guard: ✓ (name, version, description)
autopilot: ✓ (name, version, description)  
gemini-cli: ✓ (name, version, description)
multi-model-debate: ✓ (name, version, description)
worktree: ✓ (name, version, description)
```

### 2.2. mcpServers 필드 사용
```yaml
codex-cli: ✓ (name, version, description, mcpServers)
# mcpServers.codex: command="codex", args=["mcp-server"]
```

### 2.3. crew 플러그인 특이사항
```yaml
crew: ✓ (name, version, description)
# 가장 복잡한 플러그인이지만 스키마 완전 준수
```

**스키마 준수율**: 7/7 = 100%  
**위반 필드 발견**: 0건

## 3. 아키텍처 패턴 분석

### 3.1. 공통 패턴 (Common Patterns)

#### Pattern A: 기본 플러그인 구조
```
.claude-plugin/plugin.json (필수)
README.md (100% 채택)
CLAUDE.md (6/7 = 85.7% 채택)
```

#### Pattern B: CLI 명령 중심 플러그인
```
commands/ 디렉토리
hooks/session-init.mjs
```
- **적용 플러그인**: codex-cli, gemini-cli

#### Pattern C: 에이전트 기반 플러그인
```
agents/ 디렉토리
skills/ 다수
hooks/ 디렉토리  
_shared/ 디렉토리
```
- **적용 플러그인**: arch-guard, crew

#### Pattern D: 스킬 전용 플러그인
```
skills/ 소수 (1-3개)
최소한의 구조
```
- **적용 플러그인**: autopilot, multi-model-debate, worktree

### 3.2. 이상치 (Outliers)

#### crew 플러그인 (복잡도 최고)
- **특징**: 8 agents, 16 skills, 전체 테스트 스위트, 광범위한 문서화
- **고유 구성**: schemas/ 디렉토리, tests/ 디렉토리, hooks/scripts/ Python 모듈
- **복잡도 지표**: 총 103 파일 (전체 플러그인 중 압도적)

#### codex-cli 플러그인 (MCP 통합)
- **특징**: mcpServers 필드 유일 사용, 외부 도구 의존성
- **구조적 특이점**: skills/ 없음, agents/ 없음 (commands만 제공)

## 4. 요약 통계

### 4.1. 전체 플러그인 현황
```yaml
총 플러그인 수: 7
.claude-plugin/plugin.json 보유: 7/7 (100%)
스키마 준수: 7/7 (100%)
README.md 보유: 7/7 (100%)  
CLAUDE.md 보유: 6/7 (85.7%)
```

### 4.2. 구성요소 분포
```yaml
skills 보유 플러그인: 5/7 (71.4%)
agents 보유 플러그인: 2/7 (28.6%)
commands 보유 플러그인: 2/7 (28.6%)
hooks 보유 플러그인: 3/7 (42.9%)
docs 보유 플러그인: 2/7 (28.6%)
tests 보유 플러그인: 1/7 (14.3%)
```

### 4.3. 복잡도 계층
```yaml
High Complexity (50+ files): crew (103 files)
Medium Complexity (10-49 files): arch-guard (25 files)
Low Complexity (< 10 files): autopilot (8), gemini-cli (8), codex-cli (5), worktree (5), multi-model-debate (4)
```

### 4.4. 도메인별 분류
```yaml
Development Pipeline: crew, autopilot, arch-guard
AI Integration: multi-model-debate, gemini-cli
CLI Tools: codex-cli
Git Utilities: worktree
```

**분석 완료 시각**: 2026-04-11 18:03 KST  
**분석 기준**: domain-expert v1.2.0 (숨김 디렉토리 포함 완전 탐색)