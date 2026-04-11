#!/usr/bin/env python3
"""Trajectory logger — accumulate LLM task trajectories for MemFactory RL.

Format (JSONL): one JSON object per line:
  {
    "ts": "2026-04-12T04:00:00+09:00",
    "session_id": "gen-057",
    "task_type": "implementation",
    "module": "crew",
    "context_tokens": 12000,
    "memory_tokens": 800,
    "outcome_score": 0.88,
    "notes": "optional free-text"
  }

Subcommands:
  log     — append a new trajectory entry
  query   — filter entries by task_type or module
  stats   — aggregate statistics by task_type
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG_PATH = Path(__file__).resolve().parent.parent.parent / "30-memory" / "trajectory.jsonl"


# ── I/O helpers ──────────────────────────────────────────────────────────────

def _load_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _append_entry(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── Core operations ──────────────────────────────────────────────────────────

def log_trajectory(
    session_id: str,
    task_type: str,
    outcome_score: float,
    context_tokens: int = 0,
    memory_tokens: int = 0,
    module: str = "",
    notes: str = "",
    log_path: Path | None = None,
) -> dict[str, Any]:
    """Append one trajectory entry to the JSONL log.

    Returns the written entry dict.
    """
    entry: dict[str, Any] = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "session_id": session_id,
        "task_type": task_type,
        "module": module,
        "context_tokens": context_tokens,
        "memory_tokens": memory_tokens,
        "outcome_score": round(outcome_score, 4),
    }
    if notes:
        entry["notes"] = notes
    _append_entry(log_path or LOG_PATH, entry)
    return entry


def query_trajectories(
    task_type: str = "",
    module: str = "",
    min_score: float = 0.0,
    log_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Filter trajectory log entries."""
    entries = _load_entries(log_path or LOG_PATH)
    results = []
    for e in entries:
        if task_type and e.get("task_type") != task_type:
            continue
        if module and e.get("module") != module:
            continue
        if e.get("outcome_score", 0) < min_score:
            continue
        results.append(e)
    return results


def trajectory_stats(log_path: Path | None = None) -> dict[str, Any]:
    """Compute aggregate statistics by task_type."""
    entries = _load_entries(log_path or LOG_PATH)
    if not entries:
        return {"total": 0, "by_task_type": {}}

    by_type: dict[str, list] = {}
    for e in entries:
        tt = e.get("task_type", "unknown")
        by_type.setdefault(tt, []).append(e)

    summary: dict[str, Any] = {"total": len(entries), "by_task_type": {}}
    for tt, es in by_type.items():
        scores = [e.get("outcome_score", 0) for e in es]
        ctx = [e.get("context_tokens", 0) for e in es]
        mem = [e.get("memory_tokens", 0) for e in es]
        avg_saving = (
            round(sum(m / c for c, m in zip(ctx, mem) if c > 0) / len(es), 4)
            if es else 0
        )
        summary["by_task_type"][tt] = {
            "count": len(es),
            "avg_score": round(sum(scores) / len(scores), 4),
            "min_score": round(min(scores), 4),
            "max_score": round(max(scores), 4),
            "avg_memory_ratio": avg_saving,
        }
    return summary


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        prog="trajectory_log",
        description="MemFactory RL trajectory accumulator — log/query/stats",
    )
    p.add_argument("--log-path", type=Path, default=None, metavar="FILE",
                   help="Override JSONL log path (default: knowledge/30-memory/trajectory.jsonl)")
    sub = p.add_subparsers(dest="cmd", required=True)

    lg = sub.add_parser("log", help="Append a new trajectory entry")
    lg.add_argument("--session-id", required=True, metavar="ID")
    lg.add_argument("--task-type", required=True, metavar="TYPE")
    lg.add_argument("--outcome-score", type=float, required=True, metavar="F")
    lg.add_argument("--context-tokens", type=int, default=0)
    lg.add_argument("--memory-tokens", type=int, default=0)
    lg.add_argument("--module", default="")
    lg.add_argument("--notes", default="")

    qr = sub.add_parser("query", help="Filter trajectory entries")
    qr.add_argument("--task-type", default="")
    qr.add_argument("--module", default="")
    qr.add_argument("--min-score", type=float, default=0.0)

    sub.add_parser("stats", help="Aggregate statistics by task_type")

    args = p.parse_args()
    lp = args.log_path

    if args.cmd == "log":
        entry = log_trajectory(
            args.session_id, args.task_type, args.outcome_score,
            args.context_tokens, args.memory_tokens, args.module, args.notes, lp,
        )
        print(json.dumps(entry, indent=2, ensure_ascii=False))

    elif args.cmd == "query":
        results = query_trajectories(args.task_type, args.module, args.min_score, lp)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.cmd == "stats":
        print(json.dumps(trajectory_stats(lp), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
