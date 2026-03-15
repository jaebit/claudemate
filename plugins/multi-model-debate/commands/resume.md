---
description: "Resume an interrupted debate from the last completed round"
argument-hint: "[debate-dir]"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Agent"]
---

# Debate Resume

Resume an interrupted multi-model debate from its last completed checkpoint.

## Instructions

1. **Locate debate state:**
   - If `debate-dir` argument provided, use that path directly
   - Otherwise, find the most recent debate: `Glob pattern: .debate/*/state.json`, pick latest by timestamp prefix

2. **Read and validate `state.json`:**
   - Confirm status is not `"completed"` (if completed, inform user and stop)
   - Identify `lastCompletedPhase` and `currentRound`

3. **Resume from next phase:**
   - If interrupted during ROUND dispatch: re-run that round (agents are idempotent)
   - If interrupted during SYNTHESIS: re-run synthesis for that round
   - If interrupted during FINAL CONSENSUS: re-run final consensus

4. **Execute the `debate-orchestration` skill** with resume parameters:
   - Pass existing debate-id, output directory, resume-from phase/round

## Usage Examples

```
/debate:resume
/debate:resume .debate/20260315-143022-rest-vs-graphql
```
