---
description: "[DEPRECATED v3.0] Use /cw:go instead"
argument-hint: ""
---

# /cw:start is now /cw:go

This command was consolidated into `/cw:go` in CW v3.0.

**Migration:**
- `/cw:start "task"` → `/cw:go "task"`
- `/cw:start --from-plan` → `/cw:go --from-plan`
- `/cw:start --plan-file <path>` → `/cw:go --from-plan`

This stub will be removed in v3.1.
