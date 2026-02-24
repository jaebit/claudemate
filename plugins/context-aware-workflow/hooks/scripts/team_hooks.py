#!/usr/bin/env python3
"""
Agent Teams Hook Script

Handles TeammateIdle and TaskCompleted events for /cw:team orchestration.

TeammateIdle (exit 2 = feedback):
  - Check .caw/team_state.json for unassigned tasks
  - If tasks available: exit 2 with assignment feedback
  - If no tasks: exit 0 (allow idle)

TaskCompleted (exit 2 = block completion):
  - Check quality gate requirements
  - If review required and not done: exit 2 (block)
  - If review passed or not required: exit 0 (allow)

Usage:
  python3 team_hooks.py teammate_idle
  python3 team_hooks.py task_completed
"""

import json
import os
import sys
from pathlib import Path


def get_project_dir():
    """Get project directory from environment."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def get_team_state():
    """Read .caw/team_state.json if it exists."""
    state_file = get_project_dir() / ".caw" / "team_state.json"
    if not state_file.exists():
        return None
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def get_hook_input():
    """Read hook input from stdin."""
    try:
        if not sys.stdin.isatty():
            return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        pass
    return {}


def handle_teammate_idle(hook_input):
    """Handle TeammateIdle: assign pending tasks to idle teammates."""
    state = get_team_state()
    if not state or not state.get("active"):
        sys.exit(0)

    tasks = state.get("tasks", [])
    pending = [t for t in tasks if t.get("status") == "pending"]

    if not pending:
        # No more tasks - allow idle
        sys.exit(0)

    # Find tasks with satisfied dependencies
    done_ids = {t["id"] for t in tasks if t.get("status") == "done"}
    available = []
    for task in pending:
        deps = task.get("depends_on", [])
        if all(d in done_ids for d in deps):
            available.append(task)

    if not available:
        # Tasks exist but deps not met
        sys.exit(0)

    # Suggest next task assignment
    next_task = available[0]
    print(f"Unassigned task available: [{next_task['id']}] {next_task.get('description', '')}")
    print(f"Pick up this task and begin implementation.")
    sys.exit(2)  # exit 2 = provide feedback to teammate


def handle_task_completed(hook_input):
    """Handle TaskCompleted: enforce quality gates before marking complete."""
    state = get_team_state()
    if not state or not state.get("active"):
        sys.exit(0)

    quality_gates = state.get("quality_gates", {})
    require_review = quality_gates.get("require_review", True)

    if not require_review:
        sys.exit(0)

    # Check if the completed task has been reviewed
    task_id = hook_input.get("task_id", "")
    tasks = state.get("tasks", [])
    task = next((t for t in tasks if t.get("id") == task_id), None)

    if not task:
        sys.exit(0)

    if task.get("status") == "review":
        # Already in review state - allow completion
        sys.exit(0)

    # Task not yet reviewed - block completion and request review
    print(f"Quality gate: Task [{task_id}] requires review before completion.")
    print(f"Please request a reviewer to validate this work.")
    sys.exit(2)  # exit 2 = block completion


def main():
    if len(sys.argv) < 2:
        print("Usage: team_hooks.py <teammate_idle|task_completed>", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    hook_input = get_hook_input()

    if action == "teammate_idle":
        handle_teammate_idle(hook_input)
    elif action == "task_completed":
        handle_task_completed(hook_input)
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
