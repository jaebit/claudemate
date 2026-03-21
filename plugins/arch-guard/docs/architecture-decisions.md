# arch-guard Plugin — Architecture Decisions

## AD-1: Config-driven rules (not hardcoded)

**Decision**: All architecture rules come from `arch-guard.json`, not embedded in the plugin.

**Rationale**:
- Different projects have different layer structures
- Users define their own rules; the plugin enforces them
- Single config file as SSOT — same philosophy as arix-dev's `arix-rules.md`, but user-owned

---

## AD-2: JSON config format

**Decision**: Use JSON for `arch-guard.json`.

**Rationale**:
- Native `JSON.parse()` — no YAML dependency needed
- Hooks parse it directly without external libraries
- JSON Schema validation possible in editors (future)
- YAML would add complexity for marginal readability gain

---

## AD-3: Independent from arix-dev

**Decision**: No dependency between arch-guard and arix-dev. Both registered separately.

**Rationale**:
- arix-dev is the reference implementation with hardcoded Arix rules
- arch-guard is the generalization for any layered architecture
- Users may install either or both without conflicts
- Keeps each plugin focused and maintainable

---

## AD-4: Hooks never block (inherited from arix-dev)

**Decision**: All hooks return `result: "continue"`. No blocking.

**Rationale**:
- Blocking hooks disrupt development flow
- Information + warnings are sufficient for awareness
- Strong validation is explicit via `/arch-check`

---

## AD-5: Skills reference config, not hardcoded rules

**Decision**: Every skill reads `arch-guard.json` as its SSOT.

**Rationale**:
- Config IS the enforceable rules
- Skills interpret config + apply reasoning (LLM-driven)
- Changing rules requires only editing the config file, not the skills

---

## AD-6: .NET only for v0.1.0

**Decision**: Detection logic handles .NET patterns directly. No `lang/` strategy directory.

**Rationale**:
- .NET is the only validated use case from arix-dev
- Premature abstraction for multi-language support would be over-engineering
- Extension points exist (getSourceExtensions, detection patterns) for future languages
- Add language strategies when a second language is actually needed

---

## AD-7: Prompt-based implementation (inherited from arix-dev AD-2)

**Decision**: Skills are SKILL.md prompts, not programmatic scripts. Hooks handle only mechanical detection.

**Rationale**:
- Claude Code skills are prompt-based by design
- Complex architectural judgment is better handled by LLM reasoning
- Hooks do lightweight detection (layer identification, forbidden ref scanning)
- Skills do deep analysis (reading docs, evaluating compliance, generating reports)

---

## AD-8: v0.2.0 — Complete skill set and arch-reviewer agent

**Decision**: Add 7 skills (implement, impl-review, spec-sync, integration-map, track, tdd, test-gen) and 1 agent (arch-reviewer) to cover the full architecture enforcement lifecycle.

**Rationale**:
- v0.1.0 covered setup, scanning, scaffolding, contracts, and ADRs — the "define and create" phase
- v0.2.0 adds the "implement, verify, and track" phase for a complete workflow
- All new skills follow the same config-driven pattern: read `arch-guard.json` as SSOT
- The arch-reviewer agent provides a single-command comprehensive fitness report with scoring
- Scoring is config-driven via `config.scoring` — defaults provided if not configured
- Track skill requires `config.phases[]` — gracefully degrades if not defined
- No arix-specific concepts — all domain knowledge comes from the user's config and architecture docs
