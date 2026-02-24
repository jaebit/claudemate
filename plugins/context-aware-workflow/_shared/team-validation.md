# Team Validation (Debate Pattern)

Enhanced review phase using Agent Teams for reviewer cross-validation via SendMessage.

## Overview

Extension of [Parallel Validation](./parallel-validation.md) that adds inter-reviewer communication.
Instead of 3 independent reviewers producing isolated verdicts, reviewers exchange findings and
challenge each other's conclusions before producing a consensus verdict.

## Debate Flow

```
Phase 1: Independent Review (parallel)
  ├── Functional Reviewer → findings
  ├── Security Reviewer → findings
  └── Quality Reviewer → findings

Phase 2: Cross-Validation (via SendMessage)
  ├── Each reviewer shares findings with others
  ├── Reviewers challenge/confirm each other's findings
  └── Identify missed issues or false positives

Phase 3: Consensus
  ├── Aggregate validated findings
  ├── Remove false positives
  └── Produce consensus verdict
```

## Implementation

### Phase 1: Independent Review

Each reviewer runs in their own Agent Teams session. Same prompts as
[Parallel Validation](./parallel-validation.md) but with team awareness:

```markdown
You are part of a review team. After your independent review,
you will share findings with other reviewers for cross-validation.

Focus on your specialty area. Be thorough - other reviewers will
challenge your findings.
```

### Phase 2: Cross-Validation via SendMessage

After all reviewers complete Phase 1, the team lead triggers exchange:

```markdown
## Cross-Validation Round

Share your top findings with the team using SendMessage.
Review findings from other team members.

For each finding from another reviewer:
- CONFIRM: You agree this is a real issue
- CHALLENGE: You believe this may be a false positive (explain why)
- ESCALATE: You found a related issue that makes this worse

Use SendMessage to communicate:
  SendMessage to="reviewer-functional" message="RE: Finding #2 - I confirm this is an issue because..."
```

### Phase 3: Consensus Verdict

After cross-validation, the team lead collects results:

```json
{
  "consensus_verdict": "APPROVED" | "REJECTED" | "NEEDS_FIX",
  "confirmed_issues": [
    {
      "original_reviewer": "security",
      "confirmed_by": ["functional", "quality"],
      "severity": "critical",
      "description": "..."
    }
  ],
  "dismissed_issues": [
    {
      "original_reviewer": "quality",
      "challenged_by": "functional",
      "reason": "False positive - intentional design pattern"
    }
  ]
}
```

## When to Use Debate Pattern

| Scenario | Use Debate? |
|----------|-------------|
| Standard feature implementation | No - parallel validation sufficient |
| Security-critical changes | Yes |
| Architecture changes | Yes |
| Large refactoring (50+ files) | Yes |
| Cross-cutting concerns | Yes |

## Integration with /cw:auto

Activated via `--debate` flag:

```bash
/cw:auto "Implement auth system" --team --debate
```

In Stage 6 (Review):
1. Create reviewer team with `TeamCreate`
2. Assign independent review tasks
3. Wait for Phase 1 completion (`TaskCompleted` hook)
4. Trigger cross-validation round via `SendMessage`
5. Collect consensus verdict
6. Proceed to Fix stage if needed

## Fallback

When `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is not set:
- Falls back to standard parallel validation (3 independent Task subagents)
- No cross-validation phase (reviewers cannot communicate)
- Same verdict aggregation logic applies
