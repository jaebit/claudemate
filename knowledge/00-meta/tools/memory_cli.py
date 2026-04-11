#!/usr/bin/env python3
"""
Memory CLI - Knowledge vault memory note management tool

Manages factual and experiential memory notes in the knowledge vault.
Provides capture, query, promote, and status operations.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Memory directories
MEMORY_BASE = Path("knowledge/30-memory")
FACTS_DIR = MEMORY_BASE / "facts"
EXPERIENCES_DIR = MEMORY_BASE / "experiences"
TEMPLATES_DIR = Path("knowledge/90-templates")
WORKING_MEMORY_DIR = Path(".claudemate/runtime")

def slugify(text: str) -> str:
    """Convert title to canonical_id slug format."""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower().strip())
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug

def parse_simple_yaml_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Simple YAML frontmatter parser without PyYAML dependency."""
    if not content.startswith('---\n'):
        return {}, content

    parts = content.split('\n---\n', 1)
    if len(parts) != 2:
        return {}, content

    frontmatter_text = parts[0][4:]  # Remove leading '---\n'
    body = parts[1]

    frontmatter = {}
    for line in frontmatter_text.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Handle different value types
            if value.startswith('[') and value.endswith(']'):
                # Simple list parsing
                value = value[1:-1]  # Remove brackets
                if value:
                    frontmatter[key] = [item.strip() for item in value.split(',')]
                else:
                    frontmatter[key] = []
            elif value.lower() in ['true', 'false']:
                frontmatter[key] = value.lower() == 'true'
            elif value.replace('.', '').isdigit():
                frontmatter[key] = float(value) if '.' in value else int(value)
            else:
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                frontmatter[key] = value

    return frontmatter, body

def render_template(template_content: str, variables: Dict[str, str]) -> str:
    """Replace {{variable}} placeholders in template content."""
    result = template_content
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result

def cmd_capture(args: argparse.Namespace) -> int:
    """Capture a new memory note from template."""
    memory_type = args.type
    title = args.title

    if memory_type not in ['factual', 'experiential']:
        print(f"Error: Invalid memory type '{memory_type}'. Must be 'factual' or 'experiential'", file=sys.stderr)
        return 1

    # Generate canonical_id
    canonical_id = slugify(title)

    # Determine output directory and template
    if memory_type == 'factual':
        output_dir = FACTS_DIR
        template_file = TEMPLATES_DIR / "tpl-memory-factual.md"
    else:
        output_dir = EXPERIENCES_DIR
        template_file = TEMPLATES_DIR / "tpl-memory-experiential.md"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if template exists
    if not template_file.exists():
        print(f"Error: Template file not found: {template_file}", file=sys.stderr)
        return 1

    # Read template
    try:
        template_content = template_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading template: {e}", file=sys.stderr)
        return 1

    # Prepare template variables
    current_date = datetime.now().isoformat()
    variables = {
        'canonical_id': canonical_id,
        'date': current_date,
        'source_task': args.source_task or '',
        'commit_sha': args.commit or '',
    }

    if memory_type == 'factual':
        variables.update({
            'fact_title': title,
            'fact_statement': '',
            'evidence': '',
            'scope': '',
            'source_file': '',
            'related_links': '',
        })
    else:  # experiential
        variables.update({
            'experience_title': title,
            'outcome': args.outcome or '',
            'task_type': args.task_type or '',
            'context': '',
            'what_happened': '',
            'lesson': '',
            'pattern': '',
            'related_links': '',
        })

    # Handle modules
    if args.modules:
        # Convert modules list to YAML format
        modules_str = ', '.join(f'"{m}"' for m in args.modules)
        template_content = template_content.replace('related_modules: []', f'related_modules: [{modules_str}]')

    # Render template
    rendered_content = render_template(template_content, variables)

    # Read body from stdin or use empty
    if args.body:
        body_content = args.body
    else:
        try:
            body_content = sys.stdin.read().strip()
        except KeyboardInterrupt:
            body_content = ""

    # If we have body content, try to populate template zones
    if body_content and memory_type == 'factual':
        # Simple body injection for factual notes
        if '{{fact_statement}}' in rendered_content:
            rendered_content = rendered_content.replace('{{fact_statement}}', body_content)
    elif body_content and memory_type == 'experiential':
        # Simple body injection for experiential notes
        if '{{what_happened}}' in rendered_content:
            rendered_content = rendered_content.replace('{{what_happened}}', body_content)

    # Write output file
    output_file = output_dir / f"{canonical_id}.md"
    try:
        output_file.write_text(rendered_content, encoding='utf-8')
        print(f"Created memory note: {output_file}")
        return 0
    except Exception as e:
        print(f"Error writing memory note: {e}", file=sys.stderr)
        return 1

