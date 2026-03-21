#!/usr/bin/env node

// SessionStart hook: inject compressed rule summary from arch-guard.json as additionalContext.

import { dirname } from "path";
import { fileURLToPath } from "url";
import { loadConfig } from "../_shared/load-config.mjs";

const cwd = process.env.CWD || process.cwd();

async function main() {
  const config = await loadConfig(cwd);
  if (!config) {
    console.log(JSON.stringify({ result: "continue" }));
    return;
  }

  const lines = [
    `# arch-guard: ${config.project.name} (${config.project.language}) — Rule Summary`,
    "",
    "## Layers",
  ];

  for (const layer of config.layers) {
    const allowed = layer.calls_allowed ? `allowed→L${layer.calls_allowed.join(",")}` : "";
    const forbidden = layer.calls_forbidden ? `forbidden→L${layer.calls_forbidden.join(",")}` : "";
    const passive = layer.passive ? " (passive)" : "";
    lines.push(`- L${layer.level} ${layer.name}${passive}: ${[allowed, forbidden].filter(Boolean).join(" | ")}`);
  }

  if (config.references?.forbidden?.length) {
    lines.push("", "## Forbidden References");
    for (const ref of config.references.forbidden) {
      const targets = Array.isArray(ref.to) ? ref.to.join(", ") : ref.to;
      lines.push(`- ${ref.from} → ${targets}: ${ref.reason}`);
    }
  }

  if (config.forbidden_patterns?.length) {
    lines.push("", "## Forbidden Patterns");
    for (const fp of config.forbidden_patterns) {
      lines.push(`- ${fp.name}: ${fp.description}`);
    }
  }

  if (config.contracts?.enabled) {
    lines.push("", "## Contracts-First", `- Suffix: ${config.contracts.project_suffix}`);
  }

  lines.push(
    "",
    "## Work Process",
    "- At design decision points (approach A vs B, interface choices, etc.): present options and ask",
    "- On user answer: proceed immediately with implementation — no additional confirmation",
    "- Items that can proceed without user decision: just proceed without asking",
    "- If exit criteria remain: suggest the next item and continue unless the user declines",
    "",
    `Verify: /arch-check | Design: /contract-first | Scaffold: /scaffold`,
  );

  console.log(JSON.stringify({
    result: "continue",
    additionalContext: lines.join("\n"),
  }));
}

main().catch(() => {
  console.log(JSON.stringify({ result: "continue" }));
});
