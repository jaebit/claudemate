---
name: plan-detector
description: Detects Plan Mode completion and suggests starting CAW workflow. Use when ExitPlanMode is called or when a plan file is created/updated in the configured plansDirectory (resolves from settings).
allowed-tools: Read, Glob, AskUserQuestion
---

# Plan Detector

Automatically detect Plan Mode completion and offer to start a structured CAW workflow.

## Event Hook

| Event | Action | Priority | Condition |
|-------|--------|----------|-----------|
| ExitPlanMode | suggest_caw_workflow | 1 | requires .caw/ directory |

## Triggers

This skill activates when:
1. `ExitPlanMode` tool is called
2. Plan file is created/modified in configured `plansDirectory` (see `_shared/plans-directory-resolution.md`)
3. User mentions "plan is ready" or similar phrases

## Behavior

### Step 1: Detect Plan File

When triggered, locate the plan file:

```
1. Resolve plansDirectory setting:
   - Read .claude/settings.local.json → "plansDirectory"
   - If not found → Read .claude/settings.json
   - If not found → Read ~/.claude/settings.json
   - If not found → Use default ".claude/plans/"

2. Check for recently modified files:
   - {plansDirectory}/*.md (configured location)
   - .claude/plan.md (legacy, always check)

3. Validate file contains implementation steps
4. Parse plan structure using patterns from patterns.md
```

### Step 2: Analyze Plan Content

Two-part analysis — first check structure, then assess readiness.

#### Part A: Structure Check

Match patterns from `patterns.md` to confirm the plan has the minimum elements:

```markdown
Required elements (must have at least 2):
- [ ] Clear task/feature title
- [ ] Implementation steps or phases
- [ ] File modifications or creations listed
```

If fewer than 2 are present, skip to the "Plan Not Suitable" output (Step 3).

#### Part B: Readiness Assessment

This is the most important part. Even a well-structured plan may have gaps that cause rework. Read the plan as an engineer who has to implement it, and ask: "What questions would I need answered before I could start coding?"

Look for these common gaps:
- **Unspecified infrastructure**: Does the plan reference a database, cache, or queue without saying which one or how it's configured?
- **Missing data models**: Are there endpoints or operations that imply a data schema that isn't defined?
- **Implicit dependencies**: Does the plan assume something exists (auth system, API client, config) without stating it?
- **Ambiguous technical choices**: Are there decisions mentioned but not resolved (e.g., "consider Redis or Memcached")?
- **Missing error/edge cases**: For user-facing features, are error states and validation rules defined?
- **No success criteria**: How will you know the implementation is correct?

Report what you find — the goal is to surface gaps the user may not have noticed, not to block them from starting. A plan with minor gaps can still proceed; a plan with fundamental gaps (no data model for a CRUD feature, no auth strategy for a security feature) should be flagged.

### Step 3: Present Options to User

Use AskUserQuestion to offer workflow options. The output should combine the structure check results with the readiness assessment:

```
🎯 Plan Mode Completion Detected

Plan file: [plan file path]

📋 Structure:
  ✅ Implementation stages: [N] Phases, [M] Steps detected
  ✅ File changes: [X] files expected
  [✅/⚠️] Technical decisions: [documented/not found]

🔍 Readiness Assessment:
  [List specific gaps found, or "No major gaps identified" if clean]
  Example gaps:
  - ⚠️ User storage: plan references login but no database/schema defined
  - ⚠️ Key management: RS256 specified but key storage location not decided

💡 [Recommendation based on gap severity]

CAW Workflow Options:
[1] Auto start - Execute /cw:go
[2] Design first - Start after detailed design with /cw:explore --arch
[3] Manual proceed - Start manually later
[4] Edit plan - Return to Plan Mode
```

When gaps exist, adjust the recommendation: suggest [2] or [4] for plans with fundamental gaps, [1] for plans with no or minor gaps.

### Step 4: Execute Selected Option

Based on user selection:

| Option | Action |
|--------|--------|
| 1 | Invoke `/cw:go` |
| 2 | Invoke `/cw:explore --arch` |
| 3 | Display reminder message |
| 4 | Suggest re-entering Plan Mode |

## Integration

- **Hook Trigger**: PostToolUse (ExitPlanMode)
- **Pattern Reference**: `patterns.md` for plan file recognition
- **Output**: User decision → appropriate command invocation
- **Next Steps**: `/cw:go`, `/cw:explore --arch`, or manual workflow

## Output Messages

### Plan Detected — Ready to Start
```
🎯 Plan Mode Completion Detected

Plan file: .claude/plans/data-export.md

📋 Structure:
   Title: CSV Data Export Feature
   Implementation stages: 2 Phases, 4 Steps
   Expected files: 3 created, 1 modified
   Technical decisions: streaming writes, RFC 4180 compliance

🔍 Readiness: No major gaps identified.
   All data sources and output formats are specified.

💡 Plan is ready for implementation.

CAW Workflow Options:
[1] Auto start - Execute /cw:go  ← recommended
[2] Design first - /cw:explore --arch
[3] Manual proceed
[4] Edit plan
```

### Plan Detected — Gaps Found
```
🎯 Plan Mode Completion Detected

Plan file: .claude/plans/auth-implementation.md

📋 Structure:
   Title: User Authentication with JWT
   Implementation stages: 3 Phases, 7 Steps
   Expected files: 5 created, 2 modified
   Technical decisions: RS256, bcrypt

🔍 Readiness: 3 gaps found
   ⚠️ User storage — login/register endpoints defined but no database, ORM, or user schema specified
   ⚠️ Refresh token persistence — RS256 + refresh tokens typically need server-side storage for revocation, not addressed
   ⚠️ RSA key management — RS256 requires a key pair, but storage location (env vars, file, vault) not decided

💡 Consider resolving these gaps before starting, or use design-first mode.

CAW Workflow Options:
[1] Auto start - Execute /cw:go
[2] Design first - /cw:explore --arch  ← recommended
[3] Manual proceed
[4] Edit plan
```

### Plan Not Suitable
```
ℹ️ Plan Mode Completion Detected

Plan file was found but is not suitable for CAW workflow:
  ⚠️ Implementation stages are not clear
  ⚠️ File changes are not defined

Recommendations:
  • Write more detailed implementation stages in Plan Mode
  • Or start fresh with /cw:go "task description"
```

## Directory Structure

```
skills/plan-detector/
├── SKILL.md      # This file - core behavior
└── patterns.md   # Plan file pattern definitions
```

## Boundaries

**Will:**
- Detect plan file creation/modification
- Analyze plan structure for CAW compatibility
- Offer appropriate workflow options
- Provide clear feedback on plan quality

**Will Not:**
- Automatically start workflow without user confirmation
- Modify the original plan file
- Force CAW workflow on unsuitable plans