def cmd_query(args: argparse.Namespace) -> int:
    """Query existing memory notes by keyword."""
    keyword = args.keyword
    memory_type_filter = args.type
    min_confidence = args.min_confidence

    if not MEMORY_BASE.exists():
        print("No memory notes found. Memory directory does not exist.", file=sys.stderr)
        return 1

    results = []

    # Search in both facts and experiences directories
    for search_dir in [FACTS_DIR, EXPERIENCES_DIR]:
        if not search_dir.exists():
            continue

        for md_file in search_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                frontmatter, body = parse_simple_yaml_frontmatter(content)

                # Apply filters
                if memory_type_filter and frontmatter.get('memory_type') != memory_type_filter:
                    continue

                confidence = frontmatter.get('confidence', 1.0)
                if confidence < min_confidence:
                    continue

                # Check if keyword matches in title, canonical_id, or body
                title = frontmatter.get('title', '')
                canonical_id = frontmatter.get('canonical_id', '')

                if (keyword.lower() in title.lower() or
                    keyword.lower() in canonical_id.lower() or
                    keyword.lower() in body.lower()):

                    results.append({
                        'file': md_file,
                        'title': title,
                        'memory_type': frontmatter.get('memory_type', 'unknown'),
                        'confidence': confidence,
                        'created': frontmatter.get('created', ''),
                        'canonical_id': canonical_id
                    })
            except Exception as e:
                print(f"Warning: Could not process {md_file}: {e}", file=sys.stderr)
                continue

    # Sort by confidence descending
    results.sort(key=lambda x: x['confidence'], reverse=True)

    # Output results
    if not results:
        print(f"No memory notes found matching '{keyword}'")
        return 0

    print(f"Found {len(results)} memory note(s) matching '{keyword}':")
    print()
    for result in results:
        print(f"📝 {result['title']}")
        print(f"   Type: {result['memory_type']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   ID: {result['canonical_id']}")
        print(f"   File: {result['file']}")
        print(f"   Created: {result['created']}")
        print()

    return 0

def cmd_promote(args: argparse.Namespace) -> int:
    """Promote a working memory file to permanent memory."""
    source_path = Path(args.path)
    memory_type = args.type

    if not source_path.exists():
        print(f"Error: Source file not found: {source_path}", file=sys.stderr)
        return 1

    if memory_type not in ['factual', 'experiential']:
        print(f"Error: Invalid memory type '{memory_type}'. Must be 'factual' or 'experiential'", file=sys.stderr)
        return 1

    try:
        content = source_path.read_text(encoding='utf-8')
        frontmatter, body = parse_simple_yaml_frontmatter(content)

        # Determine title and canonical_id
        title = frontmatter.get('title', source_path.stem)
        canonical_id = slugify(title)

        # Determine destination directory
        if memory_type == 'factual':
            dest_dir = FACTS_DIR
        else:
            dest_dir = EXPERIENCES_DIR

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / f"{canonical_id}.md"

        # Update frontmatter for memory zone
        current_date = datetime.now().isoformat()
        frontmatter.update({
            'zone': 'memory',
            'memory_type': memory_type,
            'canonical_id': canonical_id,
            'created': frontmatter.get('created', current_date),
            'last_updated': current_date,
        })

        # Rebuild content with updated frontmatter
        frontmatter_lines = ['---']
        for key, value in frontmatter.items():
            if isinstance(value, list):
                value_str = '[' + ', '.join(f'"{item}"' for item in value) + ']'
            elif isinstance(value, bool):
                value_str = 'true' if value else 'false'
            elif isinstance(value, str) and any(char in value for char in [' ', ':', '"', "'"]):
                value_str = f'"{value}"'
            else:
                value_str = str(value)
            frontmatter_lines.append(f'{key}: {value_str}')
        frontmatter_lines.append('---')

        new_content = '\n'.join(frontmatter_lines) + '\n' + body

        dest_file.write_text(new_content, encoding='utf-8')
        print(f"Promoted {source_path} to {dest_file}")

        # Optionally remove source file
        if source_path.parent == WORKING_MEMORY_DIR:
            source_path.unlink()
            print(f"Removed source file: {source_path}")

        return 0

    except Exception as e:
        print(f"Error promoting file: {e}", file=sys.stderr)
        return 1

