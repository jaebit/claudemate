#!/usr/bin/env python3
"""PageIndex — tree-based search over knowledge/10-wiki/ without vector embeddings.

Design: filesystem path hierarchy IS the index structure.
build_index() scans wiki/ and builds a flat dict of {slug → metadata}.
search_tree() does lexical matching + path-hierarchy scoring.
"""

import re
import sys
from pathlib import Path
from typing import Any

KNOWLEDGE_ROOT = Path(__file__).resolve().parent.parent.parent
WIKI_ROOT = KNOWLEDGE_ROOT / "10-wiki"


# ── Index building ───────────────────────────────────────────────────────────

def _extract_title(text: str, fallback: str) -> str:
    """Extract first H1 heading or YAML title: field from markdown text."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("title:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return fallback


def _extract_tags(text: str) -> list[str]:
    """Extract tags from YAML frontmatter 'tags:' line."""
    for line in text.splitlines():
        if line.startswith("tags:"):
            raw = line.split(":", 1)[1].strip().strip("[]")
            return [t.strip().strip('"') for t in raw.split(",") if t.strip()]
    return []


def _extract_headings(text: str) -> list[str]:
    """Return all H2 headings as topic keywords."""
    return [re.sub(r"^##+ ", "", l).strip()
            for l in text.splitlines() if re.match(r"^## [^#]", l)]


def build_index(wiki_root: Path | None = None) -> dict[str, dict[str, Any]]:
    """Scan wiki_root recursively and build a searchable page index.

    Returns:
        {slug: {title, path, depth, tags, headings, raw_text}}
    where slug is the relative path stem (e.g. "modules/crew").
    """
    root = Path(wiki_root) if wiki_root else WIKI_ROOT
    index: dict[str, dict[str, Any]] = {}

    for md_file in sorted(root.rglob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        rel = md_file.relative_to(root)
        slug = str(rel.with_suffix(""))  # e.g. "modules/crew"
        depth = len(rel.parts)           # 1 = top-level, 2 = modules/*, etc.

        index[slug] = {
            "title": _extract_title(text, md_file.stem),
            "path": str(rel),
            "depth": depth,
            "tags": _extract_tags(text),
            "headings": _extract_headings(text),
            "raw_text": text,
        }

    return index


# ── Tree search ──────────────────────────────────────────────────────────────

def _score_entry(entry: dict[str, Any], query_terms: list[str]) -> float:
    """Score a page entry against a list of query terms.

    Scoring heuristic:
      - title match      = 3.0 pts per term
      - heading match    = 2.0 pts per term
      - tag match        = 2.0 pts per term
      - body match       = 0.5 pts per term  (capped at 5 body hits)
      - depth bonus      = 0.2 × (1/depth)   (shallower = slightly higher)
    """
    score = 0.0
    title_lower = entry["title"].lower()
    headings_lower = " ".join(entry["headings"]).lower()
    tags_lower = " ".join(entry["tags"]).lower()
    body_lower = entry["raw_text"].lower()

    for term in query_terms:
        t = term.lower()
        if t in title_lower:
            score += 3.0
        if t in headings_lower:
            score += 2.0
        if t in tags_lower:
            score += 2.0
        body_hits = min(body_lower.count(t), 5)
        score += body_hits * 0.5

    score += 0.2 / max(entry["depth"], 1)
    return score


def search_tree(
    index: dict[str, dict[str, Any]],
    query: str,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Lexical search over the page index using path-hierarchy scoring.

    Returns a ranked list of result dicts (without raw_text to save tokens).
    """
    terms = [t for t in re.split(r"\W+", query) if len(t) > 1]
    if not terms:
        return []

    scored = []
    for slug, entry in index.items():
        s = _score_entry(entry, terms)
        if s > 0:
            scored.append((s, slug, entry))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "slug": slug,
            "title": e["title"],
            "path": e["path"],
            "score": round(score, 3),
            "matched_headings": [h for h in e["headings"]
                                  if any(t.lower() in h.lower() for t in terms)],
            "tags": e["tags"],
        }
        for score, slug, e in scored[:max_results]
    ]


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse, json
    p = argparse.ArgumentParser(
        prog="page_index",
        description="PageIndex tree-search over knowledge/10-wiki/",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="Search the wiki index")
    s.add_argument("query", help="Search query")
    s.add_argument("--top", type=int, default=10, metavar="N", help="Max results")
    s.add_argument("--wiki-root", type=Path, default=None)

    sub.add_parser("index", help="Print full index (slugs only)")

    args = p.parse_args()

    if args.cmd == "search":
        idx = build_index(args.wiki_root)
        results = search_tree(idx, args.query, args.top)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.cmd == "index":
        idx = build_index()
        for slug in sorted(idx):
            print(slug)


if __name__ == "__main__":
    main()
