"""Terminal formatter — colorful ANSI output."""

from datetime import datetime

# ANSI codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BG_BLUE = "\033[44m"


def _header(emoji, title):
    return f"\n{BOLD}{CYAN}{emoji}  {title}{RESET}\n{'─' * 50}"


def _fmt_weather(data):
    if data.get("error"):
        return f"{_header('🌤️', 'Weather')}\n  {RED}Error: {data['error']}{RESET}"
    return "\n".join([
        _header("🌤️", f"Weather — {data['location']}"),
        f"  {BOLD}{data['condition']}{RESET}  {data['temp_f']}°F (feels like {data['feels_like_f']}°F)",
        f"  {DIM}High: {data['high_f']}°F  Low: {data['low_f']}°F{RESET}",
        f"  💧 Humidity: {data['humidity']}%  🌬️  Wind: {data['wind_mph']} mph {data['wind_dir']}",
        f"  ☀️  UV: {data['uv_index']}  🌧️  Rain: {data['precip_chance']}%",
        f"  🌅 Sunrise: {data['sunrise']}  🌇 Sunset: {data['sunset']}",
    ])


def _fmt_calendar(data):
    if data.get("error"):
        return f"{_header('📅', 'Calendar')}\n  {RED}Error: {data['error']}{RESET}"
    if not data.get("available"):
        return f"{_header('📅', 'Calendar')}\n  {DIM}{data.get('note', 'Not configured')}{RESET}"
    events = data.get("events", [])
    if not events:
        return f"{_header('📅', 'Calendar')}\n  {GREEN}No events today — wide open!{RESET}"
    count = data.get("count", len(events))
    lines = [_header("📅", f"Calendar — {count} event{'s' if count != 1 else ''}")]
    for e in events:
        loc = f"  {DIM}@ {e['location']}{RESET}" if e.get("location") else ""
        lines.append(f"  {BOLD}{e['start_time']}{RESET} {e['title']}{loc}")
    return "\n".join(lines)


def _fmt_git(data):
    if data.get("error"):
        return f"{_header('📦', 'Git Status')}\n  {RED}Error: {data['error']}{RESET}"
    lines = [_header("📦", f"Git Status — {data['totalRepos']} repos")]

    if data["dirtyRepos"] > 0:
        n = data["dirtyRepos"]
        lines.append(f"  {YELLOW}⚠ {n} repo{'s' if n > 1 else ''} with uncommitted changes{RESET}")
    if data["reposWithRecentCommits"] > 0:
        n = data["reposWithRecentCommits"]
        lines.append(f"  {GREEN}✓ {n} repo{'s' if n > 1 else ''} with commits in last 24h{RESET}")

    interesting = [
        r for r in data["repos"]
        if r["uncommitted"] > 0 or r.get("ahead", 0) > 0 or r.get("behind", 0) > 0 or r["recentCommits"] > 0
    ]
    if interesting:
        lines.append("")
        for r in interesting:
            flags = []
            if r["uncommitted"] > 0:
                flags.append(f"{YELLOW}{r['uncommitted']} uncommitted{RESET}")
            if r.get("ahead", 0) > 0:
                flags.append(f"{GREEN}↑{r['ahead']}{RESET}")
            if r.get("behind", 0) > 0:
                flags.append(f"{RED}↓{r['behind']}{RESET}")
            if r["recentCommits"] > 0:
                flags.append(f"{CYAN}{r['recentCommits']} recent{RESET}")
            lines.append(f"  {BOLD}{r['name']}{RESET} ({r['branch']}) — {', '.join(flags)}")

    if data.get("errors"):
        for e in data["errors"]:
            lines.append(f"  {RED}{e}{RESET}")

    if not interesting and data["dirtyRepos"] == 0:
        lines.append(f"  {GREEN}All clean!{RESET}")

    return "\n".join(lines)


def _fmt_system(data):
    if data.get("error"):
        return f"{_header('🖥️', 'System')}\n  {RED}Error: {data['error']}{RESET}"

    mem = data.get("memory", {})
    pct = int(mem.get("percent", 0))
    mem_color = RED if pct > 80 else YELLOW if pct > 60 else GREEN

    lines = [
        _header("🖥️", "System Health"),
        f"  ⏱️  Uptime: {data['uptime']}  |  CPUs: {data['cpus']}",
        f"  📊 Load: {data['load']['1m']} / {data['load']['5m']} / {data['load']['15m']}",
        f"  🧠 Memory: {mem_color}{mem['percent']}%{RESET} ({mem['used_gb']}/{mem['total_gb']} GB)",
    ]

    if data.get("disks"):
        lines.append("  💾 Disks:")
        for d in data["disks"]:
            d_color = RED if d["warning"] else GREEN
            warn = " ⚠️" if d["warning"] else ""
            lines.append(f"     {d['mount']}: {d_color}{d['percent']}%{RESET} ({d['used']}/{d['size']}){warn}")

    return "\n".join(lines)


def _fmt_k8s(data):
    if data.get("error"):
        return f"{_header('☸️', 'Kubernetes')}\n  {RED}Error: {data['error']}{RESET}"
    if not data.get("available"):
        return f"{_header('☸️', 'Kubernetes')}\n  {DIM}{data.get('note', 'Not available')}{RESET}"

    lines = [_header("☸️", "Kubernetes")]

    if data.get("nodes"):
        ready = data["nodesReady"]
        total = data["nodeCount"]
        color = GREEN if ready == total else RED
        lines.append(f"  🖧  Nodes: {color}{ready}/{total} ready{RESET}")

    lines.append(f"  📦 Pods: {data['totalPods']} total")

    if data.get("unhealthyCount", 0) > 0:
        n = data["unhealthyCount"]
        lines.append(f"  {RED}⚠ {n} unhealthy pod{'s' if n > 1 else ''}:{RESET}")
        for p in data["unhealthyPods"][:10]:
            lines.append(f"     {RED}{p['namespace']}/{p['name']} ({p['phase']}){RESET}")
    else:
        lines.append(f"  {GREEN}✓ All pods healthy{RESET}")

    if data.get("restartIssueCount", 0) > 0:
        n = data["restartIssueCount"]
        lines.append(f"  {YELLOW}🔄 {n} container{'s' if n > 1 else ''} with restart loops:{RESET}")
        for r in data["restartIssues"][:10]:
            lines.append(f"     {YELLOW}{r['namespace']}/{r['pod']}:{r['container']} ({r['restarts']} restarts){RESET}")

    return "\n".join(lines)


def format_terminal(results):
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p").lstrip("0")

    parts = [
        f"\n{BOLD}{BG_BLUE}{WHITE} ☀️  DAILY BRIEFING — {date_str} {time_str} {RESET}\n",
    ]

    s = results["sections"]
    for key in ["weather", "calendar", "git", "system", "kubernetes"]:
        if key in s:
            formatter = {
                "weather": _fmt_weather,
                "calendar": _fmt_calendar,
                "git": _fmt_git,
                "system": _fmt_system,
                "kubernetes": _fmt_k8s,
            }[key]
            parts.append(formatter(s[key]))

    parts.append(f"\n{DIM}Generated at {results['timestamp']}{RESET}\n")
    return "\n".join(parts)
