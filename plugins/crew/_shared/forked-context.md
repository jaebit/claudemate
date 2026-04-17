# Forked Context Pattern

Skills with `forked-context: true` run in an isolated context.

## Why Fork (post-1M context)

With the primary model's 1M context window, forking is **no longer a token-budget survival tool**. It remains valuable for three narrower reasons:

1. **Structured-output discipline.** A forked skill must return a schema-shaped result to be useful. This forces skill authors to define an explicit contract (`result.success`, `result.data`, `result.summary`) instead of leaking conversational prose back to the orchestrator.
2. **State isolation.** The forked skill cannot see — and therefore cannot accidentally depend on — prior conversation context. This guarantees the skill behaves identically whether invoked early or late in a session, which matters for deterministic replay and for skills called from multiple orchestrators.
3. **Prompt-cache stability.** The main conversation's cache is not perturbed by the skill's internal reasoning tokens, which keeps the executor's per-call cost predictable.

If none of the three apply to a new skill, do not set `forked-context: true` just out of habit — the default inline invocation is simpler and cheaper.

## Behavior

- Skill executes in separate context from main conversation
- Cannot see prior conversation history
- Must return structured output for main context to use

## Return Format

Skill must return structured data that main context can consume:

```yaml
result:
  success: true|false
  data: [skill output]
  summary: [brief description]
```

## Usage in Skills

```yaml
---
forked-context: true
---
```

When forked:
1. Skill receives only the invocation prompt
2. Performs isolated analysis/action
3. Returns structured result
4. Main context processes result
