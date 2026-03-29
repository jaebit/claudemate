#!/usr/bin/env node

// Verify build output: check if git commits were produced during Phase 3.
// Called on SessionStart (record baseline) and SubagentStop (check for new commits).

import { readFile, writeFile } from "fs/promises";
import { join } from "path";
import { execFileSync } from "child_process";

const cwd = process.env.CWD || process.cwd();
const event = process.argv[2]; // "session-start" or "subagent-stop"
const verifyPath = join(cwd, ".autopilot", "build-verification.json");

function getCommitCount() {
  try {
    const out = execFileSync("git", ["rev-list", "--count", "HEAD"], { cwd, encoding: "utf-8" }).trim();
    return parseInt(out, 10) || 0;
  } catch {
    return 0;
  }
}

async function main() {
  if (event === "session-start") {
    // Only record baseline if .autopilot/ already exists (active pipeline)
    try {
      await readFile(join(cwd, ".autopilot", "state.json"), "utf-8");
    } catch {
      // No active autopilot pipeline — skip baseline recording
      return;
    }
    const count = getCommitCount();
    try {
      await writeFile(verifyPath, JSON.stringify({ baseline_commits: count, recorded_at: new Date().toISOString() }));
    } catch {}
    return;
  }

  if (event === "subagent-stop") {
    // Check if we're in build phase
    try {
      const stateRaw = await readFile(join(cwd, ".autopilot", "state.json"), "utf-8");
      const state = JSON.parse(stateRaw);
      if (state.phase !== "build" && state.phases?.build?.status !== "running") {
        return;
      }
    } catch {
      return;
    }

    // Compare commit count to baseline
    const currentCount = getCommitCount();
    let baseline = 0;
    try {
      const raw = await readFile(verifyPath, "utf-8");
      baseline = JSON.parse(raw).baseline_commits || 0;
    } catch {}

    const newCommits = currentCount - baseline;
    const result = {
      baseline_commits: baseline,
      current_commits: currentCount,
      new_commits: newCommits,
      verified_at: new Date().toISOString(),
      verdict: newCommits > 0 ? "PASS" : "WARNING"
    };

    await writeFile(verifyPath, JSON.stringify(result, null, 2));

    if (newCommits === 0) {
      console.log(JSON.stringify({
        additionalContext: `WARNING: Build agent produced 0 commits. Expected per-step [feat] commits. All changes are uncommitted. Run: git add -A && git commit -m "feat: build output"`
      }));
    }
  }
}

main().catch(() => {});
