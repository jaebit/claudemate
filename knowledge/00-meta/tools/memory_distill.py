#!/usr/bin/env python3
"""Memory distillation engine — compress/merge/prune knowledge/30-memory/ files."""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # → knowledge/
MEM_ROOT = ROOT / "30-memory"
FACTS_DIR = MEM_ROOT / "facts"
EXPERIENCES_DIR = MEM_ROOT / "experiences"


# ── Frontmatter parser ───────────────────────────────────────────────────────

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (meta_dict, body) from markdown with YAML frontmatter."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta: dict = {}
    for line in text[3:end].strip().splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip().strip('"').strip("'")
        if v.startswith("["):
            v = [x.strip().strip('"') for x in v.strip("[]").split(",") if x.strip()]
        meta[k.strip()] = v
    return meta, text[end + 4:].strip()


def _parse_dt(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _rebuild(meta: dict, body: str) -> str:
    lines = []
    for k, v in meta.items():
        lines.append(f"{k}: {json.dumps(v) if isinstance(v, list) else v}")
    return "---\n" + "\n".join(lines) + "\n---\n\n" + body


# ── Core functions ───────────────────────────────────────────────────────────

def group_by_topic(files: list[Path]) -> dict[str, list[Path]]:
    """Group memory .md files by their 'topic' frontmatter field."""
    groups: dict[str, list[Path]] = defaultdict(list)
    for f in files:
        try:
            meta, _ = _parse_frontmatter(f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        groups[meta.get("topic", "uncategorized")].append(f)
    return dict(groups)


def merge_notes(notes: list[Path], dry_run: bool = False) -> list[Path]:
    """Merge duplicate notes (same topic) into the newest one.

    Appends older bodies into the newest file, then deletes older files.
    Returns list of files that were (or would be) deleted.
    """
    if len(notes) <= 1:
        return []
    dated = []
    for f in notes:
        try:
            meta, body = _parse_frontmatter(f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        dt = _parse_dt(meta.get("created_at", "")) or datetime.min.replace(tzinfo=timezone.utc)
        dated.append((dt, f, meta, body))
    dated.sort(key=lambda x: x[0])
    *older, (_, newest_f, newest_meta, newest_body) = dated
    if not dry_run and older:
        extra = "\n\n---\n\n".join(b for _, _, _, b in older if b.strip())
        merged_body = newest_body + ("\n\n---\n\n" + extra if extra else "")
        newest_f.write_text(_rebuild(newest_meta, merged_body), encoding="utf-8")
        for _, f, _, _ in older:
            f.unlink(missing_ok=True)
    return [f for _, f, _, _ in older]


def prune_stale(
    files: list[Path],
    min_confidence: float = 0.5,
    max_age_days: int = 30,
    dry_run: bool = False,
) -> list[Path]:
    """Remove notes with confidence < min_confidence or age > max_age_days.

    Targets knowledge/30-memory/facts/ and knowledge/30-memory/experiences/.
    Returns list of files that were (or would be) removed.
    """
    now = datetime.now(tz=timezone.utc)
    pruned: list[Path] = []
    for f in files:
        try:
            meta, _ = _parse_frontmatter(f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        confidence = float(meta.get("confidence", 1.0))
        dt = _parse_dt(meta.get("created_at", ""))
        age_days = (now - dt).days if dt else 0
        if confidence < min_confidence or age_days > max_age_days:
            pruned.append(f)
            if not dry_run:
                f.unlink(missing_ok=True)
    return pruned


def distill(
    memory_dir: Path | None = None,
    dry_run: bool = False,
    min_confidence: float = 0.5,
    max_age_days: int = 30,
) -> dict:
    """Orchestrate distillation across knowledge/30-memory/facts/ and experiences/.

    Steps: group_by_topic → merge_notes → prune_stale.
    Returns {"merged": N, "pruned": N}.
    """
    dirs = [FACTS_DIR, EXPERIENCES_DIR] if memory_dir is None else [Path(memory_dir)]
    total_merged, total_pruned = 0, 0

    for d in dirs:
        if not d.exists():
            print(f"  [skip] {d} — directory not found", file=sys.stderr)
            continue
        files = list(d.glob("*.md"))
        if not files:
            print(f"  [info] {d.name}/ — no .md files yet")
            continue

        groups = group_by_topic(files)
        print(f"  {d.name}/: {len(files)} notes → {len(groups)} topics")

        for topic, grp in groups.items():
            merged = merge_notes(grp, dry_run=dry_run)
            if merged:
                verb = "would merge" if dry_run else "merged"
                print(f"    [{verb}] '{topic}': {len(merged)} redundant")
            total_merged += len(merged)

        remaining = [f for f in files if f.name not in {m.name for m in []}]
        pruned = prune_stale(remaining, min_confidence, max_age_days, dry_run)
        if pruned:
            verb = "would prune" if dry_run else "pruned"
            print(f"    [{verb}] {len(pruned)} stale (conf<{min_confidence} | age>{max_age_days}d)")
        total_pruned += len(pruned)

    return {"merged": total_merged, "pruned": total_pruned}


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        prog="memory_distill",
        description="Distill knowledge/30-memory/: merge duplicates, prune stale notes.",
    )
    p.add_argument("--dry-run", action="store_true",
                   help="Preview actions without modifying files")
    p.add_argument("--min-confidence", type=float, default=0.5, metavar="F",
                   help="Prune notes below this confidence (default: 0.5)")
    p.add_argument("--max-age-days", type=int, default=30, metavar="N",
                   help="Prune notes older than N days (default: 30)")
    p.add_argument("--memory-dir", type=Path, default=None, metavar="DIR",
                   help="Target a specific directory instead of facts/ + experiences/")
    args = p.parse_args()

    prefix = "[DRY-RUN] " if args.dry_run else ""
    print(f"{prefix}Distilling knowledge/30-memory/ ...")
    print(f"  min-confidence={args.min_confidence}  max-age-days={args.max_age_days}")

    result = distill(
        memory_dir=args.memory_dir,
        dry_run=args.dry_run,
        min_confidence=args.min_confidence,
        max_age_days=args.max_age_days,
    )
    suffix = " (dry-run — no files changed)" if args.dry_run else ""
    print(f"\nDone: {result['merged']} merged, {result['pruned']} pruned{suffix}")


if __name__ == "__main__":
    main()
