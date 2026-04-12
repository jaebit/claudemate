#!/usr/bin/env python3
"""Memory query, status, and retrieve commands for the knowledge vault."""

import sys
from pathlib import Path

import yaml

from memory_utils import (
    BUDGET_FILE, EXPERIENCES_DIR, FACTS_DIR, KNOWLEDGE_ROOT,
    VALID_TASK_TYPES, parse_simple_yaml_frontmatter,
)


def cmd_query(args) -> int:
    """Query memory notes by keyword, with optional type and confidence filters."""
    if not (FACTS_DIR.parent).exists():
        print("Memory directory not found.", file=sys.stderr)
        return 1
    if not 0.0 <= args.min_confidence <= 1.0:
        print("Error: --min-confidence must be between 0.0 and 1.0", file=sys.stderr)
        return 1

    results = []
    for d in [FACTS_DIR, EXPERIENCES_DIR]:
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            try:
                meta, body = parse_simple_yaml_frontmatter(f.read_text(encoding='utf-8'))
            except (OSError, UnicodeDecodeError) as e:
                print(f"Warning: skip {f.name}: {e}", file=sys.stderr)
                continue
            if args.type and meta.get('memory_type') != args.type:
                continue
            if float(meta.get('confidence', 1.0)) < args.min_confidence:
                continue
            kw = args.keyword.lower()
            title = meta.get('title', '')
            if kw in title.lower() or kw in meta.get('canonical_id', '').lower() or kw in body.lower():
                results.append({
                    'file': f, 'title': title,
                    'memory_type': meta.get('memory_type', 'unknown'),
                    'confidence': float(meta.get('confidence', 1.0)),
                    'created': meta.get('created', ''),
                    'canonical_id': meta.get('canonical_id', ''),
                })

    results.sort(key=lambda x: x['confidence'], reverse=True)
    if not results:
        print(f"No notes matching '{args.keyword}'")
        return 0

    print(f"Found {len(results)} note(s) matching '{args.keyword}':\n")
    for r in results:
        print(f"  {r['title']}")
        print(f"    type={r['memory_type']}  conf={r['confidence']}  id={r['canonical_id']}")
        print(f"    file={r['file']}  created={r['created']}\n")
    return 0


def cmd_status(args) -> int:
    """Show memory vault statistics."""
    def count_md(d: Path) -> int:
        return len(list(d.glob("*.md"))) if d.exists() else 0

    facts = count_md(FACTS_DIR)
    exps = count_md(EXPERIENCES_DIR)
    print("Memory Vault Status")
    print("=" * 20)
    print(f"Factual:      {facts}")
    print(f"Experiential: {exps}")
    print(f"Total:        {facts + exps}")

    needs_review, latest_file, latest_date = 0, None, ""
    for d in [FACTS_DIR, EXPERIENCES_DIR]:
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            try:
                meta, _ = parse_simple_yaml_frontmatter(f.read_text(encoding='utf-8'))
            except (OSError, UnicodeDecodeError):
                continue
            if meta.get('needs_review', False):
                needs_review += 1
            created = meta.get('created', '')
            if created > latest_date:
                latest_date, latest_file = created, f

    print(f"Needs review: {needs_review}")
    print(f"Latest note:  {latest_file.name if latest_file else 'None'}")
    return 0


