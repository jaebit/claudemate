---
description: "[DEPRECATED v3.0] Use /cw:review --loop --deep instead"
argument-hint: ""
---

# /cw:ultraqa is now /cw:review --loop --deep

This command was consolidated into `/cw:review` in CW v3.0.

**Migration:**
- `/cw:ultraqa` → `/cw:review --loop --deep`
- `/cw:ultraqa --target build` → `/cw:review --build`
- `/cw:ultraqa --target test` → `/cw:review --build --target test`
- `/cw:ultraqa --max-cycles 5` → `/cw:review --loop --max-cycles 5`

This stub will be removed in v3.1.
