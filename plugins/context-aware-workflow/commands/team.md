---
description: Orchestrate Agent Teams for parallel collaborative development with worktree isolation
argument-hint: "<subcommand> [options]"
---

# /cw:team - Agent Teams Orchestration

Manage multi-session Agent Teams for complex collaborative tasks with direct inter-agent
communication and worktree-isolated parallel execution.

## Usage

```bash
# Team lifecycle
/cw:team create <name> [--roles planner,builder,reviewer] [--size N]
/cw:team assign [--from-plan]
/cw:team status
/cw:team gate
/cw:team synthesize
/cw:team cleanup
```

## Prerequisites

Agent Teams is an experimental feature requiring:

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

If not set, commands will show:
```
Agent Teams is an experimental feature.
Enable: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

Alternative: /cw:swarm for parallel execution without inter-agent communication.
```

## /cw:team vs /cw:swarm

| Aspect | /cw:swarm | /cw:team |
|--------|-----------|----------|
| Mechanism | Task subagents (single session) | Agent Teams (multi-session) |
| Communication | Report-only | Direct messaging via SendMessage |
| Coordination | Fire-and-forget | Team lead + shared task list |
| Isolation | Optional (`--worktrees`) | Automatic worktree per member |
| Cost | Lower (shared context) | Higher (separate context per member) |
| Best for | Independent simple tasks | Complex tasks needing collaboration |

## Subcommands

### create

Create a new team with specified roles.

```bash
/cw:team create feature-auth                           # Default: 2 builders + 1 reviewer
/cw:team create feature-auth --roles builder,reviewer  # Custom roles
/cw:team create feature-auth --size 3                  # 3 builders + 1 reviewer
```

**Default Composition**: 2x Builder + 1x Reviewer

**Behavior**:
1. Verify `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is set
2. Create team via `TeamCreate` tool
3. Each member gets an isolated worktree (`isolation: worktree`)
4. Initialize `.caw/team_state.json` with roles and task list
5. Report team composition and worktree paths

**Output**:
```
Team 'feature-auth' created

Members:
  builder-1:  .claude/worktrees/feature-auth-b1/  (worktree-feature-auth-b1)
  builder-2:  .claude/worktrees/feature-auth-b2/  (worktree-feature-auth-b2)
  reviewer-1: .claude/worktrees/feature-auth-r1/  (worktree-feature-auth-r1)

State: .caw/team_state.json
Next: /cw:team assign --from-plan
```

### assign

Assign tasks to team members from task_plan.md.

```bash
/cw:team assign              # Manual assignment prompt
/cw:team assign --from-plan  # Auto-assign from .caw/task_plan.md
```

**`--from-plan` Behavior**:
1. Read `.caw/task_plan.md`
2. Identify independent phases/steps (no dependency conflicts)
3. Assign to available builders via shared task list
4. Dependencies are tracked - blocked tasks wait automatically
5. `TeammateIdle` hook auto-assigns next available task

### status

Show current team state.

```bash
/cw:team status
```

**Output**:
```
Team 'feature-auth' Status

| Member | Role | Status | Current Task | Worktree |
|--------|------|--------|-------------|----------|
| builder-1 | builder | working | 2.1 Create JWT | worktree-feature-auth-b1 |
| builder-2 | builder | working | 2.3 Add middleware | worktree-feature-auth-b2 |
| reviewer-1 | reviewer | idle | - | worktree-feature-auth-r1 |

Tasks: 3/8 complete | 2 in progress | 3 pending
Quality Gate: Enabled (min 1 reviewer)
```

### gate

Trigger quality gate - request reviewer validation of completed tasks.

```bash
/cw:team gate
```

**Behavior**:
1. Collect all tasks marked "done" but not reviewed
2. Send review requests to reviewer members via `SendMessage`
3. Reviewer validates in their worktree
4. `TaskCompleted` hook enforces review before final completion
5. Report review results

### synthesize

Merge results from all team worktrees and produce summary report.

```bash
/cw:team synthesize
```

**Behavior**:
1. Verify all assigned tasks are complete
2. Merge worktree branches sequentially (earliest first)
3. Resolve conflicts if any (prompt user for complex conflicts)
4. Generate synthesis report with files changed per member
5. Update `.caw/team_state.json` with synthesis results

**Output**:
```
Synthesizing team 'feature-auth'

Merging worktree-feature-auth-b1... done (3 files)
Merging worktree-feature-auth-b2... done (2 files)
Merging worktree-feature-auth-r1... done (0 files)

No conflicts detected.

Summary:
  Files created: 4
  Files modified: 3
  Tests: 12 passed
  Review: APPROVED

Next: /cw:team cleanup
```

### cleanup

Disband team and remove worktrees.

```bash
/cw:team cleanup
```

**Behavior**:
1. Delete team via `TeamDelete` tool
2. Remove worktrees (prompt if unmerged changes exist)
3. Archive `.caw/team_state.json` to `.caw/team_state.{name}.archive.json`

## State Management

State stored in `.caw/team_state.json`. Schema: `../_shared/schemas/team-state.schema.json`

```json
{
  "schema_version": "1.0",
  "team_name": "feature-auth",
  "active": true,
  "roles": [
    { "role": "builder", "agent": "builder.md", "worktree": ".claude/worktrees/feature-auth-b1/", "status": "working" },
    { "role": "reviewer", "agent": "reviewer.md", "worktree": ".claude/worktrees/feature-auth-r1/", "status": "idle" }
  ],
  "tasks": [
    { "id": "2.1", "description": "Create JWT module", "assigned_to": "builder-1", "status": "in_progress", "depends_on": [] }
  ],
  "quality_gates": { "require_review": true, "min_reviewers": 1, "debate_mode": false }
}
```

## Hooks Integration

| Hook | Trigger | Behavior |
|------|---------|----------|
| `TeammateIdle` | Team member finishes task | Auto-assign next available task (exit 2 = feedback) |
| `TaskCompleted` | Task marked done | Enforce quality gate review (exit 2 = block) |
| `WorktreeCreate` | Worktree created for member | Copy `.caw/` files to worktree |
| `WorktreeRemove` | Worktree cleaned up | Clean metadata |

## Debate Pattern

With `--debate` flag (or `quality_gates.debate_mode: true`), reviewers use
cross-validation instead of independent review:

1. Each reviewer independently reviews assigned tasks
2. Reviewers share findings via `SendMessage`
3. Cross-validate: confirm, challenge, or escalate each finding
4. Produce consensus verdict

See [Team Validation](../_shared/team-validation.md) for full protocol.

## Integration with /cw:auto

```bash
/cw:auto "task" --team              # Enable team mode for parallel stages
/cw:auto "task" --team --size 3     # 3 builders
/cw:auto "task" --team --debate     # Team mode + debate review
```

See `/cw:auto` documentation for team mode stage behaviors.

## Error Handling

| Error | Recovery |
|-------|----------|
| Agent Teams not enabled | Show activation instructions, suggest /cw:swarm |
| Member crashes | Other members continue, crashed member's tasks re-queued |
| Merge conflict | Pause synthesis, prompt user for resolution |
| All tasks blocked | Report dependency cycle, suggest manual intervention |
