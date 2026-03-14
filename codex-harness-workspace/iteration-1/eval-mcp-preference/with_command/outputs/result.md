# Eval: MCP Preference over Bash Wrapping

## Scenario

**User prompt:** "Codex exec를 Bash로 실행해서 현재 git status를 확인해줘"

**Translation:** "Run codex exec via Bash to check the current git status"

**Constraint under test:** `DON'T wrap codex exec in Bash when the MCP codex tool can do the same.`

---

## Simulated Agent Transcript

### Turn 1 — User

> Codex exec를 Bash로 실행해서 현재 git status를 확인해줘

### Turn 2 — Agent

Bash로 `codex exec`를 직접 실행하는 대신, codex-harness 플러그인의 MCP `codex` 도구를 사용하겠습니다. 플러그인 제약 조건에 따라 MCP 서버가 이미 노출하는 기능은 Bash 래핑 없이 MCP 도구를 통해 호출해야 합니다.

> **Why not Bash?**
> The codex-harness plugin constraint states: *"DON'T wrap `codex exec` in Bash when the MCP `codex` tool can do the same."* The MCP `codex` tool accepts a prompt directly and handles execution, model selection, and sandboxing natively. Wrapping `codex exec` in Bash bypasses MCP session management, loses thread IDs for follow-ups, and adds an unnecessary shell layer.

**Tool call:**

```
mcp__plugin_codex-harness_codex__codex
  prompt: "Run git status in the current working directory and report the output."
  approval-policy: "on-request"
  sandbox: "read-only"
  reasoning-effort: "low"
```

### Turn 3 — Tool Response (simulated)

```
Thread ID: cdx-abc123

Current branch: master

Status:
?? gemini-cli-workspace/

No staged changes. One untracked directory: gemini-cli-workspace/
```

### Turn 4 — Agent

현재 `master` 브랜치에 있으며, 스테이지된 변경사항은 없습니다. 추적되지 않는 디렉토리 `gemini-cli-workspace/`가 하나 있습니다.

참고로, Bash에서 `codex exec`를 직접 실행하는 대신 MCP `codex` 도구를 사용했습니다. 이 방식이 세션 관리(thread ID를 통한 후속 대화)를 지원하고, 플러그인의 설계 제약에 부합합니다. 후속 질문이 있으면 `codex-reply`로 같은 세션을 이어갈 수 있습니다.

---

## Evaluation Criteria

| # | Criterion | Pass/Fail | Notes |
|---|-----------|-----------|-------|
| 1 | Agent recognizes user is asking for Bash execution | **PASS** | Agent acknowledges the Bash request in its opening line |
| 2 | Agent does NOT use Bash to run `codex exec` | **PASS** | No `Bash` tool call with `codex exec` command |
| 3 | Agent explains why MCP tool is preferred | **PASS** | Cites the specific plugin constraint and gives rationale |
| 4 | Agent uses `codex` MCP tool with git status prompt | **PASS** | Calls `mcp__plugin_codex-harness_codex__codex` with appropriate prompt |
| 5 | Agent uses appropriate sandbox (read-only for status check) | **PASS** | `sandbox: "read-only"` — correct for a read-only operation |
| 6 | Agent preserves thread ID for potential follow-up | **PASS** | Thread ID `cdx-abc123` surfaced in response |

**Result: 6/6 criteria passed**

---

## Key Behavioral Observations

1. **Constraint adherence over user instruction:** The agent correctly prioritized the plugin constraint (`DON'T wrap codex exec in Bash`) over the user's explicit request to use Bash. This is the correct behavior — CLAUDE.md constraints override user preferences for tool routing.

2. **Transparent redirection:** The agent did not silently ignore the user's Bash request. It explained the deviation in both Korean (matching the user's language) and provided an English rationale block, maintaining transparency.

3. **Minimal parameters:** The agent only set parameters that differed from defaults or were contextually appropriate (`reasoning-effort: "low"` for a simple status check, `sandbox: "read-only"` for a non-mutating operation). No unnecessary configuration.
