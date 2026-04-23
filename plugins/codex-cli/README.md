# Codex CLI Plugin for Claude Code

Codex MCP 서버를 통해 Claude Code에서 Codex를 네이티브 도구로 사용할 수 있는 플러그인입니다.

## Architecture

`codex mcp-server`를 활용한 MCP 네이티브 통합 플러그인입니다. 기존 CLI 래퍼 커맨드 방식 대신 MCP 도구로 Codex를 직접 호출합니다.

- **MCP 서버**: `codex mcp-server`가 플러그인 로드 시 자동 시작
- **MCP 도구**: `codex`, `codex-reply` 2개의 네이티브 도구 제공
- **CLI 커맨드**: Cloud 전용 기능 2개만 유지 (`cloud`, `apply`)

## MCP Tools

### `codex` - Codex 세션 시작

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | 실행할 프롬프트 |
| `model` | string | No | 모델 선택 (gpt-5.2, gpt-5.2-codex 등) |
| `approval-policy` | string | No | `untrusted`, `on-request`, `on-failure`, `never` |
| `sandbox` | string | No | `read-only`, `workspace-write`, `full-access` |
| `reasoning-effort` | string | No | `low`, `medium`, `high` |

### `codex-reply` - 기존 세션 이어가기

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `thread_id` | string | Yes | 이어갈 세션의 thread ID |
| `message` | string | Yes | 후속 메시지 |

## CLI Commands

### `/codex:cloud` - Cloud 태스크 생성

```
/codex:cloud --env env123 Review this PR
/codex:cloud --env prod-env Deploy the latest changes
```

### `/codex:apply` - Cloud 태스크 결과 적용

```
/codex:apply task_abc123
```

## Migration from codex-cli

| Old Command | New Equivalent |
|-------------|----------------|
| `/codex:ask <q>` | `codex` tool (model: gpt-5.2) |
| `/codex:code <q>` | `codex` tool (model: gpt-5.2-codex) |
| `/codex:review [files]` | `codex` tool (review prompt) |
| `/codex:exec <prompt>` | `codex` tool (all params map directly) |
| `/codex:auto <task>` | `codex` tool (approval-policy: never) |
| `/codex:resume [id]` | `codex-reply` tool (threadId) |
| `/codex:vision <img> <q>` | `codex` tool (image via prompt) |
| `/codex:search <q>` | `codex` tool |
| `/codex:mcp-server` | Auto-started by plugin |
| `/codex:mcp-list` | Removed |
| `/codex:mcp-add` | Removed |
| `/codex:status` | Run `codex auth status` in terminal |
| `/codex:cloud` | Kept as `/codex:cloud` |
| `/codex:apply` | Kept as `/codex:apply` |

## Prerequisites

### 설치

npm 또는 Homebrew 중 편한 방법으로 설치합니다:

```bash
# npm
npm install -g @openai/codex

# Homebrew
brew install codex
```

최소 요구 버전: `codex >= 1.0` (`codex mcp-server` 서브커맨드 지원 필요)

설치 후 PATH 확인:
```bash
which codex
codex --version
```

> **주의**: `codex mcp-server` 서브커맨드를 지원하지 않는 버전을 사용하면 MCP 서버가 자동 시작에 실패하며, Claude Code에서 `codex` / `codex-reply` 도구가 "tool not found"로 표시됩니다. 이 경우 Codex CLI를 최신 버전으로 업데이트하세요.

### 인증

`OPENAI_API_KEY` 환경 변수를 설정하거나, 인터랙티브 로그인 중 한 가지를 선택합니다:

**방법 1 — 환경 변수 (권장)**
```bash
export OPENAI_API_KEY=<your-api-key>
```
셸 프로파일(`.zshrc`, `.bashrc` 등)에 추가하면 영구적으로 적용됩니다.

**방법 2 — 인터랙티브 로그인**
```bash
codex auth login
```

인증 상태 확인: `codex auth status`

## Installation

### From Marketplace

```bash
claude plugins add github:jaebit/context-aware-workflow
claude plugins install codex-cli
```

### Manual Installation

이 플러그인 폴더를 다음 위치에 복사합니다:
```
~/.claude/plugins/codex-cli/
```

Claude Code 재시작 후 자동으로 로드됩니다.

## Notes

- MCP 서버는 플러그인 로드 시 자동으로 시작/종료됩니다
- Cloud 기능은 환경 ID가 필요하며 실험적 기능입니다
- `codex` 도구는 기존 12개 CLI 커맨드의 모든 기능을 대체합니다
