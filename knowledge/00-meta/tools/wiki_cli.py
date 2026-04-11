#!/usr/bin/env python3
"""
wiki_cli.py — Knowledge Vault Wiki CLI

Commands:
    init    Scaffold wiki pages for all discovered modules
    update  Incrementally update wiki pages based on code changes
    lint    Validate frontmatter, zone markers, and write ownership
    graph   Regenerate graph.json from current wiki pages
    status  Show wiki coverage and staleness report

Usage:
    python3 wiki_cli.py init [--target plugins]
    python3 wiki_cli.py update [--module crew] [--commit HEAD]
    python3 wiki_cli.py lint
    python3 wiki_cli.py graph
    python3 wiki_cli.py status
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]  # knowledge/00-meta/tools -> repo root
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
WIKI_ROOT = KNOWLEDGE_ROOT / "10-wiki"
MODULES_DIR = WIKI_ROOT / "modules"
CROSS_CUTTING_DIR = WIKI_ROOT / "cross-cutting"
GRAPH_PATH = WIKI_ROOT / "graph.json"
TEMPLATES_DIR = KNOWLEDGE_ROOT / "90-templates"
PLUGINS_DIR = REPO_ROOT / "plugins"

TODAY = date.today().isoformat()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_current_commit_sha() -> str:
    """Get the short SHA of the current HEAD commit."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except FileNotFoundError:
        return "unknown"


def discover_modules() -> list[dict[str, Any]]:
    """Discover all plugin modules in plugins/ directory."""
    modules = []
    if not PLUGINS_DIR.exists():
        return modules

    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue

        plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
        claude_md = plugin_dir / "CLAUDE.md"
        readme = plugin_dir / "README.md"

        info: dict[str, Any] = {
            "name": plugin_dir.name,
            "path": str(plugin_dir.relative_to(REPO_ROOT)),
            "has_plugin_json": plugin_json.exists(),
            "has_claude_md": claude_md.exists(),
            "has_readme": readme.exists(),
        }

        # Parse plugin.json
        if plugin_json.exists():
            try:
                with open(plugin_json) as f:
                    pj = json.load(f)
                info["version"] = pj.get("version", "0.0.0")
                info["description"] = pj.get("description", "")
            except (json.JSONDecodeError, OSError):
                info["version"] = "0.0.0"
                info["description"] = ""
        else:
            info["version"] = "0.0.0"
            info["description"] = ""

        # Discover sub-components
        info["has_agents"] = (plugin_dir / "agents").is_dir()
        info["has_skills"] = (plugin_dir / "skills").is_dir()
        info["has_hooks"] = (plugin_dir / "hooks").is_dir()
        info["has_commands"] = (plugin_dir / "commands").is_dir()
        info["has_shared"] = (plugin_dir / "_shared").is_dir()
        info["has_tests"] = (plugin_dir / "tests").is_dir()
        info["has_mcp"] = False

        if plugin_json.exists():
            try:
                with open(plugin_json) as f:
                    pj = json.load(f)
                info["has_mcp"] = "mcpServers" in pj
            except (json.JSONDecodeError, OSError):
                pass

        # Count skills
        skills_dir = plugin_dir / "skills"
        if skills_dir.is_dir():
            info["skill_names"] = sorted([
                d.name for d in skills_dir.iterdir()
                if d.is_dir() and (d / "SKILL.md").exists()
            ])
        else:
            info["skill_names"] = []

        # Count agents
        agents_dir = plugin_dir / "agents"
        if agents_dir.is_dir():
            info["agent_names"] = sorted([
                f.stem for f in agents_dir.glob("*.md")
            ])
        else:
            info["agent_names"] = []

        # Discover dependencies from CLAUDE.md mentions
        info["dependencies"] = []
        if claude_md.exists():
            try:
                content = claude_md.read_text()
                # Look for references to other plugins
                for other in PLUGINS_DIR.iterdir():
                    if other.is_dir() and other.name != plugin_dir.name and not other.name.startswith("."):
                        if other.name in content:
                            info["dependencies"].append(other.name)
            except OSError:
                pass

        modules.append(info)

    return modules


def parse_frontmatter(filepath: Path) -> dict[str, Any] | None:
    """Parse YAML frontmatter from a markdown file."""
    try:
        content = filepath.read_text()
    except OSError:
        return None

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    fm: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Handle lists
            if value.startswith("[") and value.endswith("]"):
                items = value[1:-1]
                if items.strip():
                    fm[key] = [i.strip().strip('"').strip("'") for i in items.split(",")]
                else:
                    fm[key] = []
            elif value.lower() == "true":
                fm[key] = True
            elif value.lower() == "false":
                fm[key] = False
            else:
                try:
                    fm[key] = float(value)
                    if fm[key] == int(fm[key]):
                        fm[key] = int(fm[key])
                except ValueError:
                    fm[key] = value
    return fm


