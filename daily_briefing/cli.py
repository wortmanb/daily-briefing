"""CLI argument parsing."""

import argparse
import os
from pathlib import Path

DEFAULT_LOCATION = "Jeffersonton, VA 22724"
DEFAULT_GIT_DIRS = os.environ.get("BRIEFING_GIT_DIRS", str(Path.home() / "git"))
ALL_SECTIONS = ["weather", "calendar", "git", "system", "kubernetes"]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="daily-briefing",
        description="Your morning briefing, one command away.",
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "plain", "json"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    parser.add_argument(
        "--sections",
        type=lambda s: [x.strip() for x in s.split(",")],
        default=ALL_SECTIONS,
        help="Comma-separated sections to include (default: all)",
    )
    parser.add_argument(
        "--location",
        default=os.environ.get("BRIEFING_LOCATION", DEFAULT_LOCATION),
        help=f"Weather location (default: {DEFAULT_LOCATION})",
    )
    parser.add_argument(
        "--git-dirs",
        type=lambda s: [x.strip() for x in s.split(",")],
        default=[d.strip() for d in DEFAULT_GIT_DIRS.split(",")],
        help="Comma-separated directories to scan for git repos",
    )
    return parser.parse_args(argv)
