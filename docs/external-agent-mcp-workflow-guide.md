# External Agent Guide For Codex MCP Workflows

This guide is for teams that want an external orchestrator agent to control multiple Codex workers over `codex mcp-server`.

Scope:
- `app-server` integrations are out of scope here. If you want a rich client integration with background jobs, streamed UI state, or native review flows inside Claude Code, use `codex-plugin-cc`.
- This guide covers the two `mcp-server` scenarios discussed earlier:
  - Scenario 1: external debate orchestration
  - Scenario 2: parallel implementation followed by parallel review

Primary references:
- `https://developers.openai.com/codex/guides/agents-sdk`
- `https://developers.openai.com/api/docs/guides/agents/integrations-observability#mcp`

## Goals

Use this document when you need to tell an external agent:
- how to connect to Codex over MCP
- how to structure worker roles
- how to pass the right instructions to each Codex worker
- how to keep state stable across turns with `threadId`
- how to request specific skills without depending on Codex internal subagents

## Assumptions

- Codex CLI is installed and available as `codex`
- The orchestrator runtime can launch local MCP servers over stdio
- Each Codex worker is exposed through the Codex MCP tools:
  - `codex`
  - `codex-reply`
- The orchestrator, not Codex, owns the top-level workflow state machine
- If a worker needs a specific skill, the skill is already installed and visible to that Codex runtime

## Why `mcp-server`

`codex mcp-server` is the right fit when:
- the external agent is the real orchestrator
- Codex workers are used as specialist engines
- workflow state, retries, fan-out, and fan-in live outside Codex
- you want simple and explicit worker boundaries

Do not use Codex internal subagents as the main orchestration primitive in these scenarios. The external orchestrator already provides the role split. Nesting another agent tree inside each Codex worker usually makes control, tracing, and failure recovery worse.

## Core Rules

- Treat each Codex worker as one durable thread.
- Persist `threadId` after the first `codex` call and reuse it with `codex-reply`.
- Prefer explicit worker roles over open-ended prompts.
- Request skills through prompt or developer instructions, not through implied behavior.
- Use fresh review workers for code review. Do not reuse implementation threads for review.
- Keep the orchestrator responsible for:
  - worker creation
  - message routing
  - consensus logic
  - merge policy
  - final approval

## MCP Connection Template

Python example:

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

codex_server = MCPServerStdio(
    name="Codex CLI",
    params={
        "command": "codex",
        "args": ["mcp-server"],
    },
)
```

TypeScript example:

```ts
import { Agent, MCPServerStdio } from "@openai/agents";

const codexServer = new MCPServerStdio({
  name: "Codex CLI",
  fullCommand: "codex mcp-server",
});
```

## Common Worker Config Schema

Use this JSON payload shape as the orchestrator-side source of truth before it talks to Codex.

```json
{
  "$schema": "https://example.com/schemas/codex-mcp-worker-config.schema.json",
  "scenario": "debate",
  "workspace": {
    "cwd": "/absolute/path/to/repo"
  },
  "runtime": {
    "approval_policy": "never",
    "sandbox": "workspace-write",
    "model": "gpt-5.4-mini",
    "profile": null
  },
  "workers": [
    {
      "id": "codex-1",
      "role": "debater-pro",
      "skills": ["argument-mapping", "risk-analysis"],
      "developer_instructions": "Use $argument-mapping and $risk-analysis before finalizing each response.",
      "thread_id": null
    }
  ]
}
```

Suggested JSON Schema:

```json
{
  "$id": "https://example.com/schemas/codex-mcp-worker-config.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["scenario", "workspace", "runtime", "workers"],
  "properties": {
    "scenario": {
      "type": "string",
      "enum": ["debate", "parallel-build-review"]
    },
    "workspace": {
      "type": "object",
      "additionalProperties": false,
      "required": ["cwd"],
      "properties": {
        "cwd": { "type": "string", "minLength": 1 }
      }
    },
    "runtime": {
      "type": "object",
      "additionalProperties": false,
      "required": ["approval_policy", "sandbox"],
      "properties": {
        "approval_policy": {
          "type": "string",
          "enum": ["untrusted", "on-request", "never"]
        },
        "sandbox": {
          "type": "string",
          "enum": ["read-only", "workspace-write", "danger-full-access"]
        },
        "model": {
          "type": ["string", "null"]
        },
        "profile": {
          "type": ["string", "null"]
        }
      }
    },
    "workers": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "role", "skills", "developer_instructions", "thread_id"],
        "properties": {
          "id": { "type": "string", "minLength": 1 },
          "role": { "type": "string", "minLength": 1 },
          "skills": {
            "type": "array",
            "items": { "type": "string", "minLength": 1 }
          },
          "developer_instructions": {
            "type": "string"
          },
          "thread_id": {
            "type": ["string", "null"]
          }
        }
      }
    }
  }
}
```

## Codex Call Contract

The orchestrator should treat Codex like this:

Initial call:

```json
{
  "tool": "codex",
  "arguments": {
    "prompt": "Worker-specific task prompt",
    "cwd": "/absolute/path/to/repo",
    "approval-policy": "never",
    "sandbox": "workspace-write",
    "model": "gpt-5.4-mini",
    "developer-instructions": "Use $skill-a and $skill-b. Do not spawn internal subagents."
  }
}
```

Follow-up call:

```json
{
  "tool": "codex-reply",
  "arguments": {
    "threadId": "persisted-thread-id",
    "prompt": "Next instruction for this same worker"
  }
}
```

Persist:
- `threadId`
- worker role
- worker state
- last completed assignment

## Skill Request Pattern

Recommended pattern:

- Put the skill request in `developer-instructions`
- Also repeat the skill request in the task prompt if the skill is critical

Recommended wording:

```text
Use $skill-name before drafting the final answer.
If the skill is unavailable, continue with the best fallback and state that the skill was unavailable.
Do not spawn internal subagents for this task.
```

Avoid:
- vague requests like "use your best tools"
- requests that rely on Codex internally deciding to split the work
- mixing role instructions and workflow routing in one giant prompt

## Scenario 1

### Purpose

An external orchestrator leads a structured debate on a topic. Codex workers act as debaters. The orchestrator manages rounds, collects evidence, and produces the final consensus.

### Role Layout

- `codex-1`: proposes a strong position
- `codex-2`: attacks assumptions and edge cases
- `codex-3`: synthesizes tradeoffs and tries to reconcile disagreement
- external orchestrator: decides the winner, consensus, dissent, and next round

### Recommended Runtime

- sandbox: `read-only`
- approval policy: `never`
- one worker thread per debater
- no internal subagents

### Debate Worker Schema

```json
{
  "scenario": "debate",
  "topic": "Should the team adopt event sourcing for the billing subsystem?",
  "rounds": 3,
  "workers": [
    {
      "id": "codex-1",
      "role": "affirmative",
      "stance": "argue for adoption",
      "skills": ["argument-mapping"],
      "thread_id": null
    },
    {
      "id": "codex-2",
      "role": "negative",
      "stance": "argue against adoption",
      "skills": ["risk-analysis"],
      "thread_id": null
    },
    {
      "id": "codex-3",
      "role": "synthesis",
      "stance": "extract strongest claims and unresolved disagreements",
      "skills": ["decision-analysis"],
      "thread_id": null
    }
  ]
}
```

### Orchestrator Request Template

Use this as the external agent instruction template:

```text
You are the debate orchestrator.

