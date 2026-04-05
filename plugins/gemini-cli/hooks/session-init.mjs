#!/usr/bin/env node

// SessionStart hook: check if Gemini CLI is installed and authenticated.

import { execFileSync } from "child_process";

function checkGemini() {
  try {
    const version = execFileSync("gemini", ["--version"], { encoding: "utf-8", timeout: 5000 }).trim();
    return { ok: true, version };
  } catch {
    return { ok: false };
  }
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
  console.log(JSON.stringify({ result: "continue" }));
}
