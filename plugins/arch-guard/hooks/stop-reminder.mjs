#!/usr/bin/env node
// Stop hook: only active in arch-guard projects (those with arch-guard.json).
// Exits 0 silently in non-arch-guard projects to avoid global noise.
import { isConfiguredProject } from "../_shared/detect-project.mjs";

if (!isConfiguredProject(process.cwd())) {
  process.exit(0);
}

process.stdout.write(
  "If you modified source files (.cs, .csproj, .java, .py, .ts, etc.) in this response, " +
  "add a one-line reminder at the end: 'Architecture verification may be needed: /arch-check or /contract-first'. " +
  "Skip if no source files were modified.\n"
);
process.exit(2);