Goal:
- run a structured debate across three Codex workers
- keep each worker in its own thread
- collect claims, counterclaims, and evidence
- produce a final consensus with dissent when needed

Rules:
- do not let Codex workers talk directly to each other
- route all messages through the orchestrator
- persist threadId for each worker and use codex-reply for later rounds
- use read-only Codex workers
- request listed skills through developer-instructions
- do not ask workers to spawn internal subagents

Round structure:
1. Ask each worker for its opening statement.
2. Send summarized opposition points back to the other workers.
3. Ask each worker for rebuttal.
4. Ask the synthesis worker to summarize strongest arguments, disagreements, and decision criteria.
5. Produce the final consensus.
```

### Codex Worker Prompt Template

```text
Role: {{ROLE}}
Topic: {{TOPIC}}
Stance: {{STANCE}}

Output contract:
- give a compact position
- list 3-5 key arguments
- identify the strongest uncertainty
- do not roleplay conversation with other workers
- do not spawn internal subagents
```

### Consensus Output Schema

```json
{
  "$id": "https://example.com/schemas/debate-consensus.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["topic", "decision", "summary", "supporting_points", "dissent", "open_questions"],
  "properties": {
    "topic": { "type": "string" },
    "decision": {
      "type": "string",
      "enum": ["accept", "reject", "defer", "split-decision"]
    },
    "summary": { "type": "string" },
    "supporting_points": {
      "type": "array",
      "items": { "type": "string" }
    },
    "dissent": {
      "type": "array",
      "items": { "type": "string" }
    },
    "open_questions": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

## Scenario 2

### Purpose

An external orchestrator assigns parallel coding tasks to multiple Codex workers. After implementation finishes, fresh Codex workers perform parallel code reviews.

### Role Layout

- `coder-a`, `coder-b`, `coder-c`: parallel implementation workers
- `reviewer-a`, `reviewer-b`, `reviewer-c`: fresh review workers
- external orchestrator: task split, worktree allocation, merge policy, reviewer assignment, final approval

### Recommended Runtime

Implementation:
- sandbox: `workspace-write`
- approval policy: `never`
- one worktree or isolated checkout per coder

Review:
- sandbox: `read-only`
- approval policy: `never`
- fresh thread per reviewer
- reviewers must not reuse coder threadIds

### Parallel Build And Review Schema

```json
{
  "scenario": "parallel-build-review",
  "workspace": {
    "root": "/absolute/path/to/repo",
    "worktrees": [
      "/absolute/path/to/repo/.worktrees/coder-a",
      "/absolute/path/to/repo/.worktrees/coder-b",
      "/absolute/path/to/repo/.worktrees/coder-c"
    ]
  },
  "coding_workers": [
    {
      "id": "coder-a",
      "role": "implement-api",
      "cwd": "/absolute/path/to/repo/.worktrees/coder-a",
      "skills": ["backend-api", "test-writing"],
      "thread_id": null
    },
    {
      "id": "coder-b",
      "role": "implement-ui",
      "cwd": "/absolute/path/to/repo/.worktrees/coder-b",
      "skills": ["frontend-ui"],
      "thread_id": null
    },
    {
      "id": "coder-c",
      "role": "implement-data-layer",
      "cwd": "/absolute/path/to/repo/.worktrees/coder-c",
      "skills": ["database-design"],
      "thread_id": null
    }
  ],
  "review_workers": [
    {
      "id": "reviewer-a",
      "role": "correctness-review",
      "skills": ["code-review"],
      "thread_id": null
    },
    {
      "id": "reviewer-b",
      "role": "risk-review",
      "skills": ["risk-analysis", "security-review"],
      "thread_id": null
    },
    {
      "id": "reviewer-c",
      "role": "test-and-regression-review",
      "skills": ["test-review"],
      "thread_id": null
    }
  ]
}
```

### Orchestrator Request Template

```text
You are the implementation orchestrator.

Goal:
- split the work across three Codex coding workers
- keep workers isolated by checkout or worktree
- collect completed outputs
- assemble a merge candidate
- send the merge candidate to fresh Codex review workers
- produce a final ship or revise decision

Rules:
- each coding worker gets exactly one assigned scope
- coding workers use workspace-write
- review workers use read-only
- review workers must be fresh threads
- do not ask any Codex worker to spawn internal subagents
- request required skills through developer-instructions
- if coding outputs conflict, resolve conflicts before review
- reviewers should see the merged candidate or final diff, not raw parallel chatter
```

### Coder Prompt Template

```text
Role: {{ROLE}}
Scope: {{SCOPE}}
Constraints:
- modify only files relevant to your assigned scope
- keep changes minimal and local
- add tests only when directly relevant
- do not spawn internal subagents
- if blocked, report the blocker and stop

Required skills:
{{SKILL_LIST}}
```

### Reviewer Prompt Template

```text
Role: {{ROLE}}
Review target: merged candidate diff

Rules:
- review only; do not fix code
- report concrete, material findings only
- prefer deep equality of reasoning over style commentary
- do not spawn internal subagents
- focus on correctness, regressions, operational risk, and missing tests

Required skills:
{{SKILL_LIST}}
```

### Review Findings Schema

```json
{
  "$id": "https://example.com/schemas/review-findings.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["verdict", "summary", "findings"],
  "properties": {
    "verdict": {
      "type": "string",
      "enum": ["approve", "needs-attention"]
    },
    "summary": {
      "type": "string"
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["title", "severity", "file", "line_start", "line_end", "body", "recommendation"],
        "properties": {
          "title": { "type": "string" },
          "severity": {
            "type": "string",
            "enum": ["low", "medium", "high", "critical"]
          },
          "file": { "type": "string" },
          "line_start": { "type": "integer", "minimum": 1 },
          "line_end": { "type": "integer", "minimum": 1 },
          "body": { "type": "string" },
          "recommendation": { "type": "string" }
        }
      }
    }
  }
}
```

## Recommended Defaults

Scenario 1:
- sandbox: `read-only`
- approval policy: `never`
- fresh workers: no
- reuse threadId: yes
- internal subagents: no

Scenario 2 coding:
- sandbox: `workspace-write`
- approval policy: `never`
- fresh workers: no
- reuse threadId: yes
- internal subagents: no

Scenario 2 review:
- sandbox: `read-only`
- approval policy: `never`
- fresh workers: yes
- reuse threadId: no
- internal subagents: no

## Failure Handling

If a Codex worker fails:
- keep its `threadId` if the thread was created successfully
- send a small recovery prompt through `codex-reply`
- if the worker is no longer trustworthy for that assignment, replace it with a fresh worker

If a skill is unavailable:
- let the worker continue with fallback behavior
- record the missing skill in orchestrator state
- do not silently assume the skill was applied

If coding workers overlap:
- stop the overlapping assignment at the orchestrator level
- do not ask Codex to negotiate ownership dynamically

## Minimal Orchestrator Checklist

- Launch one `codex mcp-server`
- Create one worker record per Codex role
- Store `threadId` after the first call
- Keep developer instructions short and role-specific
- Use `codex-reply` for later rounds or follow-ups
- Keep review workers fresh
- Keep internal subagents disabled by policy and prompt

## Copy-Paste Summary

Use this instruction when telling an external orchestrator how to behave:

```text
Use Codex only as an MCP worker runtime.
Create one durable thread per worker and persist threadId.
Request required Codex skills through developer-instructions.
Do not ask Codex workers to spawn internal subagents.
For debate workflows, keep all workers read-only and route all exchanges through the orchestrator.
For implementation workflows, isolate coding workers by worktree and use fresh read-only review workers after merge-candidate creation.
```
