---
description: "[DEPRECATED v3.0] Use /cw:parallel instead"
argument-hint: ""
---

# /cw:swarm is now /cw:parallel

This command was consolidated into `/cw:parallel` in CW v3.0.

**Migration:**
- `/cw:swarm "task1" "task2"` → `/cw:parallel "task1" "task2"`
- `/cw:swarm --workers 4` → `/cw:parallel --workers 4`
- `/cw:swarm --from-plan` → `/cw:parallel --from-plan`
- `/cw:swarm --merge` → `/cw:parallel --merge`

This stub will be removed in v3.1.
