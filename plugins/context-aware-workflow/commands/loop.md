---
description: "[DEPRECATED v3.0] Use /cw:go --max-iterations instead"
argument-hint: ""
---

# /cw:loop is now /cw:go

This command was consolidated into `/cw:go` in CW v3.0.

**Migration:**
- `/cw:loop "task"` → `/cw:go "task"`
- `/cw:loop --max-iterations 30` → `/cw:go --max-iterations 30`
- `/cw:loop --continue` → `/cw:go --continue`
- `/cw:loop --no-reflect` → `/cw:go --skip-reflect`

This stub will be removed in v3.1.