def cmd_status(args: argparse.Namespace) -> int:
    """Show memory vault status."""
    print("Memory Vault Status")
    print("=" * 20)

    # Count facts
    facts_count = 0
    if FACTS_DIR.exists():
        facts_count = len(list(FACTS_DIR.glob("*.md")))
    print(f"Factual memories: {facts_count}")

    # Count experiences
    experiences_count = 0
    if EXPERIENCES_DIR.exists():
        experiences_count = len(list(EXPERIENCES_DIR.glob("*.md")))
    print(f"Experiential memories: {experiences_count}")

    print(f"Total memory notes: {facts_count + experiences_count}")

    # Count files needing review
    needs_review_count = 0
    latest_file = None
    latest_date = ""

    for search_dir in [FACTS_DIR, EXPERIENCES_DIR]:
        if not search_dir.exists():
            continue

        for md_file in search_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                frontmatter, _ = parse_simple_yaml_frontmatter(content)

                if frontmatter.get('needs_review', False):
                    needs_review_count += 1

                created = frontmatter.get('created', '')
                if created > latest_date:
                    latest_date = created
                    latest_file = md_file

            except Exception:
                continue

    print(f"Needs review: {needs_review_count}")

    if latest_file:
        print(f"Latest note: {latest_file.name} ({latest_date})")
    else:
        print("Latest note: None")

    return 0


