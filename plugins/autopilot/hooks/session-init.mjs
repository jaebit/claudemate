#!/usr/bin/env node

// SessionStart hook: detect .autopilot/state.json and print resume notice.

import { readFile } from "fs/promises";
import { join } from "path";

const cwd = process.env.CWD || process.cwd();

async function main() {
  const statePath = join(cwd, ".autopilot", "state.json");

  let state;
  try {
    const raw = await readFile(statePath, "utf8");
    state = JSON.parse(raw);
  } catch {
    // No state file — nothing to resume
    console.log(JSON.stringify({ result: "continue" }));
    return;
  }

  if (!state.phase || state.phase === "complete" || state.phase === "cancelled") {
    console.log(JSON.stringify({ result: "continue" }));
    return;
  }

  const topic = state.topic || "(unknown)";
  const phase = state.phase;
  const started = state.started_at ? ` (started ${state.started_at})` : "";

  const lines = [
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
