---
description: "[DEPRECATED v3.0] Use /cw:parallel --team instead"
argument-hint: ""
---

# /cw:team is now /cw:parallel --team

This command was consolidated into `/cw:parallel` in CW v3.0.

**Migration:**
- `/cw:team create <name>` → `/cw:parallel --team create <name>`
- `/cw:team assign` → `/cw:parallel --team assign`
- `/cw:team status` → `/cw:parallel --team status`
- `/cw:team gate` → `/cw:parallel --team gate`
- `/cw:team synthesize` → `/cw:parallel --team synthesize`
- `/cw:team cleanup` → `/cw:parallel --team cleanup`

This stub will be removed in v3.1.
