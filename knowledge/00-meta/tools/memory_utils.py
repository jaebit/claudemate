#!/usr/bin/env python3
"""Shared utilities and constants for the memory CLI modules."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

# ── Paths ────────────────────────────────────────────────────────────────────

KNOWLEDGE_ROOT = Path(__file__).resolve().parent.parent.parent
MEMORY_BASE = KNOWLEDGE_ROOT / "30-memory"
FACTS_DIR = MEMORY_BASE / "facts"
EXPERIENCES_DIR = MEMORY_BASE / "experiences"
TEMPLATES_DIR = KNOWLEDGE_ROOT / "90-templates"
WORKING_MEMORY_DIR = Path(".claudemate/runtime")
BUDGET_FILE = Path(__file__).resolve().parent / "retrieval-budget.yaml"

VALID_MEMORY_TYPES = ("factual", "experiential")
VALID_TASK_TYPES = ("explore", "locate", "edit", "validate")


# ── Utilities ────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert title to canonical_id slug (lowercase, hyphens only)."""
    return re.sub(r'[^a-z0-9]+', '-', text.lower().strip()).strip('-')


def parse_simple_yaml_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter without PyYAML dependency.

    Returns (meta_dict, body_string).
    """
    if not content.startswith('---\n'):
        return {}, content
    parts = content.split('\n---\n', 1)
    if len(parts) != 2:
        return {}, content
    meta: dict[str, Any] = {}
    for line in parts[0][4:].strip().split('\n'):
        if ':' not in line:
            continue
        k, _, v = line.partition(':')
        v = v.strip()
        if v.startswith('[') and v.endswith(']'):
            meta[k.strip()] = [i.strip() for i in v[1:-1].split(',') if i.strip()]
        elif v.lower() in ('true', 'false'):
            meta[k.strip()] = v.lower() == 'true'
        elif re.fullmatch(r'-?\d+(\.\d+)?', v):
            meta[k.strip()] = float(v) if '.' in v else int(v)
        else:
            meta[k.strip()] = v.strip('"\'')
    return meta, parts[1]


def render_template(template: str, variables: dict[str, str]) -> str:
    """Replace {{key}} placeholders with values."""
    for k, v in variables.items():
        template = template.replace(f'{{{{{k}}}}}', str(v))
    return template


def now_iso() -> str:
    """Return current datetime as ISO string."""
    return datetime.now().isoformat()


def rebuild_frontmatter(meta: dict[str, Any], body: str) -> str:
    """Reconstruct a markdown file from frontmatter dict and body."""
    lines = ['---']
    for k, v in meta.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(repr(i) for i in v)}]")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, str) and any(c in v for c in (' ', ':', '"', "'")):
            lines.append(f'{k}: "{v}"')
        else:
            lines.append(f'{k}: {v}')
    lines.append('---')
    return '\n'.join(lines) + '\n' + body
