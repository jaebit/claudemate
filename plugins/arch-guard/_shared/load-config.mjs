// Find and parse arch-guard.json from CWD, walking up to 3 parent directories.

import { readFile } from "fs/promises";
import { existsSync } from "fs";
import { join, dirname } from "path";

/**
 * Walk up from cwd looking for arch-guard.json.
 * Returns parsed config object or null if not found / invalid.
 */
export async function loadConfig(cwd) {
  let dir = cwd;
  for (let i = 0; i < 4; i++) {
    const configPath = join(dir, "arch-guard.json");
    if (existsSync(configPath)) {
      try {
        const raw = await readFile(configPath, "utf-8");
        const config = JSON.parse(raw);
        if (!validate(config)) return null;
        config._configDir = dir;
        return config;
      } catch {
        return null;
      }
    }
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

/**
 * Validate required fields in config.
 */
function validate(config) {
  if (!config.version) return false;
  if (!config.project?.language) return false;
  if (!Array.isArray(config.layers) || config.layers.length === 0) return false;
  return true;
}
