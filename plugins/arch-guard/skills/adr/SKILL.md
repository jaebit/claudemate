---
name: adr
description: >
  This skill should be used when the user asks "create ADR", "document design decision",
  "adr", "record architecture decision", "why did we decide this", or wants to create
  an Architecture Decision Record documenting a design choice with context, rationale,
  alternatives, and consequences.
argument-hint: "<decision-title> e.g. \"Why we chose PostgreSQL JSONB\""
user_invocable: true
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---

# /adr — Architecture Decision Record

Creates an ADR documenting a design decision using the Michael Nygard template format.

## Usage

```
/adr "Why we chose PostgreSQL JSONB for state storage"
/adr "Switching from REST to gRPC for inter-service communication"
```

## Reference

Read `arch-guard.json` to determine the ADR directory path from `config.docs.adr_dir`. Default: `docs/adr/`.

## Procedure

### Step 1: Determine ADR Directory

1. Read `arch-guard.json` for `config.docs.adr_dir` (default: `docs/adr/`)
2. Create the directory if it doesn't exist
3. Find existing ADRs to determine the next number:

```bash
ls {adr_dir}/ADR-*.md 2>/dev/null | sort | tail -1
```

Auto-assign the next number. Start at ADR-001 if none exist.

### Step 2: Reference Architecture Docs

If `config.docs.architecture` is set, read the referenced architecture document for relevant context.

Also check existing ADRs for related decisions.

### Step 3: Generate ADR Draft

Create `{adr_dir}/ADR-{number}-{slug}.md`:

### ADR Standard Format (Michael Nygard)

```markdown
# ADR-{number}: {title}

- **Status**: Accepted | Proposed | Deprecated | Superseded by ADR-XXX
- **Date**: {today's date}
- **Deciders**: {ask the user}

## Context

{Background for this decision. What problem are we solving?}

## Decision

{What was decided. Clear and concise.}

## Rationale

{Why this decision was made. Compare with alternatives.}

### Alternatives Considered

| Alternative | Pros | Cons | Rejection Reason |
|------------|------|------|-----------------|
| ... | ... | ... | ... |

## Consequences

{Impact of this decision. Both positive and negative.}

## Related

- arch-guard.json layer rules: {relevant layers}
- Architecture docs: {relevant sections}
- Related ADRs: {if any}
```

### Step 4: User Review

Present the draft and ask for corrections or additions.

### Step 5: Write and Report

After confirmation, write the file and report:

```
## ADR Created

- File: {adr_dir}/ADR-{number}-{slug}.md
- Status: {status}
- Related: {related docs}

### Next Steps
- /arch-check — verify the decision doesn't conflict with existing code
- /scaffold {module} — if the decision requires new project structure
```
