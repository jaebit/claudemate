// Generic layer detection and forbidden reference checking for arch-guard.
// Config-driven replacement of arix-dev's detect-arix.mjs.

import { existsSync } from "fs";
import { join, dirname } from "path";

/**
 * Convert a glob-like pattern (e.g. "MyApp.Domain.*") to a RegExp.
 * Supports * as single-segment wildcard.
 */
function patternToRegex(pattern) {
  const escaped = pattern.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, "[A-Za-z0-9_]+");
  return new RegExp(escaped);
}

/**
 * Identify which layer a file path belongs to.
 * Returns the matching layer object or null.
 */
export function getLayer(filePath, config) {
  for (const layer of config.layers) {
    if (patternToRegex(layer.pattern).test(filePath)) return layer;
  }
  if (config.cross_cutting?.pattern && patternToRegex(config.cross_cutting.pattern).test(filePath)) {
    return { name: config.cross_cutting.label || "Cross-cutting", level: 0, pattern: config.cross_cutting.pattern, _type: "cross_cutting" };
  }
  if (config.hosts?.pattern && patternToRegex(config.hosts.pattern).test(filePath)) {
    return { name: "Host", level: 99, pattern: config.hosts.pattern, _type: "hosts" };
  }
  return null;
}

/**
 * Extract sub-project type from file path (e.g. "Contracts", "Domain", "Application").
 * Matches the segment after the layer identifier.
 */
export function getSubProject(filePath, config) {
  for (const layer of config.layers) {
    const base = layer.pattern.replace(/\.\*$/, "");
    const regex = new RegExp(base.replace(/[.+?^${}()|[\]\\]/g, "\\$&") + "\\.([A-Za-z0-9_]+)");
    const match = filePath.match(regex);
    if (match) return match[1];
  }
  return null;
}

/**
 * Check if a reference from source to target is forbidden.
 * Returns the rule reason string or null.
 */
export function checkForbiddenRef(sourceLayer, sourceSubProject, targetLayerName, config) {
  const forbidden = config.references?.forbidden || [];
  for (const rule of forbidden) {
    const fromMatch = matchesWildcard(sourceLayer.pattern, rule.from) ||
                      (sourceSubProject && matchesSubProjectWildcard(sourceSubProject, rule.from));
    const targets = Array.isArray(rule.to) ? rule.to : [rule.to];
    for (const target of targets) {
      if (fromMatch && matchesTarget(targetLayerName, target)) {
        return rule.reason || `Forbidden: ${rule.from} -> ${target}`;
      }
    }
  }

  // Check layer-level calls_forbidden
  if (sourceLayer.calls_forbidden) {
    const targetLayer = config.layers.find((l) => l.name === targetLayerName);
    if (targetLayer && sourceLayer.calls_forbidden.includes(targetLayer.level)) {
      return `Layer ${sourceLayer.name} (L${sourceLayer.level}) cannot reference L${targetLayer.level} ${targetLayer.name}`;
    }
  }

  // Check hosts no_inbound_refs
  if (config.hosts?.no_inbound_refs) {
    if (targetLayerName === "Host" || targetLayerName === "Hosts") {
      return "No project may reference Host projects";
    }
  }

  return null;
}

/**
 * Check if arch-guard.json exists in or above cwd.
 */
export function isConfiguredProject(cwd) {
  let dir = cwd;
  for (let i = 0; i < 4; i++) {
    if (existsSync(join(dir, "arch-guard.json"))) return true;
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return false;
}

/**
 * Get source file extensions for a language.
 */
export function getSourceExtensions(language) {
  const map = {
    dotnet: [".cs", ".csproj"],
    java: [".java", ".gradle", ".xml"],
    typescript: [".ts", ".tsx"],
    python: [".py"],
  };
  return map[language] || [];
}

// --- internal helpers ---

function matchesWildcard(value, pattern) {
  if (!pattern) return false;
  return patternToRegex(pattern).test(value);
}

function matchesSubProjectWildcard(subProject, pattern) {
  if (!pattern) return false;
  const subMatch = pattern.match(/^\*\.(.+)$/);
  if (subMatch) return subProject === subMatch[1];
  return false;
}

function matchesTarget(targetName, ruleTarget) {
  if (!ruleTarget) return false;
  if (targetName === ruleTarget) return true;
  const subMatch = ruleTarget.match(/^\*\.(.+)$/);
  if (subMatch) return targetName === subMatch[1] || targetName.endsWith(`.${subMatch[1]}`);
  return patternToRegex(ruleTarget).test(targetName);
}