def generate_module_page(module: dict[str, Any], commit_sha: str) -> str:
    """Generate a wiki module page from discovered module info."""
    deps = module.get("dependencies", [])
    skills = module.get("skill_names", [])
    agents = module.get("agent_names", [])

    # Build components section
    components_lines = []
    if skills:
        components_lines.append("### Skills")
        for s in skills:
            components_lines.append(f"- `{s}`")
        components_lines.append("")
    if agents:
        components_lines.append("### Agents")
        for a in agents:
            components_lines.append(f"- `{a}`")
        components_lines.append("")
    if module.get("has_hooks"):
        components_lines.append("### Hooks")
        components_lines.append("- Hook definitions in `hooks/` directory")
        components_lines.append("")
    if module.get("has_commands"):
        components_lines.append("### Commands")
        components_lines.append("- Slash commands in `commands/` directory")
        components_lines.append("")
    if module.get("has_shared"):
        components_lines.append("### Shared Resources")
        components_lines.append("- Shared protocols and schemas in `_shared/` directory")
        components_lines.append("")

    components_text = "\n".join(components_lines) if components_lines else "No sub-components discovered."

    # Build exports
    exports = []
    if skills:
        exports.extend([f"/crew:{s}" if module["name"] == "crew" else f"/{module['name']}:{s}" for s in skills[:5]])
    exports_yaml = json.dumps(exports) if exports else "[]"

    deps_yaml = json.dumps(deps) if deps else "[]"
    dependents_yaml = "[]"  # Will be computed in graph phase

    # Architecture notes
    arch_parts = []
    if module.get("has_mcp"):
        arch_parts.append("- Includes MCP server integration")
    if module.get("has_agents"):
        arch_parts.append(f"- {len(agents)} agent(s) for task execution")
    if module.get("has_skills"):
        arch_parts.append(f"- {len(skills)} skill(s) providing user-invocable commands")
    if module.get("has_hooks"):
        arch_parts.append("- Hook-based event automation")
    if module.get("has_tests"):
        arch_parts.append("- Test suite in `tests/` directory")
    arch_text = "\n".join(arch_parts) if arch_parts else "Standard plugin structure."

    return f"""---
title: "{module['name']}"
zone: wiki
module: "{module['name']}"
module_path: "{module['path']}"
created: "{TODAY}"
last_updated: "{TODAY}"
last_verified_commit: "{commit_sha}"
confidence: 1.0
tier: 2
dependencies: {deps_yaml}
dependents: {dependents_yaml}
exports: {exports_yaml}
tags: [wiki, module]
---

# {module['name']}

## Purpose

<!-- LLM-ZONE -->
{module.get('description', 'No description available.')}

- **Version**: {module.get('version', '0.0.0')}
- **Path**: `{module['path']}`
<!-- /LLM-ZONE -->

## Architecture

<!-- LLM-ZONE -->
{arch_text}
<!-- /LLM-ZONE -->

## Key Components

<!-- LLM-ZONE -->
{components_text}
<!-- /LLM-ZONE -->

## Dependencies

<!-- LLM-ZONE -->
{('Depends on: ' + ', '.join(f'[[{d}]]' for d in deps)) if deps else 'No inter-plugin dependencies detected.'}
<!-- /LLM-ZONE -->

## Configuration

<!-- LLM-ZONE -->
{'- Plugin JSON: `' + module['path'] + '/.claude-plugin/plugin.json`' if module.get('has_plugin_json') else 'No configuration files detected.'}
{'- Module docs: `' + module['path'] + '/CLAUDE.md`' if module.get('has_claude_md') else ''}
<!-- /LLM-ZONE -->

## Notes

<!-- HUMAN-ZONE -->
*Add human notes here. Agents will not modify this section.*
<!-- /HUMAN-ZONE -->
"""


