---
name: optimize
description: "Optimize a CLAUDE.md/AGENTS.md file using research-backed classification rules (arxiv 2602.11988v1). Use this skill whenever the user wants to reduce token overhead, clean up agent instructions, shrink or audit CLAUDE.md/AGENTS.md bloat, compress documentation for AI agents, or improve instruction file efficiency — even if they don't say 'optimize' explicitly."
argument-hint: "[path] [--dry-run] [--report-only]"
disable-model-invocation: true
context: fork
agent: general-purpose
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Docs Optimization Skill

Apply classification rules from arxiv 2602.11988v1 to reduce token overhead while preserving agent-critical information.

For detailed classification rules, migration strategies, and table formats, see [reference.md](reference.md).

## Target Files

- Available CLAUDE.md files: !`find . -name "CLAUDE.md" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -20 || echo "None found"`
- Available AGENTS.md files: !`find . -name "AGENTS.md" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -20 || echo "None found"`

## Arguments

- If a path argument is provided, use that file directly
- If no argument, use the file list injected above
- `--dry-run`: Run classification and show proposed changes without modifying files
- `--report-only`: Output current state analysis (line counts, section breakdown) only

## 5-Step Process

### Step 1: SCAN
- Read the target file (use the Read tool — line numbers are included automatically)
- Note total line count from the last line number
- List each `##` section with its line count

### Step 2: CLASSIFY
For each section, apply classification rules from [reference.md](reference.md). Output a classification table.

If `--report-only` flag: stop here and display the table.

### Step 3: PLAN
For each non-HIGH-VALUE section, assign a migration strategy. Calculate expected final line count.

If `--dry-run` flag: stop here and display the plan.

### Step 4: REWRITE
- Keep all HIGH-VALUE sections verbatim
- Apply migration strategies to other sections
- Merge scattered constraints into a single section
- Compress verbose wording (remove filler, use tables over paragraphs)
- Write the optimized file

### Step 5: VERIFY
- Confirm pointer targets exist (Glob/Read check)
- Run project tests if available (`pytest`, `npm test`, etc.)
- Display before/after comparison:
  ```
  Before: N lines | After: M lines | Reduction: X%
  ```