def cmd_retrieve(args: argparse.Namespace) -> int:
    """Retrieve memories based on task type and budget constraints."""
    import yaml

    # Load retrieval budget configuration
    budget_file = Path(__file__).parent / "retrieval-budget.yaml"
    if not budget_file.exists():
        print(f"Error: Budget configuration not found at {budget_file}", file=sys.stderr)
        return 1

    try:
        with open(budget_file, 'r') as f:
            config = yaml.safe_load(f)
        budget = config['retrieval_budget'][args.task_type]
    except Exception as e:
        print(f"Error loading budget configuration: {e}", file=sys.stderr)
        return 1

    # Token estimation ratio (4 chars ≈ 1 token)
    token_ratio = config.get('token_estimation_ratio', 4)

    memory_root = Path.home() / ".claudemate" / "memory"
    wiki_root = Path(__file__).parents[2] / "10-wiki"  # knowledge/10-wiki/

    results = []
    total_tokens = 0

    # 1. Wiki memory (highest priority)
    if wiki_root.exists() and budget['wiki_tokens'] > 0:
        wiki_files = list(wiki_root.rglob("*.md"))
        for wiki_file in wiki_files:
            if total_tokens >= budget['total_budget']:
                break

            # Module filter
            if args.module and args.module.lower() not in str(wiki_file).lower():
                continue

            try:
                content = wiki_file.read_text()
                estimated_tokens = len(content) // token_ratio

                if total_tokens + estimated_tokens <= budget['wiki_tokens']:
                    results.append({
                        'type': 'wiki',
                        'path': wiki_file,
                        'tokens': estimated_tokens,
                        'content': content
                    })
                    total_tokens += estimated_tokens
            except:
                continue

    # 2. Factual memory
    facts_dir = memory_root / "facts"
    if facts_dir.exists() and budget['factual_tokens'] > 0:
        fact_files = list(facts_dir.glob("*.md"))
        for fact_file in fact_files:
            if total_tokens >= budget['total_budget']:
                break

            # Module filter
            if args.module:
                try:
                    content = fact_file.read_text()
                    frontmatter, _ = parse_simple_yaml_frontmatter(content)
                    modules = frontmatter.get('modules', [])
                    if isinstance(modules, str):
                        modules = [modules]
                    if args.module not in modules:
                        continue
                except:
                    continue

            try:
                content = fact_file.read_text()
                estimated_tokens = len(content) // token_ratio

                if total_tokens + estimated_tokens <= budget['factual_tokens']:
                    results.append({
                        'type': 'factual',
                        'path': fact_file,
                        'tokens': estimated_tokens,
                        'content': content
                    })
                    total_tokens += estimated_tokens
            except:
                continue

    # 3. Experiential memory (top-k by confidence/recency)
    experiences_dir = memory_root / "experiences"
    if experiences_dir.exists() and budget['experiential_tokens'] > 0:
        exp_candidates = []
        exp_files = list(experiences_dir.glob("*.md"))

        for exp_file in exp_files:
            # Module filter
            if args.module:
                try:
                    content = exp_file.read_text()
                    frontmatter, _ = parse_simple_yaml_frontmatter(content)
                    modules = frontmatter.get('modules', [])
                    if isinstance(modules, str):
                        modules = [modules]
                    if args.module not in modules:
                        continue
                except:
                    continue

            try:
                content = exp_file.read_text()
                frontmatter, _ = parse_simple_yaml_frontmatter(content)
                confidence = frontmatter.get('confidence', 0.5)
                estimated_tokens = len(content) // token_ratio

                exp_candidates.append({
                    'path': exp_file,
                    'confidence': confidence,
                    'tokens': estimated_tokens,
                    'content': content,
                    'mtime': exp_file.stat().st_mtime
                })
            except:
                continue

        # Sort by confidence desc, then recency desc
        exp_candidates.sort(key=lambda x: (x['confidence'], x['mtime']), reverse=True)

        exp_tokens_used = 0
        for candidate in exp_candidates:
            if total_tokens >= budget['total_budget']:
                break
            if exp_tokens_used + candidate['tokens'] <= budget['experiential_tokens']:
                results.append({
                    'type': 'experiential',
                    'path': candidate['path'],
                    'tokens': candidate['tokens'],
                    'content': candidate['content']
                })
                total_tokens += candidate['tokens']
                exp_tokens_used += candidate['tokens']

    # Output results
    print(f"Retrieval Results for task-type: {args.task_type}")
    print(f"Budget: {budget['total_budget']} tokens, Used: {total_tokens} tokens")
    print("=" * 50)

    for result in results:
        print(f"\n[{result['type'].upper()}] {result['path'].name} ({result['tokens']} tokens)")
        print("-" * 40)
        print(result['content'])

    if not results:
        print("No memories found matching criteria.")

    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Memory CLI - Knowledge vault memory note management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s capture factual "API Rate Limit" --source-task T123
  %(prog)s query "rate limit" --type factual --min-confidence 0.7
  %(prog)s promote .claudemate/runtime/note.md --type experiential
  %(prog)s status
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Capture command
    capture_parser = subparsers.add_parser('capture', help='Capture new memory note')
    capture_parser.add_argument('type', choices=['factual', 'experiential'],
                               help='Memory type')
    capture_parser.add_argument('title', help='Memory note title')
    capture_parser.add_argument('--source-task', help='Source task ID')
    capture_parser.add_argument('--commit', help='Source commit SHA')
    capture_parser.add_argument('--modules', help='Related modules (comma-separated)')
    capture_parser.add_argument('--body', help='Memory note body content')
    capture_parser.add_argument('--outcome', help='Outcome for experiential memories')
    capture_parser.add_argument('--task-type', help='Task type for experiential memories')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query memory notes')
    query_parser.add_argument('keyword', help='Search keyword')
    query_parser.add_argument('--type', choices=['factual', 'experiential'],
                             help='Filter by memory type')
    query_parser.add_argument('--min-confidence', type=float, default=0.5,
                             help='Minimum confidence threshold')

    # Promote command
    promote_parser = subparsers.add_parser('promote', help='Promote working memory to permanent')
    promote_parser.add_argument('path', help='Path to working memory file')
    promote_parser.add_argument('--type', choices=['factual', 'experiential'], required=True,
                               help='Target memory type')

    # Status command
    subparsers.add_parser('status', help='Show memory vault status')

    # Retrieve command
    retrieve_parser = subparsers.add_parser('retrieve', help='Retrieve memories by task type with budget constraints')
    retrieve_parser.add_argument('task_type', choices=['explore', 'locate', 'edit', 'validate'],
                                help='Task type for retrieval budget')
    retrieve_parser.add_argument('--module', help='Filter by specific module')

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Handle modules argument
    if hasattr(args, 'modules') and args.modules:
        args.modules = [m.strip() for m in args.modules.split(',')]

    # Route to appropriate command
    if args.command == 'capture':
        return cmd_capture(args)
    elif args.command == 'query':
        return cmd_query(args)
    elif args.command == 'promote':
        return cmd_promote(args)
    elif args.command == 'status':
        return cmd_status(args)
    elif args.command == 'retrieve':
        return cmd_retrieve(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())