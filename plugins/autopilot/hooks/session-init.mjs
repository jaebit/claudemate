#!/usr/bin/env node

// SessionStart hook:
//   1. Prerequisite check — verify crew/multi-model-debate/arch-guard/codex-cli are installed.
//   2. Detect .autopilot/state.json and print resume notice.

import { readFile } from "fs/promises";
import { join } from "path";
import { execFileSync } from "child_process";

const cwd = process.env.CWD || process.cwd();

// ---------------------------------------------------------------------------
// Step 1: Prerequisite probe
// ---------------------------------------------------------------------------

/**
 * Check whether a Claude plugin directory exists under the user's plugin roots.
 * We probe: ~/.claude/plugins/<name>  and  <repo>/.claude-plugin/<name>
 * Returns { installed: boolean, path: string|null }
 */
function probePlugin(name) {
  const os = process.env.HOME || process.env.USERPROFILE || "";
  const candidates = [
    join(os, ".claude", "plugins", name),
    join(os, ".claude", "plugins", "cache", "github.com", "jaebit", "claudemate", name),
    // local monorepo path (dev installs)
    join(cwd, "plugins", name),
  ];
  for (const candidate of candidates) {
    try {
      execFileSync("test", ["-d", candidate]);
      return { installed: true, path: candidate };
    } catch {
      // continue
    }
  }
  // Also try: claude plugins list output (graceful — may not be available)
  try {
    const out = execFileSync("claude", ["plugins", "list", "--json"], { encoding: "utf-8", timeout: 5000 });
    const list = JSON.parse(out);
    const found = (Array.isArray(list) ? list : list.plugins ?? []).find(
      (p) => p.name === name || p.id === name
    );
    if (found) return { installed: true, path: found.path ?? null };
  } catch {
    // claude CLI not available or flag unsupported — skip
  }
  return { installed: false, path: null };
}

function checkPrerequisites() {
  const deps = [
    { name: "crew",               required: true  },
    { name: "multi-model-debate", required: false },
    { name: "arch-guard",         required: false },
    { name: "codex-cli",          required: false },
  ];

  const missing_required = [];
  const missing_optional = [];
  const notices = [];

  for (const dep of deps) {
    const { installed } = probePlugin(dep.name);
    if (!installed) {
      if (dep.required) {
        missing_required.push(dep.name);
      } else {
        missing_optional.push(dep.name);
      }
    }
  }

  if (missing_required.length > 0) {
    notices.push(`# autopilot: Missing required dependency`);
    notices.push("");
    for (const name of missing_required) {
      notices.push(`- **${name}** is required. Install: \`claude plugins install ${name}\``);
    }
    notices.push("");
    notices.push("autopilot cannot run without required dependencies.");
    return { ok: false, notices };
  }

  if (missing_optional.length > 0) {
    notices.push(`# autopilot: Optional plugins not installed`);
    notices.push("");
    for (const name of missing_optional) {
      notices.push(`- **${name}** (optional): \`claude plugins install ${name}\``);
    }
    notices.push("");
    notices.push("autopilot will run with reduced capability (some phases will be skipped).");
  }

  return { ok: true, notices };
}

async function main() {
  // --- Prerequisite check ---
  const prereq = checkPrerequisites();
  if (!prereq.ok) {
    console.log(JSON.stringify({
      result: "continue",
      additionalContext: prereq.notices.join("\n"),
    }));
    return;
  }
  // Optional-plugin warnings surfaced only when an autopilot pipeline is active
  // (checked below after state.json probe — we'll hold the notices for now)
  const optionalWarnings = prereq.notices;
  const statePath = join(cwd, ".autopilot", "state.json");

  // --- State-file check ---
  let state;
  try {
    const raw = await readFile(statePath, "utf8");
    state = JSON.parse(raw);
  } catch {
    // No state file — nothing to resume
    // Still surface optional-plugin warnings so user knows before starting
    if (optionalWarnings.length > 0) {
      console.log(JSON.stringify({ result: "continue", additionalContext: optionalWarnings.join("\n") }));
    } else {
      console.log(JSON.stringify({ result: "continue" }));
    }
    return;
  }

  if (!state.phase || state.phase === "cancelled") {
    if (optionalWarnings.length > 0) {
      console.log(JSON.stringify({ result: "continue", additionalContext: optionalWarnings.join("\n") }));
    } else {
      console.log(JSON.stringify({ result: "continue" }));
    }
    return;
  }

  // Complete with gaps: show remaining work notice
  if (state.phase === "complete") {
    const missing = state.completion?.missing ?? 0;
    if (missing > 0) {
      const topic = state.topic || "(unknown)";
      const built = state.completion?.built ?? 0;
      const total = state.completion?.total ?? 0;
      const lines = [
        ...(optionalWarnings.length > 0 ? [...optionalWarnings, "---", ""] : []),
        `# autopilot: Pipeline completed with gaps`,
        "",
        `- **Topic**: ${topic}`,
        `- **Built**: ${built}/${total} deliverables`,
        `- **Missing**: ${missing} (see .autopilot/remaining-work.md)`,
        "",
        `Resume gap-filling: \`/autopilot --continue\``,
      ];
      console.log(JSON.stringify({
        result: "continue",
        additionalContext: lines.join("\n"),
      }));
    } else {
      if (optionalWarnings.length > 0) {
        console.log(JSON.stringify({ result: "continue", additionalContext: optionalWarnings.join("\n") }));
      } else {
        console.log(JSON.stringify({ result: "continue" }));
      }
    }
    return;
  }

  const topic = state.topic || "(unknown)";
  const phase = state.phase;
  const started = state.started_at ? ` (started ${state.started_at})` : "";

  const lines = [
    ...(optionalWarnings.length > 0 ? [...optionalWarnings, "---", ""] : []),
    `# autopilot: Incomplete pipeline detected`,
    "",
    `- **Topic**: ${topic}`,
    `- **Paused at**: ${phase}${started}`,
    "",
    `Resume with: \`/autopilot --continue\``,
  ];

  console.log(JSON.stringify({
    result: "continue",
    additionalContext: lines.join("\n"),
  }));
}

main().catch(() => {
  console.log(JSON.stringify({ result: "continue" }));
});
