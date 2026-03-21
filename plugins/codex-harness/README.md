# Codex Harness Plugin for Claude Code

Codex MCP 서버를 통해 Claude Code에서 Codex를 네이티브 도구로 사용할 수 있는 플러그인입니다.

## Architecture

기존 codex-cli 플러그인은 14개의 CLI 래퍼 커맨드로 구성되어 있었습니다. codex-harness는 `codex mcp-server`를 활용하여 MCP 네이티브 통합으로 전환합니다.

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

- Codex CLI가 설치되어 있어야 합니다
- PATH에 `codex` 명령어가 등록되어 있어야 합니다
- `codex mcp-server` 지원 버전 필요

## Installation

```bash
claude plugins add github:jaebit/claudemate
claude plugins install codex-harness
```

## Notes

- MCP 서버는 플러그인 로드 시 자동으로 시작/종료됩니다
- Cloud 기능은 환경 ID가 필요하며 실험적 기능입니다
- `codex` 도구는 기존 12개 CLI 커맨드의 모든 기능을 대체합니다
