#!/usr/bin/env node

// PreToolUse hook: Write|Edit — identify layer from file path and warn on forbidden references.

import { loadConfig } from "../_shared/load-config.mjs";
import { getLayer, getSubProject, checkForbiddenRef, getSourceExtensions } from "../_shared/detect-project.mjs";

const cwd = process.env.CWD || process.cwd();
const toolInput = process.env.TOOL_INPUT;

if (!toolInput) {
  console.log(JSON.stringify({ result: "continue" }));
  process.exit(0);
}

let parsed;
try {
  parsed = JSON.parse(toolInput);
} catch {
  console.log(JSON.stringify({ result: "continue" }));
  process.exit(0);
}

const filePath = parsed.file_path || "";

async function main() {
  const config = await loadConfig(cwd);
  if (!config) {
    console.log(JSON.stringify({ result: "continue" }));
    return;
  }

  const extensions = getSourceExtensions(config.project.language);
  if (!extensions.some((ext) => filePath.endsWith(ext))) {
    console.log(JSON.stringify({ result: "continue" }));
    return;
  }

  const sourceLayer = getLayer(filePath, config);
  if (!sourceLayer) {
    console.log(JSON.stringify({ result: "continue" }));
    return;
  }

  const sourceSubProject = getSubProject(filePath, config);
  const content = parsed.content || parsed.new_string || "";
  const violations = [];

  // Build detection patterns based on language
  const patterns = getDetectionPatterns(config.project.language);
  for (const pattern of patterns) {
    let match;
    while ((match = pattern.regex.exec(content)) !== null) {
      const targetName = match[1];
      // Try to identify target layer
      const targetLayer = config.layers.find((l) => {
        const base = l.pattern.replace(/\.\*$/, "").split(".").pop();
        return targetName.includes(base);
      });
      if (!targetLayer || targetLayer.name === sourceLayer.name) continue;

      const rule = checkForbiddenRef(sourceLayer, sourceSubProject, targetLayer.name, config);
      if (rule) {
        violations.push(`${sourceLayer.name} -> ${targetLayer.name}: ${rule}`);
      }
    }
  }

  const layerLabel = `L${sourceLayer.level || "?"} ${sourceLayer.name}`;
  let message = `[arch-guard] Layer: ${layerLabel}`;

  if (violations.length > 0) {
    const unique = [...new Set(violations)];
    message = `[arch-guard] Layer: ${layerLabel} | WARNING — forbidden references detected:\n${unique.map((v) => `  - ${v}`).join("\n")}`;
  }

  console.log(JSON.stringify({ result: "continue", message }));
}

function getDetectionPatterns(language) {
  switch (language) {
    case "dotnet":
      return [
        { regex: /using\s+([A-Za-z][A-Za-z0-9_.]+)/g },
        { regex: /ProjectReference[^>]*[\\\/]([A-Za-z][A-Za-z0-9_.]+)\./g },
      ];
    case "java":
      return [{ regex: /import\s+([A-Za-z][A-Za-z0-9_.]+)/g }];
    case "typescript":
      return [{ regex: /from\s+['"]([^'"]+)['"]/g }];
    default:
      return [];
  }
}

main().catch(() => {
  console.log(JSON.stringify({ result: "continue" }));
});
