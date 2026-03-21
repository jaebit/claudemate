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

  if (!state.phase || state.phase === "cancelled") {
    console.log(JSON.stringify({ result: "continue" }));
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
      console.log(JSON.stringify({ result: "continue" }));
    }
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