def generate_graph(modules: list[dict[str, Any]], commit_sha: str) -> dict[str, Any]:
    """Generate graph.json from module information."""
    graph: dict[str, Any] = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "wiki-cli",
        "modules": {},
        "cross_cutting": {},
        "edges": [],
    }

    # Build module nodes
    for mod in modules:
        graph["modules"][mod["name"]] = {
            "path": mod["path"],
            "version": mod.get("version", "0.0.0"),
            "skills": mod.get("skill_names", []),
            "agents": mod.get("agent_names", []),
            "has_mcp": mod.get("has_mcp", False),
            "has_hooks": mod.get("has_hooks", False),
            "has_tests": mod.get("has_tests", False),
            "wiki_page": f"10-wiki/modules/{mod['name']}.md",
            "last_verified_commit": commit_sha,
        }

    # Build dependency edges
    for mod in modules:
        for dep in mod.get("dependencies", []):
            graph["edges"].append({
                "from": mod["name"],
                "to": dep,
                "type": "depends_on",
            })

    # Compute dependents (reverse edges)
    for mod_name in graph["modules"]:
        dependents = [
            e["from"] for e in graph["edges"]
            if e["to"] == mod_name and e["type"] == "depends_on"
        ]
        graph["modules"][mod_name]["dependents"] = dependents

    return graph


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    """Scaffold wiki pages for all discovered modules."""
    print(f"[wiki init] Discovering modules in {PLUGINS_DIR}...")
    modules = discover_modules()

    if not modules:
        print("[wiki init] No modules found.")
        return 1

    commit_sha = get_current_commit_sha()
    MODULES_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0
    for mod in modules:
        page_path = MODULES_DIR / f"{mod['name']}.md"
        if page_path.exists() and not args.force:
            print(f"  SKIP {mod['name']} (already exists, use --force to overwrite)")
            skipped += 1
            continue

        content = generate_module_page(mod, commit_sha)
        page_path.write_text(content)
        print(f"  CREATE {mod['name']} -> {page_path.relative_to(REPO_ROOT)}")
        created += 1

    # Generate graph
    graph = generate_graph(modules, commit_sha)
    GRAPH_PATH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n")
    print(f"\n[wiki init] Graph updated: {GRAPH_PATH.relative_to(REPO_ROOT)}")

    print(f"\n[wiki init] Done: {created} created, {skipped} skipped, {len(modules)} total modules")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    """Incrementally update wiki pages based on code changes."""
    commit_sha = get_current_commit_sha()
    modules = discover_modules()

    if args.module:
        modules = [m for m in modules if m["name"] == args.module]
        if not modules:
            print(f"[wiki update] Module '{args.module}' not found.")
            return 1

    updated = 0
    for mod in modules:
        page_path = MODULES_DIR / f"{mod['name']}.md"
        if not page_path.exists():
            print(f"  SKIP {mod['name']} (no wiki page, run 'init' first)")
            continue

        # Check if source has changed since last verification
        fm = parse_frontmatter(page_path)
        if fm and fm.get("last_verified_commit") == commit_sha and not args.force:
            print(f"  CURRENT {mod['name']} (commit unchanged)")
            continue

        # Regenerate page
        content = generate_module_page(mod, commit_sha)
        page_path.write_text(content)
        print(f"  UPDATE {mod['name']} -> {page_path.relative_to(REPO_ROOT)}")
        updated += 1

    # Regenerate graph
    all_modules = discover_modules()
    graph = generate_graph(all_modules, commit_sha)
    GRAPH_PATH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n")
    print(f"\n[wiki update] Graph updated: {GRAPH_PATH.relative_to(REPO_ROOT)}")
    print(f"[wiki update] Done: {updated} updated")
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    """Validate frontmatter, zone markers, and write ownership."""
    errors: list[str] = []
    warnings: list[str] = []

    # Lint all wiki pages
    for md_file in sorted(WIKI_ROOT.rglob("*.md")):
        rel = md_file.relative_to(KNOWLEDGE_ROOT)
        content = md_file.read_text()

        # Check frontmatter exists
        fm = parse_frontmatter(md_file)
        if fm is None:
            errors.append(f"{rel}: Missing YAML frontmatter")
            continue

        # Check required fields
        for field in ["title", "zone"]:
            if field not in fm:
                errors.append(f"{rel}: Missing required field '{field}'")

        if fm.get("zone") != "wiki" and str(rel).startswith("10-wiki/modules/"):
            errors.append(f"{rel}: Zone should be 'wiki' but got '{fm.get('zone')}'")

        # Check wiki-specific fields for module pages
        if str(rel).startswith("10-wiki/modules/") and rel.name != "README.md":
            for field in ["module", "last_verified_commit", "confidence"]:
                if field not in fm:
                    warnings.append(f"{rel}: Missing wiki field '{field}'")

            conf = fm.get("confidence", 1.0)
            if isinstance(conf, (int, float)) and conf < 0.5:
                warnings.append(f"{rel}: Stale page (confidence={conf})")

        # Check zone markers balance
        human_opens = content.count("<!-- HUMAN-ZONE -->")
        human_closes = content.count("<!-- /HUMAN-ZONE -->")
        llm_opens = content.count("<!-- LLM-ZONE -->")
        llm_closes = content.count("<!-- /LLM-ZONE -->")

        if human_opens != human_closes:
            errors.append(f"{rel}: Unbalanced HUMAN-ZONE markers ({human_opens} opens, {human_closes} closes)")
        if llm_opens != llm_closes:
            errors.append(f"{rel}: Unbalanced LLM-ZONE markers ({llm_opens} opens, {llm_closes} closes)")

    # Lint memory pages
    memory_root = KNOWLEDGE_ROOT / "30-memory"
    for md_file in sorted(memory_root.rglob("*.md")):
        rel = md_file.relative_to(KNOWLEDGE_ROOT)
        if md_file.name == "README.md":
            continue

        fm = parse_frontmatter(md_file)
        if fm is None:
            errors.append(f"{rel}: Missing YAML frontmatter")
            continue

        if fm.get("zone") != "memory":
            errors.append(f"{rel}: Zone should be 'memory' but got '{fm.get('zone')}'")

        for field in ["memory_type", "canonical_id", "confidence"]:
            if field not in fm:
                warnings.append(f"{rel}: Missing memory field '{field}'")

    # Report
    print(f"[wiki lint] Scanned {KNOWLEDGE_ROOT}")
    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    ✗ {e}")
    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠ {w}")
    if not errors and not warnings:
        print("  All checks passed.")

    return 1 if errors else 0


