#!/usr/bin/env python3
"""
Worktree Setup Hook Script

Handles WorktreeCreate and WorktreeRemove events to synchronize
.caw/ project context into new worktrees.

Usage:
  python3 worktree_setup.py create   # WorktreeCreate hook
  python3 worktree_setup.py remove   # WorktreeRemove hook
"""

import json
import os
import shutil
import sys
from pathlib import Path


# Files to copy from .caw/ into the new worktree
CAW_FILES = [
    "task_plan.md",
    "context_manifest.json",
    "spec.md",
    "session.json",
    "auto-state.json",
]


def get_hook_input():
    """Read hook input from stdin."""
    try:
        if not sys.stdin.isatty():
            return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        pass
    return {}


def get_project_dir():
    """Get project directory from environment."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def handle_create(hook_input):
    """Handle WorktreeCreate: copy .caw/ files to new worktree."""
    worktree_path = hook_input.get("worktree_path", "")
    worktree_name = hook_input.get("worktree_name", "")

    if not worktree_path:
        print("No worktree_path in hook input", file=sys.stderr)
        sys.exit(0)

    worktree = Path(worktree_path)
    source_caw = get_project_dir() / ".caw"

    if not source_caw.exists():
        print("No .caw/ directory to copy", file=sys.stderr)
        sys.exit(0)

    dest_caw = worktree / ".caw"
    dest_caw.mkdir(parents=True, exist_ok=True)

    copied = []
    for filename in CAW_FILES:
        src = source_caw / filename
        if src.exists():
            shutil.copy2(str(src), str(dest_caw / filename))
            copied.append(filename)

    # Write worktree metadata
    config = {
        "worktree_name": worktree_name,
        "worktree_path": str(worktree),
        "source_project": str(get_project_dir()),
        "copied_files": copied,
    }
    config_path = dest_caw / "worktree_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    if copied:
        print(f"Copied {len(copied)} .caw/ files to worktree: {', '.join(copied)}", file=sys.stderr)


def handle_remove(hook_input):
    """Handle WorktreeRemove: clean up worktree metadata."""
    worktree_path = hook_input.get("worktree_path", "")

    if not worktree_path:
        sys.exit(0)

    worktree = Path(worktree_path)
    config_path = worktree / ".caw" / "worktree_config.json"

    if config_path.exists():
        try:
            config_path.unlink()
            print("Cleaned up worktree_config.json", file=sys.stderr)
        except OSError:
            pass


def main():
    if len(sys.argv) < 2:
        print("Usage: worktree_setup.py <create|remove>", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    hook_input = get_hook_input()

    if action == "create":
        handle_create(hook_input)
    elif action == "remove":
        handle_remove(hook_input)
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
