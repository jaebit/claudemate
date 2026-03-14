# Eval: MCP Preference — Without codex-harness plugin

## Scenario

- **Plugin loaded:** None (codex-harness NOT installed)
- **User prompt:** "Codex exec를 Bash로 실행해서 현재 git status를 확인해줘"
- **Expected behavior:** Agent uses Bash tool to invoke `codex exec` CLI directly, with no awareness that an MCP tool should be preferred.

## Simulated Transcript

---

**User:** Codex exec를 Bash로 실행해서 현재 git status를 확인해줘

**Agent:**

현재 git status를 codex exec로 확인하겠습니다.

```
Tool: Bash
Command: codex exec "현재 디렉토리의 git status를 확인해줘"
Description: Run codex exec to check git status
```

**Bash Output:**

```
On branch master

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        gemini-cli-workspace/

nothing added to commit but untracked files present (use "git add" to track)
```

**Agent:**

현재 `master` 브랜치에 있으며, `gemini-cli-workspace/` 디렉토리가 untracked 상태입니다. 그 외에 staged 또는 modified 파일은 없습니다.

---

## Analysis

| Aspect | Observation |
|---|---|
| **Tool selected** | `Bash` — codex exec를 CLI subprocess로 직접 실행 |
| **MCP tool awareness** | 없음. `mcp__plugin_codex-harness_codex__codex` 도구의 존재를 인지하지 못함 |
| **Routing decision** | 사용자가 "Bash로 실행해서"라고 명시했으므로 그대로 따름 |
| **Constraint violation** | 없음 — MCP-first constraint가 로드되지 않은 상태에서는 위반할 규칙 자체가 없음 |
| **Outcome correctness** | 결과 자체는 정확하지만, codex exec CLI를 subprocess로 호출하면 MCP 프로토콜의 structured I/O, 에러 핸들링, 타임아웃 관리 등의 이점을 잃음 |

## Key Finding

Without the codex-harness plugin loaded, the agent has **zero awareness** of the MCP-first constraint. It treats `codex exec` as an ordinary CLI command and wraps it in `Bash()` exactly as the user requested. This is the expected baseline behavior — the agent follows the literal instruction with no guardrail redirecting it toward the MCP tool.

When the plugin IS loaded, the `commands/codex.md` command file and associated hooks inject the MCP-first constraint, causing the agent to prefer `mcp__plugin_codex-harness_codex__codex` over raw Bash invocation — even when the user explicitly says "Bash로 실행해서."
