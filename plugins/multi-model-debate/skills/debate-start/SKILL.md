---
name: debate-start
description: "Start a multi-model debate on a software engineering topic. Use when the user invokes /debate:start with a topic to evaluate using Claude, Codex, and Gemini in parallel."
argument-hint: "<topic> [--context <files>] [--perspectives <p1,p2,p3>] [--rounds <N>]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
---

# Debate Start

Launch a structured multi-model debate with Claude, Codex, and Gemini.

## Instructions

1. **Parse arguments:**
   - `topic` (required): The debate topic or decision question
   - `--context <files>`: Comma-separated file paths or glob patterns to include as context
   - `--perspectives <p1,p2,p3>`: Custom perspective labels for each agent (Claude, Codex, Gemini)
   - `--rounds <N>`: Number of debate rounds (default: 2)

2. **Verify prerequisites:**
   - Check Codex CLI: run `which codex` via Bash
   - Check Gemini CLI: run `which gemini` via Bash
   - If either fails, report what's missing and stop

3. **Read context files** (if `--context` provided):
   - Resolve glob patterns with Glob tool
   - Read each file with Read tool
   - Concatenate as shared context for all agents

4. **Create output directory:**
   - Generate debate-id: `YYYYMMDD-HHMMSS-<topic-slug>` (slug: lowercase, hyphens, max 30 chars)
   - Create `.debate/<debate-id>/`

5. **Execute the `debate-orchestration` skill**, passing:
   - topic, context, perspectives, rounds, debate-id, output directory path

## Usage Examples

```
/debate:start "Should we use REST or GraphQL for our API?"
/debate:start "Monorepo vs polyrepo" --context src/package.json,docs/architecture.md
/debate:start "Next.js vs Remix vs Astro" --perspectives "Performance,DX,Ecosystem" --rounds 3
```