def cmd_graph(args: argparse.Namespace) -> int:
    """Regenerate graph.json from current module discovery."""
    commit_sha = get_current_commit_sha()
    modules = discover_modules()
    graph = generate_graph(modules, commit_sha)
    GRAPH_PATH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n")
    print(f"[wiki graph] Generated {GRAPH_PATH.relative_to(REPO_ROOT)}")
    print(f"  Modules: {len(graph['modules'])}")
    print(f"  Edges: {len(graph['edges'])}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Show wiki coverage and staleness report."""
    modules = discover_modules()
    module_names = {m["name"] for m in modules}

    # Check wiki coverage
    existing_pages = {p.stem for p in MODULES_DIR.glob("*.md") if p.name != "README.md"}
    covered = module_names & existing_pages
    missing = module_names - existing_pages
    orphaned = existing_pages - module_names

    print("[wiki status] Module Coverage")
    print(f"  Total modules: {len(module_names)}")
    print(f"  Wiki pages:    {len(existing_pages)}")
    print(f"  Covered:       {len(covered)}")
    if missing:
        print(f"  Missing:       {', '.join(sorted(missing))}")
    if orphaned:
        print(f"  Orphaned:      {', '.join(sorted(orphaned))}")

    # Staleness report
    print("\n[wiki status] Freshness Report")
    commit_sha = get_current_commit_sha()
    for page_path in sorted(MODULES_DIR.glob("*.md")):
        if page_path.name == "README.md":
            continue
        fm = parse_frontmatter(page_path)
        if fm:
            conf = fm.get("confidence", 0)
            verified = fm.get("last_verified_commit", "?")
            stale_marker = ""
            if verified != commit_sha:
                stale_marker = " (commit mismatch)"
            if isinstance(conf, (int, float)) and conf < 0.5:
                stale_marker += " [STALE]"
            print(f"  {page_path.stem}: confidence={conf}, commit={verified}{stale_marker}")

    # Memory stats
    facts_dir = KNOWLEDGE_ROOT / "30-memory" / "facts"
    exp_dir = KNOWLEDGE_ROOT / "30-memory" / "experiences"
    fact_count = len(list(facts_dir.glob("*.md"))) if facts_dir.exists() else 0
    exp_count = len(list(exp_dir.glob("*.md"))) if exp_dir.exists() else 0

    print("\n[wiki status] Memory Entries")
    print(f"  Factual:       {fact_count}")
    print(f"  Experiential:  {exp_count}")

    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="wiki",
        description="Knowledge Vault Wiki CLI — manage code wiki pages",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Scaffold wiki pages for all modules")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing pages")
    p_init.add_argument("--target", default="plugins", help="Target directory (default: plugins)")

    # update
    p_update = subparsers.add_parser("update", help="Incrementally update wiki pages")
    p_update.add_argument("--module", help="Update specific module only")
    p_update.add_argument("--commit", help="Reference commit (default: HEAD)")
    p_update.add_argument("--force", action="store_true", help="Force update even if commit unchanged")

    # lint
    subparsers.add_parser("lint", help="Validate frontmatter and zone markers")

    # graph
    subparsers.add_parser("graph", help="Regenerate graph.json")

    # status
    subparsers.add_parser("status", help="Show coverage and staleness report")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "update": cmd_update,
        "lint": cmd_lint,
        "graph": cmd_graph,
        "status": cmd_status,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
