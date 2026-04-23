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

function checkGeminiAuth() {
  try {
    execFileSync("gemini", ["-p", ""], { encoding: "utf-8", timeout: 4000, stdio: ["ignore", "pipe", "pipe"] });
    return { ok: true };
  } catch (err) {
    const output = (err.stdout || "") + (err.stderr || "");
    const authKeywords = ["auth", "login", "authenticate", "credential", "unauthorized", "unauthenticated", "sign in", "not logged"];
    const isAuthError = authKeywords.some((kw) => output.toLowerCase().includes(kw));
    return { ok: false, isAuthError, output };
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
  const authResult = checkGeminiAuth();
  if (!authResult.ok && authResult.isAuthError) {
    console.log(JSON.stringify({
      result: "continue",
      additionalContext:
        "⚠️  gemini-cli: Gemini CLI is installed but not authenticated.\n" +
        "Run:  gemini auth login\n" +
        "Alt:  Set the GEMINI_API_KEY environment variable.\n" +
        "gemini:* commands will not work until authenticated.",
    }));
  } else {
    console.log(JSON.stringify({ result: "continue" }));
  }
}
