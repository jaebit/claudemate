#!/usr/bin/env node

// PreToolUse hook (Write only): check if the layer's Contracts project exists when creating new source files.

import { existsSync } from "fs";
import { join } from "path";
import { loadConfig } from "../_shared/load-config.mjs";
import { getLayer, getSubProject, getSourceExtensions } from "../_shared/detect-project.mjs";

const cwd = process.env.CWD || process.cwd();
const toolName = process.env.TOOL_NAME || "";
const toolInput = process.env.TOOL_INPUT;

// Only target Write tool (Edit is for existing files)
if (toolName !== "Write" || !toolInput) {
  console.log(JSON.stringify({ result: "continue" }));
  process.exit(0);
}

let filePath;
try {
  filePath = JSON.parse(toolInput).file_path || "";
} catch {
  console.log(JSON.stringify({ result: "continue" }));
  process.exit(0);
}

async function main() {
  const config = await loadConfig(cwd);
  if (!config || !config.contracts?.enabled) {
    console.log(JSON.stringify({ result: "continue" }));
    return;
  }

  // Only check source files (not project files)
  const srcExts = getSourceExtensions(config.project.language).filter((e) => e !== ".csproj" && e !== ".xml" && e !== ".gradle");
  if (!srcExts.some((ext) => filePath.endsWith(ext))) {
    console.log(JSON.stringify({ result: "continue" }));
    return;
  }

  const layer = getLayer(filePath, config);
  const subProject = getSubProject(filePath, config);

  if (!layer || layer._type === "cross_cutting" || layer._type === "hosts") {
    console.log(JSON.stringify({ result: "continue" }));
    return;
  }

  // Skip if writing to Contracts itself
  const suffix = config.contracts.project_suffix || "Contracts";
  if (subProject === suffix) {
    console.log(JSON.stringify({ result: "continue" }));
    return;
  }

  // Derive the contracts project directory name from the layer pattern
  const layerBase = layer.pattern.replace(/\.\*$/, "");
  const contractsName = `${layerBase}.${suffix}`;
  const sourceRoot = config.project.source_root || "src/";
  const projectRoot = config._configDir || cwd;
  const contractsDir = join(projectRoot, sourceRoot, contractsName);

  if (!existsSync(contractsDir)) {
    console.log(JSON.stringify({
      result: "continue",
      message: `[arch-guard] WARNING: ${contractsName} does not exist. Consider running /scaffold to create it first (Contracts-first principle).`,
    }));
  } else {
    console.log(JSON.stringify({ result: "continue" }));
  }
}

main().catch(() => {
  console.log(JSON.stringify({ result: "continue" }));
});
