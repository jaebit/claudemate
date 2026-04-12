#!/usr/bin/env python3
"""Memory capture and promote commands for the knowledge vault."""

import sys
from pathlib import Path

from memory_utils import (
    EXPERIENCES_DIR, FACTS_DIR, TEMPLATES_DIR, VALID_MEMORY_TYPES,
    WORKING_MEMORY_DIR, now_iso, parse_simple_yaml_frontmatter,
    rebuild_frontmatter, render_template, slugify,
)


def cmd_capture(args) -> int:
    """Capture a new memory note from template.

    Validates memory type, reads template, renders with variables, writes output.
    """
    if args.type not in VALID_MEMORY_TYPES:
        print(f"Error: type must be one of {VALID_MEMORY_TYPES}", file=sys.stderr)
        return 1

    canonical_id = slugify(args.title)
    out_dir = FACTS_DIR if args.type == 'factual' else EXPERIENCES_DIR
    tpl_file = TEMPLATES_DIR / f"tpl-memory-{args.type}.md"

    out_dir.mkdir(parents=True, exist_ok=True)

    if not tpl_file.exists():
        print(f"Error: template not found: {tpl_file}", file=sys.stderr)
        return 1

    try:
        tpl = tpl_file.read_text(encoding='utf-8')
    except OSError as e:
        print(f"Error reading template: {e}", file=sys.stderr)
        return 1

    variables: dict[str, str] = {
        'canonical_id': canonical_id,
        'date': now_iso(),
        'source_task': args.source_task or '',
        'commit_sha': args.commit or '',
    }
    if args.type == 'factual':
        variables.update({
            'fact_title': args.title, 'fact_statement': '',
            'evidence': '', 'scope': '', 'source_file': '', 'related_links': '',
        })
    else:
        variables.update({
            'experience_title': args.title, 'outcome': args.outcome or '',
            'task_type': args.task_type or '', 'context': '',
            'what_happened': '', 'lesson': '', 'pattern': '', 'related_links': '',
        })

    if args.modules:
        mods = ', '.join(f'"{m}"' for m in args.modules)
        tpl = tpl.replace('related_modules: []', f'related_modules: [{mods}]')

    rendered = render_template(tpl, variables)

    body = args.body or ''
    if not body:
        try:
            body = sys.stdin.read().strip()
        except KeyboardInterrupt:
            body = ''
    if body:
        key = 'fact_statement' if args.type == 'factual' else 'what_happened'
        rendered = rendered.replace(f'{{{{{key}}}}}', body)

    out_file = out_dir / f"{canonical_id}.md"
    try:
        out_file.write_text(rendered, encoding='utf-8')
        print(f"Created: {out_file}")
        return 0
    except OSError as e:
        print(f"Error writing note: {e}", file=sys.stderr)
        return 1


def cmd_promote(args) -> int:
    """Promote a working memory file to permanent memory.

    Reads source, updates frontmatter for memory zone, writes to facts/ or experiences/.
    """
    src = Path(args.path)
    if not src.exists():
        print(f"Error: not found: {src}", file=sys.stderr)
        return 1
    if args.type not in VALID_MEMORY_TYPES:
        print(f"Error: type must be one of {VALID_MEMORY_TYPES}", file=sys.stderr)
        return 1

    try:
        content = src.read_text(encoding='utf-8')
    except OSError as e:
        print(f"Error reading {src}: {e}", file=sys.stderr)
        return 1

    meta, body = parse_simple_yaml_frontmatter(content)
    title = meta.get('title', src.stem)
    canonical_id = slugify(title)
    dest_dir = FACTS_DIR if args.type == 'factual' else EXPERIENCES_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{canonical_id}.md"

    ts = now_iso()
    meta.update({
        'zone': 'memory', 'memory_type': args.type,
        'canonical_id': canonical_id,
        'created': meta.get('created', ts),
        'last_updated': ts,
    })

    try:
        dest.write_text(rebuild_frontmatter(meta, body), encoding='utf-8')
        print(f"Promoted {src} → {dest}")
    except OSError as e:
        print(f"Error writing {dest}: {e}", file=sys.stderr)
        return 1

    if src.resolve().parent == WORKING_MEMORY_DIR.resolve():
        try:
            src.unlink()
            print(f"Removed source: {src}")
        except OSError as e:
            print(f"Warning: could not remove source: {e}", file=sys.stderr)

    return 0
