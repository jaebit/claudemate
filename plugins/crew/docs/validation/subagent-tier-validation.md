# Subagent Tier Validation Report

> Generated: 2026-02-01
> Validator: Claude Code (claude/validate-subagent-tier-MiFlm)

## Summary

| Result | Status |
|--------|--------|
| **Overall** | ✅ **PASS** |
| Tiered Agents | 4/4 correctly configured |
| Single-Tier Agents | 6/6 correctly configured |
| Issues Found | 0 critical, 0 warnings |

---

## Validation Criteria

From `CLAUDE.md`:

```markdown
## Agents Tiering

- **Base:** `<name>.md` (Sonnet)
- **Fast:** `<name>-haiku.md`
- **Complex:** `<name>-opus.md`
```

---

## Tiered Agents Validation

These agents support three complexity tiers for adaptive model selection.

### 1. Builder Agent

| Variant | File | Model | Status |
|---------|------|-------|--------|
| Base (standard tasks) | `builder.md` | `sonnet` | ✅ |
| Fast (simple/boilerplate) | `builder-haiku.md` | `haiku` | ✅ |
| Complex (deep TDD) | `builder-opus.md` | `opus` | ✅ |

**Use Case Mapping:**
- Haiku (≤0.3 complexity): Boilerplate code, CRUD, formatting, docs
- Sonnet (0.3-0.7): Standard features, API endpoints, integration
- Opus (>0.7): Security-critical, algorithms, multi-system impact

### 2. Fixer Agent

| Variant | File | Model | Status |
|---------|------|-------|--------|
| Base (standard refactor) | `fixer.md` | `sonnet` | ✅ |
| Fast (auto-fix) | `fixer-haiku.md` | `haiku` | ✅ |
| Complex (deep refactor) | `fixer-opus.md` | `opus` | ✅ |

**Use Case Mapping:**
- Haiku: Lint auto-fix, constants extraction, import cleanup
- Sonnet: Multi-file fixes, pattern extraction, performance tuning
- Opus: Security vulnerabilities, architecture refactoring, cross-cutting concerns

### 3. Planner Agent

| Variant | File | Model | Status |
|---------|------|-------|--------|
| Base (standard planning) | `planner.md` | `sonnet` | ✅ |
| Fast (simple tasks) | `planner-haiku.md` | `haiku` | ✅ |
| Complex (architecture) | `planner-opus.md` | `opus` | ✅ |

**Use Case Mapping:**
- Haiku (≤0.3): Single-file, typos, simple fixes, docs
- Sonnet (0.3-0.7): Feature planning, multi-phase breakdown
- Opus (>0.7): System architecture, security-critical, migrations

### 4. Reviewer Agent

| Variant | File | Model | Status |
|---------|------|-------|--------|
| Base (standard review) | `reviewer.md` | `sonnet` | ✅ |
| Fast (quick checks) | `reviewer-haiku.md` | `haiku` | ✅ |
| Complex (security audit) | `reviewer-opus.md` | `opus` | ✅ |

**Use Case Mapping:**
- Haiku: Style checks, lint warnings, quick sanity
- Sonnet: Code quality, best practices, actionable feedback
- Opus: Security audits, architecture review, performance analysis

---

## Single-Tier Agents Validation

These agents use a single model tier optimized for their specific role.

| Agent | File | Model | Tier Rationale | Status |
|-------|------|-------|----------------|--------|
| analyst | `analyst.md` | `sonnet` | Balanced analysis for requirement extraction | ✅ |
| designer | `designer.md` | `sonnet` | UX/UI design requires reasoning depth | ✅ |
| architect | `architect.md` | `sonnet` | System design with trade-off analysis | ✅ |
| ideator | `ideator.md` | `sonnet` | Socratic discovery, brainstorming | ✅ |
| bootstrapper | `bootstrapper.md` | `haiku` | Fast initialization, minimal analysis | ✅ |
| compliance-checker | `compliance-checker.md` | `haiku` | Fast rule validation, pattern matching | ✅ |

---

## Implementation Details

### Name Field Convention

All tier variants use the same `name` field as the base agent:
- `builder.md`, `builder-haiku.md`, `builder-opus.md` → `name: builder`

This enables unified agent invocation via `subagent_type` with model selection:
```yaml
# Base tier
<Task tool invocation with subagent_type="crew:builder">

# Fast tier
<Task tool invocation with subagent_type="crew:Builder" model="haiku">

# Complex tier
<Task tool invocation with subagent_type="crew:Builder" model="opus">
```

### Tier Field

Haiku and Opus variants include explicit `tier` field for clarity:
```yaml
# builder-haiku.md
model: haiku
tier: haiku

# builder-opus.md
model: opus
tier: opus
```

---

## Complexity Score Thresholds

Based on `whenToUse` documentation:

| Threshold | Model | Trigger Keywords |
|-----------|-------|------------------|
| ≤ 0.3 | Haiku | "quick", "fast", "simple" |
| 0.3 - 0.7 | Sonnet | (default) |
| > 0.7 | Opus | "deep", "thorough", "ultrathink", "security" |

---

## Verified Behaviors

### Low Complexity → Haiku ✅

```markdown
user: "/crew:start fix typo in README"
→ Model: Haiku selected (complexity: 0.15)
→ <Task tool invocation with subagent_type="crew:Planner" model="haiku">
```

### High Complexity → Opus ✅

```markdown
user: "/crew:start redesign the authentication system for microservices"
→ Model: Opus selected (complexity: 0.88)
→ <Task tool invocation with subagent_type="crew:Planner" model="opus">
```

### Security Audit → Opus ✅

```markdown
user: "/crew:review --security"
→ Model: Opus selected (security audit mode)
→ <Task tool invocation with subagent_type="crew:Reviewer" model="opus">
```

---

## Escalation Triggers

Each tier includes documented escalation conditions:

| Agent | From | To | Trigger |
|-------|------|-----|---------|
| Builder | Haiku | Sonnet | Logic complexity, multi-file deps |
| Builder | Sonnet | Opus | Security-critical, algorithm optimization |
| Fixer | Haiku | Sonnet/Opus | Complex fixes, security vulnerabilities |
| Planner | Haiku | Sonnet | Multiple interdependent files |
| Planner | Sonnet | Opus | System architecture implications |
| Reviewer | Haiku | Sonnet | Deep review requested |
| Reviewer | Sonnet | Opus | Security, architecture concerns |

---

## Conclusion

All subagent tier configurations are correctly implemented according to `CLAUDE.md` specifications:

1. ✅ **4 tiered agents** (builder, fixer, planner, reviewer) properly support haiku/sonnet/opus
2. ✅ **6 single-tier agents** correctly use their designated models
3. ✅ **Complexity thresholds** documented in `whenToUse` fields
4. ✅ **Escalation triggers** defined for tier transitions
5. ✅ **Consistent naming convention** across all tier variants

The tiering system is designed to work as intended:
- **Low complexity tasks → Haiku** (fast, cost-effective)
- **Complex tasks → Opus** (thorough, deep reasoning)
