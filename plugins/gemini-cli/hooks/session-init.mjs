#!/usr/bin/env node

// SessionStart hook: check if Gemini CLI is installed and has credentials configured.
// Credentials check is FILE-/ENV-based (no API call) — avoids burning free-tier quota
// (~1,500/day per README) or paid-tier cost on every session.

import { execFileSync } from "child_process";
import { statSync } from "fs";
import { join } from "path";

function checkGemini() {
  try {
    const version = execFileSync("gemini", ["--version"], { encoding: "utf-8", timeout: 5000 }).trim();
    return { ok: true, version };
  } catch {
    return { ok: false };
  }
}

/**
 * Credentials are configured if any of the following is true:
 *   - `GEMINI_API_KEY` env var is set
 *   - `~/.config/gemini/` or `~/.gemini/` exists (CLI-created credentials directory)
 * No network / API call is made.
 */
function checkGeminiCredentials() {
  if (process.env.GEMINI_API_KEY && process.env.GEMINI_API_KEY.trim().length > 0) {
    return { configured: true, via: "GEMINI_API_KEY env" };
  }
  const home = process.env.HOME || process.env.USERPROFILE || "";
  const candidates = [
    join(home, ".config", "gemini"),
    join(home, ".gemini"),
  ];
  for (const candidate of candidates) {
    try {
      if (statSync(candidate).isDirectory()) {
        return { configured: true, via: candidate };
      }
    } catch {
      // continue
    }
  }
  return { configured: false };
}

const result = checkGemini();

if (!result.ok) {
  console.log(JSON.stringify({
    result: "continue",
    additionalContext:
      "⚠️  gemini-cli: Gemini CLI not found.\n" +
      "Install: brew install google-gemini/tap/gemini-cli\n" +
      "Auth:    gemini auth login\n" +
      "gemini:* commands will not work until installed.",
  }));
} else {
  const creds = checkGeminiCredentials();
  if (!creds.configured) {
    console.log(JSON.stringify({
      result: "continue",
      additionalContext:
        "⚠️  gemini-cli: Gemini CLI is installed but no credentials detected.\n" +
        "Run:  gemini auth login\n" +
        "Alt:  export GEMINI_API_KEY=<your-key>\n" +
        "(Checked: GEMINI_API_KEY env, ~/.config/gemini/, ~/.gemini/)\n" +
        "gemini:* commands will not work until authenticated.",
    }));
  } else {
    console.log(JSON.stringify({ result: "continue" }));
  }
}
