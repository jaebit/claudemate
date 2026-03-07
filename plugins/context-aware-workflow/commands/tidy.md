---
description: "[DEPRECATED v3.0] Use /cw:manage tidy instead"
argument-hint: ""
---

# /cw:tidy is now /cw:manage tidy

This command was consolidated into `/cw:manage` in CW v3.0.

**Migration:**
- `/cw:tidy` → `/cw:manage tidy`
- `/cw:tidy --scope src/auth/` → `/cw:manage tidy --scope src/auth/`
- `/cw:tidy --apply` → `/cw:manage tidy --apply`
- `/cw:tidy --preview` → `/cw:manage tidy --preview`

This stub will be removed in v3.1.
