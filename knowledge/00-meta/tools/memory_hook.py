#!/usr/bin/env python3
"""
Stop Hook Script for Memory Pipeline
Automatically captures session summaries to experiential memory when Claude Code session ends.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Import the capture function from memory_cli
sys.path.insert(0, str(Path(__file__).parent))
from memory_cli import cmd_capture


def capture_session_memory(session_summary: str, session_id: str = None) -> bool:
    """
    Capture session summary to experiential memory.

    Args:
        session_summary: Summary of the completed session
        session_id: Optional session identifier

    Returns:
        bool: True if capture succeeded, False otherwise
    """
    try:
        # Create a mock args object for the capture function
        class MockArgs:
            def __init__(self):
                self.template = "experiential"
                self.title = f"Session Summary {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                self.content = session_summary
                self.tags = ["session", "automated", "hook"]
                if session_id:
                    self.tags.append(f"session-{session_id}")
                self.confidence = 0.8  # High confidence for automated captures

        mock_args = MockArgs()
        result = cmd_capture(mock_args)
        return result == 0

    except Exception as e:
        print(f"Error capturing session memory: {e}", file=sys.stderr)
        return False


def main():
    """
    Main entry point for the Stop hook.
    Reads session summary from stdin or environment variables.
    """
    session_summary = ""
    session_id = os.environ.get("CLAUDE_SESSION_ID")

    # Try to read from stdin first
    if not sys.stdin.isatty():
        try:
            session_summary = sys.stdin.read().strip()
        except:
            pass

    # Fallback to environment variable
    if not session_summary:
        session_summary = os.environ.get("CLAUDE_SESSION_SUMMARY", "")

    # If no summary available, create a minimal one
    if not session_summary:
        session_summary = f"Session completed at {datetime.now().isoformat()}"

    # Capture the session memory
    success = capture_session_memory(session_summary, session_id)

    if success:
        print("Session memory captured successfully")
        sys.exit(0)
    else:
        print("Failed to capture session memory", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()