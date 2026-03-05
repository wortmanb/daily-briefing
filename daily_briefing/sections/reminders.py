"""Reminders section — simple file-based reminders."""

from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path
from typing import List, Tuple

DEFAULT_FILE = Path.home() / ".config" / "daily-briefing" / "reminders.txt"


def _parse_line(line: str) -> Tuple[date | None, str] | None:
    raw = line.strip()
    if not raw or raw.startswith("#"):
        return None
    if "|" in raw:
        left, right = raw.split("|", 1)
        left = left.strip()
        right = right.strip()
        try:
            d = datetime.strptime(left, "%Y-%m-%d").date()
            return d, right
        except ValueError:
            return None, raw
    return None, raw


def _load_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return path.read_text().splitlines()


def _write_lines(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines).rstrip()
    if content:
        path.write_text(content + "\n")
    else:
        path.write_text("")


def get_reminders(_args=None):
    path = Path(os.environ.get("BRIEFING_REMINDERS_FILE", str(DEFAULT_FILE)))
    today = date.today()
    lines = _load_lines(path)

    reminders: List[str] = []
    keep: List[str] = []

    for line in lines:
        parsed = _parse_line(line)
        if parsed is None:
            continue
        d, text = parsed
        if d is None:
            reminders.append(text)
            keep.append(line)
            continue
        if d <= today:
            reminders.append(text)
        else:
            keep.append(line)

    if lines != keep:
        _write_lines(path, keep)

    if not reminders:
        return {"available": False, "note": "No reminders"}

    return {
        "available": True,
        "count": len(reminders),
        "reminders": reminders,
    }
