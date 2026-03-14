# Eval: Apply Cloud Task via /codex:apply

**Prompt:** `/codex:apply task_550e8400`

---

## Transcript

### Step 1: Parse the task ID from arguments

The agent receives the `/codex:apply` command and extracts the task ID `task_550e8400` from the argument string per the command spec in `commands/apply.md`.

---

### Step 2: Run `codex apply` via Bash

The command spec specifies `allowed-tools: ["Bash"]`, so the agent invokes the Codex CLI directly.

```
Tool: Bash
Command: codex apply task_550e8400
```

**Output:**

```
Applying task task_550e8400...

Fetching diff from Codex Cloud...
Task status: completed

Applied 2 file(s):

  M src/utils/parser.py  (modified, +18 -4)
  A src/utils/validator.py  (new file, +42)

Changes applied to local workspace.
Use `git diff` to review.
```

---

### Step 3: Display the applied changes

The agent runs `git diff` to show what was applied.

```
Tool: Bash
Command: git diff --stat
```

**Output:**

```
 src/utils/parser.py    | 22 ++++++++++++++++----
 src/utils/validator.py | 42 ++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 60 insertions(+), 4 deletions(-)
```

```
Tool: Bash
Command: git diff
```

**Output (summarized):**

```diff
diff --git a/src/utils/parser.py b/src/utils/parser.py
index a1b2c3d..e4f5g6h 100644
--- a/src/utils/parser.py
+++ b/src/utils/parser.py
@@ -12,10 +12,26 @@ class Parser:
     def parse(self, raw_input: str) -> dict:
-        tokens = raw_input.split(",")
-        return {"tokens": tokens}
+        tokens = raw_input.split(",")
+        validated = self._validate_tokens(tokens)
+        return {"tokens": validated, "count": len(validated)}
+
+    def _validate_tokens(self, tokens: list[str]) -> list[str]:
+        """Filter and normalize tokens using the new validator."""
+        from .validator import TokenValidator
+        v = TokenValidator()
+        return [v.normalize(t) for t in tokens if v.is_valid(t)]

diff --git a/src/utils/validator.py b/src/utils/validator.py
new file mode 100644
index 0000000..f7g8h9i
--- /dev/null
+++ b/src/utils/validator.py
@@ -0,0 +1,42 @@
+"""Token validator module created by Codex Cloud task task_550e8400."""
+
+import re
+
+
+class TokenValidator:
+    """Validates and normalizes parsed tokens."""
+
+    PATTERN = re.compile(r"^[a-zA-Z0-9_\-]+$")
+
+    def is_valid(self, token: str) -> bool:
+        """Return True if token matches the allowed pattern."""
+        token = token.strip()
+        if not token:
+            return False
+        return bool(self.PATTERN.match(token))
+
+    def normalize(self, token: str) -> str:
+        """Strip whitespace and lowercase the token."""
+        return token.strip().lower()
```

---

**Agent final message:**

Task `task_550e8400` has been applied. Two files were changed:

- **`src/utils/parser.py`** -- added token validation via a new `_validate_tokens` method (+18 -4 lines)
- **`src/utils/validator.py`** -- new file with a `TokenValidator` class for filtering and normalizing tokens (+42 lines)

The changes are unstaged. Run `git diff` to review the full diff, then commit when ready.

---

## Evaluation Notes

| Criterion | Result |
|-----------|--------|
| Used Bash tool (not MCP tool) for `codex apply` | PASS |
| Command includes `codex apply` | PASS |
| Command includes task ID `task_550e8400` | PASS |
| Displayed applied changes to user | PASS |
| Did not attempt MCP tool for CLI-only feature | PASS |

**Verdict:** The agent correctly parsed the task ID from the `/codex:apply task_550e8400` invocation, ran `codex apply task_550e8400` via Bash (the only allowed tool for this command), and displayed the resulting diff to the user. This matches the command spec in `commands/apply.md` and the constraint in `CLAUDE.md` that CLI commands are reserved for features not available via MCP.
