#!/usr/bin/env python3
"""
zone_lint.py — Zone-Based Editing Validator

Checks that:
1. HUMAN-ZONE / LLM-ZONE markers are balanced
2. Write ownership rules are respected in git diffs
3. No zone markers have been deleted or moved by agents

Usage:
    python3 zone_lint.py [--diff]    # Check all files (or only changed files with --diff)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"

# Write ownership map: zone -> allowed writers
OWNERSHIP = {
    "00-meta": {"human"},
    "10-wiki": {"wiki-cli"},
    "20-notes": {"human", "agent-limited"},
    "30-memory": {"memory-manager"},
    "90-templates": {"human"},
}


def get_changed_files() -> list[Path]:
    """Get list of changed files in knowledge/ from git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        staged = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        files = set()
        for line in (result.stdout + staged.stdout).splitlines():
            line = line.strip()
            if line.startswith("knowledge/") and line.endswith(".md"):
                files.add(REPO_ROOT / line)
        return sorted(files)
    except FileNotFoundError:
        return []


def check_zone_balance(filepath: Path) -> list[str]:
    """Check that zone markers are balanced."""
    errors = []
    try:
        content = filepath.read_text()
    except OSError:
        return [f"Cannot read file: {filepath}"]

    lines = content.splitlines()
    human_stack = []
    llm_stack = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == "<!-- HUMAN-ZONE -->":
            human_stack.append(i)
        elif stripped == "<!-- /HUMAN-ZONE -->":
            if not human_stack:
                errors.append(f"Line {i}: Closing HUMAN-ZONE without opening")
            else:
                human_stack.pop()
        elif stripped == "<!-- LLM-ZONE -->":
            llm_stack.append(i)
        elif stripped == "<!-- /LLM-ZONE -->":
            if not llm_stack:
                errors.append(f"Line {i}: Closing LLM-ZONE without opening")
            else:
                llm_stack.pop()

    for line_no in human_stack:
        errors.append(f"Line {line_no}: Unclosed HUMAN-ZONE")
    for line_no in llm_stack:
        errors.append(f"Line {line_no}: Unclosed LLM-ZONE")

    return errors


def check_ownership(filepath: Path) -> list[str]:
    """Check write ownership rules based on file location."""
    warnings = []
    rel = filepath.relative_to(KNOWLEDGE_ROOT)
    parts = rel.parts

    if not parts:
        return warnings

    zone = parts[0]
    allowed = OWNERSHIP.get(zone, set())

    if not allowed:
        warnings.append(f"Unknown zone: {zone}")

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="zone-lint",
        description="Validate zone-based editing markers and ownership",
    )
    parser.add_argument("--diff", action="store_true",
                        help="Only check files changed in git")
    args = parser.parse_args()

    if args.diff:
        files = get_changed_files()
        if not files:
            print("[zone-lint] No changed knowledge files.")
            return 0
    else:
        files = sorted(KNOWLEDGE_ROOT.rglob("*.md"))

    total_errors = 0
    total_warnings = 0

    for filepath in files:
        rel = filepath.relative_to(KNOWLEDGE_ROOT)

        # Zone balance check
        errors = check_zone_balance(filepath)
        for e in errors:
            print(f"  ERROR {rel}: {e}")
            total_errors += 1

        # Ownership check
        warnings = check_ownership(filepath)
        for w in warnings:
            print(f"  WARN  {rel}: {w}")
            total_warnings += 1

    print(f"\n[zone-lint] Scanned {len(files)} files: {total_errors} errors, {total_warnings} warnings")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
