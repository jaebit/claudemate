# Eval: Session Continuity — Without codex-harness MCP Tools

## Scenario

**User prompt:** "Codex에게 Python으로 fibonacci 함수를 작성해달라고 해줘. 그 다음에 같은 세션에서 memoization 버전으로 개선해달라고 이어서 요청해줘"

**Translation:** "Ask Codex to write a fibonacci function in Python. Then, in the same session, ask it to improve it to a memoization version."

**Environment:** Claude Code agent with NO codex-harness plugin loaded. No `mcp__plugin_codex-harness_codex__codex` or `mcp__plugin_codex-harness_codex__codex-reply` tools available.

---

## Simulated Transcript

### Agent Reasoning (internal)

> The user wants me to delegate to "Codex" — OpenAI's Codex agent. I don't have a
> direct integration with Codex, but I can try running it via the CLI if it's
> installed. Let me check if `codex` is available as a command-line tool.

---

### Tool Call 1: Check if codex CLI exists

```
Bash: which codex || echo "NOT_FOUND"
```

**Output:**
```
/usr/local/bin/codex
```

### Agent Reasoning (internal)

> Good, `codex` CLI is installed. I'll use `codex exec` to send the first prompt.
> The user wants session continuity — "같은 세션에서" means "in the same session."
> I'm not sure how to maintain a persistent session with codex via CLI.
> Let me try sending the first request and see what happens.

---

### Tool Call 2: First request — write fibonacci

```
Bash: codex exec "Write a Python fibonacci function"
```

**Output:**
```
Here's a simple Python fibonacci function:

def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

# Example usage
for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")
```

### Agent Reasoning (internal)

> OK, the first request worked. Now the user wants me to continue "in the same
> session" and ask for a memoization improvement. But `codex exec` is stateless —
> each invocation is a fresh context. There's no `--session-id` or `--thread-id`
> flag I'm aware of that would link two calls together.
>
> I have two options:
> 1. Run another `codex exec` with full context (paste the previous code into the prompt)
> 2. Just make the call and hope codex remembers (it won't — it's stateless)
>
> I'll try option 1 — embed the previous output into the follow-up prompt to
> simulate continuity.

---

### Tool Call 3: Second request — memoization (attempt at continuity)

```
Bash: codex exec "I previously wrote this fibonacci function:

def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

Please improve it to use memoization for better performance."
```

**Output:**
```
Here's the improved fibonacci function with memoization:

def fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 0:
        memo[n] = 0
    elif n == 1:
        memo[n] = 1
    else:
        memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]

# Or using functools.lru_cache:
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)
```

---

### Agent's Final Response to User

> Codex에게 두 번 요청을 보냈습니다.
>
> 첫 번째로 기본 재귀 fibonacci 함수를 작성했고, 두 번째로 memoization 버전으로
> 개선했습니다.
>
> 다만 한 가지 알려드릴 점이 있습니다: `codex exec`는 각 호출이 독립적인
> stateless 명령이라 실제로는 "같은 세션"을 유지할 수 없었습니다. 대신 이전
> 코드를 두 번째 프롬프트에 직접 포함시켜서 맥락을 전달했습니다. 진정한 세션
> 연속성이 필요하다면 Codex의 대화형 모드나 API를 통한 thread 관리가
> 필요합니다.

---

## Analysis

### Observed Behavior

| Aspect | Result |
|---|---|
| **Delegation to Codex** | Partially successful — used `codex exec` CLI |
| **Session continuity** | Failed — no mechanism to link two calls |
| **Workaround attempted** | Manual context injection (pasted previous code into prompt) |
| **Thread ID tracking** | None — agent has no concept of `thread_id` |
| **Number of Bash calls** | 3 (1 check + 2 independent `codex exec`) |
| **User intent fulfilled** | Partially — got both outputs but no true session |

### Key Failures

1. **No session continuity:** `codex exec` is stateless. Each call starts a fresh context. The agent correctly identified this limitation but had no solution beyond manual context stuffing.

2. **No `codex-reply` equivalent:** Without the MCP tool `codex-reply`, there is no way to send a follow-up message to an existing Codex thread. The agent doesn't even know this concept exists.

3. **Manual context injection is fragile:** Pasting previous output into the next prompt works for trivial cases but breaks down for:
   - Long conversations (prompt length limits)
   - Complex state (file edits, tool usage within Codex)
   - Multi-turn reasoning chains

4. **Alternative path — agent writes code itself:** A common failure mode is the agent deciding "I'll just write the code myself instead of delegating to Codex." This satisfies the functional requirement but ignores the user's explicit request to use Codex as the delegate.

### What the codex-harness Plugin Would Provide

With the codex-harness MCP tools loaded:

```
# First call — returns a thread_id
mcp__plugin_codex-harness_codex__codex(
  prompt="Write a Python fibonacci function"
)
→ { thread_id: "abc-123", response: "..." }

# Second call — continues the SAME thread
mcp__plugin_codex-harness_codex__codex-reply(
  thread_id="abc-123",
  prompt="Now improve it to use memoization"
)
→ { thread_id: "abc-123", response: "..." }
```

This gives true session continuity: Codex retains full context of the previous exchange, including any reasoning, code, and tool calls it performed.

### Scoring

| Criterion | Score | Notes |
|---|---|---|
| Task completion | 2/5 | Both outputs obtained, but no true session |
| Session continuity | 0/5 | Completely absent |
| Correct tool usage | 1/5 | Used CLI fallback, not purpose-built MCP tools |
| User intent alignment | 2/5 | Functional result OK, delegation model broken |
| **Overall** | **1.25/5** | Manual workaround cannot replace proper session management |
