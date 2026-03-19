---
name: debate-resume
description: "Resume an interrupted multi-model debate from the last completed round. Use when the user invokes /debate:resume to continue a previously started debate."
argument-hint: "[debate-dir]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Agent
---

# Debate Resume

Resume an interrupted multi-model debate from its last completed checkpoint.

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
