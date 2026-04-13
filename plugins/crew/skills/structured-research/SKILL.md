---
name: structured-research
user_invocable: false
description: "Deep research and investigation skill that produces comprehensive, cross-validated reports on any topic. Use this skill whenever the user asks to research, investigate, compare, or do a deep dive on technologies, architectures, tools, libraries, frameworks, or strategies. Triggers on phrases like 'research X', 'deep dive on', 'compare X vs Y', 'thorough analysis of', 'investigate how', 'pros and cons', 'trade-offs between', '비교 분석', '심층 분석', '조사해줘'. Decomposes topics into subtopics, dispatches parallel web/docs investigations via MCP tools, cross-validates findings for contradictions, and synthesizes into a structured research report with confidence ratings and sourced citations."
disable-model-invocation: true
---

# Structured Research

4-stage deep research process: **Decompose → Parallel Investigate → Cross-Validate → Synthesize**.

## Current Project Context

- **Research output directory**: !`ls .caw/research/ 2>/dev/null || echo "(no prior research)"`

## MCP Servers

- `tavily` — Web research and extraction
- `exa` — Semantic web search
- `context7` — Library/framework documentation lookup

## Stage 1: Decomposition

Analyze the research topic and generate ~5 focused subtopic questions.

### Tool Assignment

Assign tools per subtopic based on type:

| Subtopic Type | Primary | Secondary |
|---------------|---------|-----------|
| Library/framework | context7 (`resolve-library-id` → `query-docs`) | tavily (`tavily_research`) |
| Comparison/vs | WebSearch | gemini (`gemini -p`) |
| Broad/conceptual | exa (`web_search_exa`) | tavily (`tavily_research`) |
| Implementation | tavily (`tavily_research`) | context7 |
| Ecosystem | WebSearch | exa (`web_search_exa`) |

### Gemini Availability

```bash
which gemini
```

If absent, fallback to WebSearch for all gemini-assigned subtopics.

### Output

Create `.caw/research/<topic-slug>/plan.json`:

```json
{
  "topic": "<original topic>",
  "slug": "<topic-slug>",
  "created_at": "<ISO timestamp>",
  "subtopics": [
    {
      "id": 1,
      "question": "<focused subtopic question>",
      "type": "<library|comparison|broad|implementation|ecosystem>",
      "primary_tool": "<tool name>",
      "secondary_tool": "<tool name>",
      "status": "pending"
    }
  ]
}
```

## Stage 2: Parallel Investigation

Dispatch research for all subtopics in parallel. **MCP tools are called directly inline; non-MCP tools use Agent subagents.**

### Dispatch Rules

| Tool | Dispatch Method | Reason |
|------|----------------|--------|
| tavily | **Direct MCP call** (`mcp__tavily__tavily_research`) | MCP tools unavailable in Agent subagents |
| context7 | **Direct MCP call** (`resolve-library-id` → `query-docs`) | Same — MCP not inherited by subagents |
| exa | **Direct MCP call** (`mcp__exa__web_search_exa`) | Same — MCP not inherited by subagents |
| WebSearch | **Direct tool call** (built-in) | Built-in, works anywhere |
| gemini | **Agent subagent** → Bash: `gemini -p "..."` | CLI tool needs Bash execution context |

> **Parallel execution**: Call all MCP tools and Agent dispatches in a **single message** for maximum parallelism.
> Each MCP call can run concurrently. Agent subagents with `run_in_background: true` also run in parallel.

### Per-Subtopic Output

After each tool returns, **save results using Write tool** to `.caw/research/<slug>/subtopic-N-<name>.md`:

```markdown
# Subtopic N: <question>

## Key Findings
- <finding 1>
- <finding 2>

## Sources
- [<title>](<url>) — <relevance note>

## Confidence
<high|medium|low> — <rationale>

## Open Questions
- <unanswered question>
```

## Stage 3: Cross-Validation

Read all `subtopic-*.md` files and produce a cross-validation report.

Adapted from multi-model-debate Phase 3 synthesis pattern.

### Categories

1. **Agreements**: Claims appearing in 2+ subtopics with consistent evidence
2. **Contradictions**: Conflicting claims — flag with sources from each side
3. **Gaps**: Topics mentioned but inadequately researched
4. **Unsupported Claims**: Assertions without source backing

### Debate Integration (optional)

Check if `/debate:start` command is available.

- For **high-impact contradictions**: suggest `Run: /debate:start "{claim}" --context .caw/research/<slug>/`
- With `--debate` flag on explore: auto-invoke `/debate:start` for top 2 contradictions

### Output

Write `.caw/research/<slug>/cross-validation.md`:

```markdown
# Cross-Validation Report

## Agreements
- <claim> — supported by subtopics N, M (sources: ...)

## Contradictions
- <claim A> (subtopic N) vs <claim B> (subtopic M)
  - Sources: ...
  - Impact: <high|medium|low>
  - Suggested: /debate:start "<claim>" --context .caw/research/<slug>/

## Gaps
- <topic area> — mentioned in subtopic N but not investigated

## Unsupported Claims
- <claim> (subtopic N) — no source provided
```

## Stage 4: Synthesis

Read all subtopic files + `cross-validation.md`. Write final report.

### Output

Write `.caw/research/<slug>/RESEARCH-REPORT.md`:

```markdown
# Research Report: <topic>

| Field | Value |
|-------|-------|
| Topic | <topic> |
| Date | <ISO date> |
| Subtopics | <count> |
| Sources | <total unique sources> |
| Overall Confidence | <high|medium|low> |

## Executive Summary
<2-3 paragraph synthesis>

## Findings by Subtopic

### 1. <subtopic title>
<synthesized findings, cross-referenced with other subtopics>

### 2. <subtopic title>
...

## Cross-References
<connections and patterns across subtopics>

## Confidence Assessment
| Subtopic | Confidence | Rationale |
|----------|------------|-----------|
| ... | ... | ... |

## Contested Points
<contradictions from cross-validation, with both sides>

## Gaps & Future Research
<areas needing further investigation>

## Sources
<deduplicated list of all sources with URLs>
```

## Output Directory

```
.caw/research/<topic-slug>/
├── plan.json
├── subtopic-1-<name>.md
├── subtopic-2-<name>.md
├── ...
├── cross-validation.md
└── RESEARCH-REPORT.md
```

## Boundaries

- **Will**: Decompose topics, dispatch parallel research, cross-validate, synthesize
- **Won't**: Auto-invoke debate without `--debate` flag, exceed 5 parallel agents, research internal codebase (that's `--research --internal`)
