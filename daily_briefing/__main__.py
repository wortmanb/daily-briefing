"""Entry point for python -m daily_briefing and the console script."""

import sys

from .cli import parse_args
from .briefing import run_briefing
from .formatters.terminal import format_terminal
from .formatters.plain import format_plain
from .formatters.json_fmt import format_json

FORMATTERS = {
    "terminal": format_terminal,
    "plain": format_plain,
    "json": format_json,
}


def main():
    args = parse_args()
    formatter = FORMATTERS.get(args.format)
    if not formatter:
        print(f"Unknown format: {args.format}", file=sys.stderr)
        sys.exit(1)

    results = run_briefing(args)
    print(formatter(results))


if __name__ == "__main__":
    main()
