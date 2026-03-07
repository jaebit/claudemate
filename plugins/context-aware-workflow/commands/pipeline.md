---
description: "[DEPRECATED v3.0] Use /cw:go instead"
argument-hint: ""
---

# /cw:pipeline is now /cw:go

This command was consolidated into `/cw:go` in CW v3.0.

**Migration:**
- `/cw:pipeline --stages "plan,build,review"` → `/cw:go "task"`
- `/cw:pipeline --resume` → `/cw:go --continue`
- `/cw:pipeline --from build` → `/cw:go --continue`

This stub will be removed in v3.1.
