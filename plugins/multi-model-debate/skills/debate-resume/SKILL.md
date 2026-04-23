---
name: debate-resume
description: "Resume an interrupted multi-model debate from the last completed round. Use when the user invokes /debate:resume to continue a previously started debate."
argument-hint: "[debate-dir]"
user_invocable: true
disable-model-invocation: true
---

# Debate Resume

Resume an interrupted multi-model debate from its last completed checkpoint.
Round dispatch runs inline (MCP accessible), synthesis/consensus delegates to `debate-orchestration` (fork).

## Current Debate State

- Latest debate directory: !`ls -1dt .debate/*/ 2>/dev/null | head -1 || echo "No debates found"`
- Latest state: !`cat $(ls -1t .debate/*/state.json 2>/dev/null | head -1) 2>/dev/null || echo "No active debate state"`

## Instructions

1. **Locate debate state:**
   - If `debate-dir` argument provided, use that path directly
   - Otherwise, use the latest debate info injected above

2. **Validate state:**
   - Confirm status is not `"completed"` (if completed, inform user and stop)
   - Identify `lastCompletedPhase` and `currentRound`

3. **Verify prerequisites** (same as debate-start):
   - Check Codex MCP tool: ToolSearch로 `mcp__plugin_codex-cli_codex__codex` 확인
   - If unavailable → update `state.json` with `codex_mode: "cli_fallback"`
   - Check Gemini CLI: `which gemini`

4. **Resume from next phase:**

   | `lastCompletedPhase` | Resume Action |
   |---|---|
   | `setup` or `synthesis-{N}` (unresolved remain) | Dispatch next round inline (step 5) |
   | `round-{N}` | Execute `debate-orchestration` for synthesis |
   | `synthesis-{N}` + all resolved or max rounds | Execute `debate-orchestration` for final consensus |

5. **Round dispatch** (inline — same pattern as debate-start step 5):

   Dispatch all 3 agents **in parallel** (single message, 3 tool calls):
   - **Codex**: MCP tool (or CLI fallback). If `state.json workers.codex.thread_id` exists, use `codex-reply` with threadId.
   - **Claude**: Agent tool (sub-agent)
   - **Gemini**: Agent tool → sub-agent runs `gemini -p "..."` via Bash

   Round 2+ uses cross-examination prompts with opposing arguments from previous synthesis.

   **Save results:** `round-{N}-claude.md`, `round-{N}-codex.md`, `round-{N}-gemini.md`
   **Update state.json:** `currentRound: N`, `lastCompletedPhase: "round-N"`

6. **Continue the loop:**
   - After round dispatch → execute `debate-orchestration` for synthesis
   - Read synthesis result → check if more rounds needed
   - If round count exceeds 3 → ask user before continuing
   - When all resolved or max rounds → execute `debate-orchestration` for final consensus

## Codex CLI Fallback

Same rules as debate-start:
- `codex exec -s read-only "<prompt>"` via Bash, output captured and saved via Write tool
- No shell redirection — Windows compatible
- Round 2+: include previous context in prompt directly (no threadId continuity)

## Usage Examples

```
/debate:resume
/debate:resume .debate/20260315-143022-rest-vs-graphql
```
