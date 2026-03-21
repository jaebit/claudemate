---
name: parallel
description: "Execute tasks in parallel using swarm or Agent Teams"
argument-hint: "<tasks...> [flags]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Agent, AskUserQuestion, SendMessage
---

# /crew:parallel - Parallel Execution

Execute multiple independent tasks concurrently using swarm mode or Agent Teams.

## Arguments

**Invoked as**: $ARGUMENTS

## Current State

- **Swarm state**: !`cat .caw/swarm_state.json 2>/dev/null | head -5 || echo "(no active swarm)"`
- **Task plan**: !`cat .caw/task_plan.md 2>/dev/null | head -10 || echo "(no task plan)"`

## Usage

```bash
# Swarm mode (default) - fire-and-forget via Task agents
/crew:parallel "task1" "task2" "task3"
/crew:parallel --workers 4 "taskA" "taskB"
/crew:parallel --from-plan
/crew:parallel --merge "feature-A" "feature-B"

# Team mode - collaborative with inter-agent communication
/crew:parallel --team "task1" "task2" "task3"
/crew:parallel --team create feature-auth --size 3
/crew:parallel --team assign --from-plan
/crew:parallel --team status
/crew:parallel --team gate
/crew:parallel --team synthesize
/crew:parallel --team cleanup

# Codex mode - offload to Codex harness
/crew:parallel --codex "task1" "task2"
```

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--workers N` | task count | Max concurrent workers |
| `--timeout S` | 300 | Per-task timeout (seconds) |
| `--merge` | false | Auto-merge file results |
| `--from-plan` | false | Extract from task_plan.md |
| `--worktrees` | false | Each task gets git worktree |
| `--on-error` | continue | `continue` or `stop` |
| `--team` | false | Use Agent Teams (collaborative mode) |
| `--codex` | false | Offload to Codex harness |

## Modes

| Aspect | Swarm (default) | Team (`--team`) | Codex (`--codex`) |
|--------|-----------------|-----------------|-------------------|
| Mechanism | Task subagents (single session) | Agent Teams (multi-session) | Codex harness |
| Communication | Report-only | Direct messaging via SendMessage | Async results |
| Coordination | Fire-and-forget | Team lead + shared task list | Background |
| Isolation | Optional (`--worktrees`) | Automatic worktree per member | Separate process |
| Cost | Lower (shared context) | Higher (separate context per member) | Variable |
| Best for | Independent simple tasks | Complex tasks needing collaboration | Offloading bulk work |

## Swarm Mode (Default)

### Workflow

1. **Analyze**: Check task independence, detect dependencies
2. **Allocate**: Assign agents by category/complexity
3. **Execute**: Parallel Task agents with progress tracking
4. **Aggregate**: Collect results, resolve conflicts

### Swarm Modes

| Mode | Description |
|------|-------------|
| **Independent** | Each task isolated context |
| **Worktree** | Each task gets git worktree |
| **Shared Context** | Read-only shared, write separate |

### Conflict Resolution

When multiple tasks modify the same file:
```
Conflict: src/Button.tsx
  [1] task1: Added onClick
  [2] task3: Changed styling

Options: 1. Manual | 2. Keep task1 | 3. Keep task3 | 4. Abort
```

## Team Mode (`--team`)

Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Falls back to swarm if not set.

### Subcommands

| Subcommand | Description |
|------------|-------------|
| `create <name> [--size N]` | Create team with builders + reviewer |
| `assign [--from-plan]` | Assign tasks to team members |
| `status` | Show current team state |
| `gate` | Trigger quality gate review |
| `synthesize` | Merge results from all worktrees |
| `cleanup` | Disband team and remove worktrees |

### Team Composition

Default: 2x Builder + 1x Reviewer. Each member gets an isolated worktree.

### Debate Pattern

With `--debate`, reviewers use cross-validation:
1. Independent review
2. Share findings via SendMessage
3. Cross-validate: confirm, challenge, or escalate
4. Consensus verdict

## Output

### Swarm Output

```
Swarm Status
Workers: 3/3 active | Timeout: 120s

[1] login API      ████████░░░░ 65%  builder-sonnet
[2] logout button  ██████████░░ 85%  builder-haiku
[3] auth review    ████░░░░░░░░ 35%  Reviewer

Elapsed: 45s | Est. remaining: 30s

Swarm Complete
  Total: 3 | Success: 3 | Failed: 0
  Tokens: 45,200 | Cost: $0.42 | Duration: 1m 7s
```

### Team Output

```
Team 'feature-auth' Status

| Member | Role | Status | Current Task | Worktree |
|--------|------|--------|-------------|----------|
| builder-1 | builder | working | 2.1 Create JWT | worktree-feature-auth-b1 |
| builder-2 | builder | working | 2.3 Add middleware | worktree-feature-auth-b2 |
| reviewer-1 | reviewer | idle | - | worktree-feature-auth-r1 |

Tasks: 3/8 complete | 2 in progress | 3 pending
```

## State

Saved in `.caw/swarm_state.json` (swarm) or `.caw/team_state.json` (team).

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Single task failure | Continue (or stop with `--on-error stop`) |
| Timeout | Kill task, mark failed |
| Agent Teams not enabled | Show activation instructions, fall back to swarm |
| Member crashes | Other members continue, crashed member's tasks re-queued |
| Merge conflict | Pause, prompt user for resolution |

## Hooks Integration (Team Mode)

| Hook | Trigger | Behavior |
|------|---------|----------|
| `TeammateIdle` | Member finishes task | Auto-assign next available task |
| `TaskCompleted` | Task marked done | Enforce quality gate review |
| `WorktreeCreate` | Worktree created | Copy `.caw/` files to worktree |

## Boundaries

**Will:**
- Read task descriptions, `.caw/task_plan.md`
- Invoke Builder, Reviewer agents
- Create `.caw/swarm_state.json`, `.caw/team_state.json`

**Won't:**
- Modify files outside assigned task scope
- Override `--on-error stop` behavior
- Start team mode without `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`
