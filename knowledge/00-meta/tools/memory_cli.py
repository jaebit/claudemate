#!/usr/bin/env python3
"""Memory CLI — thin dispatcher importing from memory_capture and memory_query."""

import argparse
import sys

from memory_capture import cmd_capture, cmd_promote
from memory_query import cmd_query, cmd_retrieve, cmd_status


def main() -> int:
    p = argparse.ArgumentParser(
        prog="memory_cli",
        description="Knowledge vault memory note management",
    )
    sub = p.add_subparsers(dest='command')

    # capture
    cap = sub.add_parser('capture', help='Capture a new memory note')
    cap.add_argument('type', choices=['factual', 'experiential'])
    cap.add_argument('title')
    cap.add_argument('--source-task')
    cap.add_argument('--commit')
    cap.add_argument('--modules')
    cap.add_argument('--body')
    cap.add_argument('--outcome')
    cap.add_argument('--task-type')

    # query
    qr = sub.add_parser('query', help='Search memory notes by keyword')
    qr.add_argument('keyword')
    qr.add_argument('--type', choices=['factual', 'experiential'])
    qr.add_argument('--min-confidence', type=float, default=0.5)

    # promote
    pr = sub.add_parser('promote', help='Promote working memory to permanent')
    pr.add_argument('path')
    pr.add_argument('--type', choices=['factual', 'experiential'], required=True)

    # status
    sub.add_parser('status', help='Show memory vault statistics')

    # retrieve
    ret = sub.add_parser('retrieve', help='Retrieve memories by task type + budget')
    ret.add_argument('task_type', choices=['explore', 'locate', 'edit', 'validate'])
    ret.add_argument('--module')

    args = p.parse_args()
    if not args.command:
        p.print_help()
        return 1

    if args.command == 'capture':
        if hasattr(args, 'modules') and args.modules:
            args.modules = [m.strip() for m in args.modules.split(',')]
        return cmd_capture(args)
    if args.command == 'query':
        return cmd_query(args)
    if args.command == 'promote':
        return cmd_promote(args)
    if args.command == 'status':
        return cmd_status(args)
    if args.command == 'retrieve':
        return cmd_retrieve(args)
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
