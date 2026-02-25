# Handoff: codex-cli → codex-harness Migration

**Date:** 2026-02-25
**Commit:** `434b8da` (`feat: replace codex-cli with codex-harness (MCP-native)`)
**Branch:** `master`

---

## What Changed

`plugins/codex-cli/` (14 CLI wrapper commands) was replaced by `plugins/codex-harness/` (MCP server + 2 CLI commands).

### Before

- 14개 Markdown commands가 각각 `codex exec` 를 Bash로 래핑
- 세션 연속성 없음 (fire-and-forget)
- 파라미터 제어가 커맨드별로 분산

### After

- `codex mcp-server`가 plugin.json의 `mcpServers` 필드를 통해 자동 시작
- `codex`, `codex-reply` 2개의 MCP 네이티브 도구가 기존 12개 커맨드를 대체
- thread 기반 세션 연속성 지원 (`codex-reply` + threadId)
- MCP로 제공 불가능한 `cloud`, `apply` 2개만 CLI 커맨드로 유지

---

## File Changes (23 files)

| Action | Path | Note |
|--------|------|------|
| Deleted (17) | `plugins/codex-cli/**` | 전체 디렉토리 삭제 |
| Created | `plugins/codex-harness/.claude-plugin/plugin.json` | `mcpServers` 필드 포함 (repo 최초) |
| Created | `plugins/codex-harness/CLAUDE.md` | 모듈 컨텍스트, MCP 파라미터 레퍼런스 |
| Created | `plugins/codex-harness/README.md` | 한국어, 마이그레이션 테이블 포함 |
| Renamed | `commands/cloud.md` | codex-cli → codex-harness (내용 동일) |
| Renamed | `commands/apply.md` | codex-cli → codex-harness (내용 동일) |
| Updated | `.claude-plugin/marketplace.json` | codex-cli → codex-harness |
| Updated | `README.md` (root) | 테이블, 설치 명령, 하이라이트 섹션 |
| Updated | `CLAUDE.md` (root) | Plugin Types, Context Map |

---

## Command Migration Map

| Old (Removed) | New Equivalent |
|---------------|----------------|
| `/codex:ask` | `codex` tool (model: gpt-5.2) |
| `/codex:code` | `codex` tool (model: gpt-5.2-codex) |
| `/codex:review` | `codex` tool (review prompt) |
| `/codex:exec` | `codex` tool (all params) |
| `/codex:auto` | `codex` tool (approval-policy: never) |
| `/codex:resume` | `codex-reply` tool (threadId) |
| `/codex:vision` | `codex` tool (image via prompt) |
| `/codex:search` | `codex` tool |
| `/codex:mcp-server` | Auto-started by plugin |
| `/codex:mcp-list` | Removed |
| `/codex:mcp-add` | Removed |
| `/codex:status` | `codex auth status` (terminal) |

| Kept | Reason |
|------|--------|
| `/codex:cloud` | `codex cloud` not exposed via MCP |
| `/codex:apply` | `codex apply` not exposed via MCP |

---

## Verification Checklist

```bash
# Orphan reference check (README migration docs only)
grep -r "codex-cli" plugins/ .claude-plugin/ README.md CLAUDE.md

# New structure
ls plugins/codex-harness/.claude-plugin/plugin.json
ls plugins/codex-harness/commands/{cloud,apply}.md

# Old plugin gone
ls plugins/codex-cli/  # Should fail

# Schema validation
python3 -c "
import json
d = json.load(open('plugins/codex-harness/.claude-plugin/plugin.json'))
assert set(d.keys()) <= {'name','version','description','mcpServers'}
"

# Marketplace sync
grep "codex-harness" .claude-plugin/marketplace.json
```

All checks passed at commit time.

---

## Risks & Notes

- **MCP server availability**: `codex mcp-server`가 PATH에 있어야 함. Codex CLI 미설치 시 플러그인 로드 실패 가능
- **첫 mcpServers 사용**: 이 repo에서 `plugin.json`에 `mcpServers`를 사용하는 첫 번째 플러그인
- **Breaking change**: 기존 `/codex:ask`, `/codex:code` 등 12개 슬래시 커맨드가 사라짐. 사용자는 MCP 도구를 직접 호출해야 함

---

## Next Steps (Optional)

- [ ] `codex mcp-server` 실제 동작 확인 (수동 테스트)
- [ ] 사용자 가이드에 MCP 도구 사용법 추가 고려
- [ ] Codex MCP 서버가 `cloud`/`apply` 기능 추가 시 CLI 커맨드 제거 가능
