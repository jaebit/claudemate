#!/usr/bin/env python3
"""
Combined PostToolUse hook: observation recording + HUD update.
Merges observe.py (post) and update_hud.py into a single hook call.
"""

import json
import os
import sys
from pathlib import Path

# Windows UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def find_caw_root():
    """Find .caw directory starting from current working directory."""
    cwd = Path.cwd()
    for path in [cwd, *cwd.parents]:
        caw_dir = path / ".caw"
        if caw_dir.is_dir():
            return caw_dir
    return None


def run_observation(hook_input):
    """Run observation recording (from observe.py)."""
    try:
        # Add the insight-collector hooks directory to path
        plugin_root = Path(__file__).parent.parent
        observe_dir = plugin_root / "skills" / "insight-collector" / "hooks"
        if str(observe_dir) not in sys.path:
            sys.path.insert(0, str(observe_dir))

        from observe import observe_post
        observe_post(hook_input)
    except Exception as e:
        print(f"Observation error: {e}", file=sys.stderr)


def run_hud_update():
    """Run HUD metrics update (from update_hud.py)."""
    try:
        caw_root = find_caw_root()
        if not caw_root:
            return

        hud_mode = os.environ.get("CAW_HUD", "disabled").lower()
        if hud_mode in ("disabled", "false", "0"):
            return

        # Import HUD functions
        plugin_root = Path(__file__).parent.parent
        hud_dir = plugin_root / "skills" / "hud"
        if str(hud_dir) not in sys.path:
            sys.path.insert(0, str(hud_dir))

        from update_hud import update_hud, render_full_hud, render_minimal_hud

        metrics = update_hud(caw_root)

        if hud_mode in ("enabled", "true", "1", "full"):
            output = render_full_hud(metrics)
        else:
            output = render_minimal_hud(metrics)

        print(output, file=sys.stderr)
    except Exception as e:
        print(f"HUD update error: {e}", file=sys.stderr)


def read_stdin_json():
    """Read JSON from stdin."""
    try:
        if sys.stdin.isatty():
            return None
        raw = sys.stdin.read(1024 * 1024).strip()
        if not raw:
            return None
        return json.loads(raw)
    except (json.JSONDecodeError, IOError):
        return None


def main():
    hook_input = read_stdin_json()

    # Run observation only if crew workflow is active (.caw/ exists)
    if hook_input and find_caw_root():
        run_observation(hook_input)

    # Run HUD update (if enabled)
    run_hud_update()


if __name__ == '__main__':
    main()
