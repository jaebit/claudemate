---
description: Optimize CLAUDE.md/AGENTS.md files using research-backed classification rules
argument-hint: "[path] [--dry-run] [--report-only]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

# Docs Optimizer

Reduce token overhead in CLAUDE.md/AGENTS.md files using classification rules from arxiv 2602.11988v1.

## Instructions

1. **Determine target files:**
   - If a path argument is provided, use that file directly
   - If no argument, scan the project for all `CLAUDE.md` and `AGENTS.md` files using Glob:
     ```
     Glob pattern: "**/CLAUDE.md" and "**/AGENTS.md"
     ```

2. **Check flags:**
   - `--dry-run`: Run classification and show proposed changes without modifying files
   - `--report-only`: Output current state analysis (line counts, section breakdown) only

3. **Execute the `optimize` skill** on each target file, passing detected flags

4. **Display summary** with before/after line counts and percentage reduction

## Usage Examples

```
/docs-optimizer:optimize                        # All CLAUDE.md/AGENTS.md in project
/docs-optimizer:optimize CLAUDE.md              # Specific file
/docs-optimizer:optimize plugins/ --dry-run     # Preview changes only
/docs-optimizer:optimize --report-only          # Analysis report only
```
