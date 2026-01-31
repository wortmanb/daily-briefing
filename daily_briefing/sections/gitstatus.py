"""Git status section — scans repos for uncommitted changes, ahead/behind, recent commits."""

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _run(cmd, cwd=None, timeout=10):
    """Run a command and return (stdout, error)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        if result.returncode != 0:
            return "", result.stderr.strip()
        return result.stdout.strip(), None
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return "", str(e)


def _scan_repo(repo_path):
    """Scan a single git repo for status info."""
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        return None

    name = repo_path.name
    info = {"name": name, "path": str(repo_path)}
    cwd = str(repo_path)

    # Uncommitted changes
    out, err = _run(["git", "status", "--porcelain"], cwd=cwd)
    if err is None and out:
        info["uncommitted"] = len([l for l in out.splitlines() if l.strip()])
    else:
        info["uncommitted"] = 0

    # Current branch
    out, err = _run(["git", "branch", "--show-current"], cwd=cwd)
    info["branch"] = out if not err else "unknown"
    if not info["branch"]:
        info["branch"] = "detached"

    # Ahead/behind
    out, err = _run(
        ["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
        cwd=cwd,
    )
    if not err and out:
        parts = out.split()
        info["ahead"] = int(parts[0]) if len(parts) > 0 else 0
        info["behind"] = int(parts[1]) if len(parts) > 1 else 0
    else:
        info["ahead"] = 0
        info["behind"] = 0

    # Recent commits (last 24h)
    since = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    out, err = _run(
        ["git", "log", f"--since={since}", "--oneline", "--no-merges"],
        cwd=cwd,
    )
    if not err and out:
        info["recentCommits"] = len([l for l in out.splitlines() if l.strip()])
    else:
        info["recentCommits"] = 0

    return info


def get_git_status(args):
    repos = []
    errors = []

    for d in args.git_dirs:
        expanded = Path(d).expanduser()
        try:
            entries = sorted(expanded.iterdir())
            for entry in entries:
                if entry.is_dir() and not entry.name.startswith("."):
                    result = _scan_repo(entry)
                    if result:
                        repos.append(result)
        except OSError as e:
            errors.append(f"{d}: {e}")

    # Sort: repos with activity first, then alphabetical
    repos.sort(
        key=lambda r: (
            -(1 if r["uncommitted"] > 0 or r.get("ahead", 0) > 0 else 0),
            r["name"].lower(),
        )
    )

    dirty = [r for r in repos if r["uncommitted"] > 0]
    with_recent = [r for r in repos if r["recentCommits"] > 0]

    result = {
        "totalRepos": len(repos),
        "dirtyRepos": len(dirty),
        "reposWithRecentCommits": len(with_recent),
        "repos": repos,
    }
    if errors:
        result["errors"] = errors

    return result
