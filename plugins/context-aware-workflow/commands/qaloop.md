---
description: "[DEPRECATED v3.0] Use /cw:review --loop instead"
argument-hint: ""
---

# /cw:qaloop is now /cw:review --loop

This command was consolidated into `/cw:review` in CW v3.0.

**Migration:**
- `/cw:qaloop` → `/cw:review --loop`
- `/cw:qaloop --max-cycles 5` → `/cw:review --loop --max-cycles 5`
- `/cw:qaloop --deep` → `/cw:review --loop --deep`
- `/cw:qaloop --severity major` → `/cw:review --loop --severity major`

This stub will be removed in v3.1.