def _load_budget(task_type: str) -> tuple[dict, int]:
    """Load retrieval budget for task_type. Returns (budget_dict, token_ratio)."""
    if not BUDGET_FILE.exists():
        raise FileNotFoundError(f"Budget config not found: {BUDGET_FILE}")
    try:
        with BUDGET_FILE.open(encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        budget = cfg['retrieval_budget'][task_type]
        return budget, cfg.get('token_estimation_ratio', 4)
    except yaml.YAMLError as e:
        raise ValueError(f"YAML parse error in budget config: {e}") from e
    except KeyError:
        available = list(cfg.get('retrieval_budget', {}).keys())
        raise KeyError(f"Unknown task_type '{task_type}'. Available: {available}") from None


def _read_file_tokens(path: Path, ratio: int) -> tuple[str, int]:
    """Read file and estimate token count."""
    content = path.read_text(encoding='utf-8')
    return content, len(content) // ratio


def cmd_retrieve(args) -> int:
    """Retrieve memories by task type within token budget constraints."""
    if args.task_type not in VALID_TASK_TYPES:
        print(f"Error: task_type must be one of {VALID_TASK_TYPES}", file=sys.stderr)
        return 1
    try:
        budget, ratio = _load_budget(args.task_type)
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    wiki_root = KNOWLEDGE_ROOT / "10-wiki"
    results, total = [], 0

    # 1. Wiki (highest priority)
    wiki_budget = budget.get('wiki_tokens', 0)
    if wiki_root.exists() and wiki_budget > 0:
        for wf in sorted(wiki_root.rglob("*.md")):
            if total >= budget['total_budget']:
                break
            if args.module and args.module.lower() not in str(wf).lower():
                continue
            try:
                content, tokens = _read_file_tokens(wf, ratio)
            except (OSError, UnicodeDecodeError) as e:
                print(f"Warning: skip {wf.name}: {e}", file=sys.stderr)
                continue
            if total + tokens <= wiki_budget:
                results.append({'type': 'wiki', 'path': wf, 'tokens': tokens, 'content': content})
                total += tokens

    # 2. Factual memories
    factual_budget = budget.get('factual_tokens', 0)
    if FACTS_DIR.exists() and factual_budget > 0:
        for ff in sorted(FACTS_DIR.glob("*.md")):
            if total >= budget['total_budget']:
                break
            try:
                meta, _ = parse_simple_yaml_frontmatter(ff.read_text(encoding='utf-8'))
            except (OSError, UnicodeDecodeError):
                continue
            if args.module:
                mods = meta.get('modules', [])
                if isinstance(mods, str):
                    mods = [mods]
                if args.module not in mods:
                    continue
            try:
                content, tokens = _read_file_tokens(ff, ratio)
            except (OSError, UnicodeDecodeError) as e:
                print(f"Warning: skip {ff.name}: {e}", file=sys.stderr)
                continue
            if total + tokens <= factual_budget:
                results.append({'type': 'factual', 'path': ff, 'tokens': tokens, 'content': content})
                total += tokens

    # 3. Experiential memories (sorted by confidence + recency)
    exp_budget = budget.get('experiential_tokens', 0)
    if EXPERIENCES_DIR.exists() and exp_budget > 0:
        candidates = []
        for ef in EXPERIENCES_DIR.glob("*.md"):
            try:
                meta, _ = parse_simple_yaml_frontmatter(ef.read_text(encoding='utf-8'))
                content, tokens = _read_file_tokens(ef, ratio)
            except (OSError, UnicodeDecodeError):
                continue
            if args.module:
                mods = meta.get('modules', [])
                if isinstance(mods, str):
                    mods = [mods]
                if args.module not in mods:
                    continue
            candidates.append({
                'path': ef, 'tokens': tokens, 'content': content,
                'confidence': float(meta.get('confidence', 0.5)),
                'mtime': ef.stat().st_mtime,
            })
        candidates.sort(key=lambda x: (x['confidence'], x['mtime']), reverse=True)
        exp_used = 0
        for c in candidates:
            if total >= budget['total_budget']:
                break
            if exp_used + c['tokens'] <= exp_budget:
                results.append({'type': 'experiential', 'path': c['path'],
                                'tokens': c['tokens'], 'content': c['content']})
                total += c['tokens']
                exp_used += c['tokens']

    # Output
    print(f"Retrieval: task={args.task_type}  budget={budget['total_budget']}  used={total}")
    print("=" * 50)
    for r in results:
        print(f"\n[{r['type'].upper()}] {r['path'].name} ({r['tokens']} tokens)")
        print("-" * 40)
        print(r['content'])
    if not results:
        print("No memories found matching criteria.")
    return 0
