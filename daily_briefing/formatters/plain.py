"""Plain text formatter — messaging-friendly output."""

from datetime import datetime


def _fmt_weather(data):
    if data.get("error"):
        return f"🌤️ Weather\nError: {data['error']}"
    return "\n".join([
        f"🌤️ Weather — {data['location']}",
        f"{data['condition']} | {data['temp_f']}°F (feels like {data['feels_like_f']}°F)",
        f"High: {data['high_f']}°F / Low: {data['low_f']}°F",
        f"Humidity: {data['humidity']}% | Wind: {data['wind_mph']} mph {data['wind_dir']}",
        f"UV: {data['uv_index']} | Rain chance: {data['precip_chance']}%",
        f"Sunrise: {data['sunrise']} | Sunset: {data['sunset']}",
    ])


def _fmt_calendar(data):
    if not data.get("available"):
        return f"📅 Calendar\n{data.get('note', 'Not configured')}"
    if data.get("error"):
        return f"📅 Calendar\nError: {data['error']}"
    events = data.get("events", [])
    if not events:
        return "📅 Calendar\nNo events today — wide open!"
    count = data.get("count", len(events))
    lines = [f"📅 Calendar — {count} event{'s' if count != 1 else ''}"]
    for e in events:
        loc = f" @ {e['location']}" if e.get("location") else ""
        lines.append(f"  {e['start_time']} — {e['title']}{loc}")
    return "\n".join(lines)


def _fmt_reminders(data):
    if not data.get("available"):
        return f"📝 Reminders\n{data.get('note', 'No reminders')}"
    if data.get("error"):
        return f"📝 Reminders\nError: {data['error']}"
    reminders = data.get("reminders", [])
    if not reminders:
        return "📝 Reminders\nNo reminders"
    lines = ["📝 Reminders"]
    for r in reminders:
        lines.append(f"  • {r}")
    return "\n".join(lines)


def _fmt_git(data):
    if data.get("error"):
        return f"📦 Git Status\nError: {data['error']}"
    lines = [f"📦 Git Status — {data['totalRepos']} repos"]

    if data["dirtyRepos"] > 0:
        lines.append(f"⚠ {data['dirtyRepos']} with uncommitted changes")
    if data["reposWithRecentCommits"] > 0:
        lines.append(f"✓ {data['reposWithRecentCommits']} with recent commits")

    interesting = [
        r for r in data["repos"]
        if r["uncommitted"] > 0 or r.get("ahead", 0) > 0 or r.get("behind", 0) > 0 or r["recentCommits"] > 0
    ]
    for r in interesting:
        flags = []
        if r["uncommitted"] > 0:
            flags.append(f"{r['uncommitted']} uncommitted")
        if r.get("ahead", 0) > 0:
            flags.append(f"↑{r['ahead']}")
        if r.get("behind", 0) > 0:
            flags.append(f"↓{r['behind']}")
        if r["recentCommits"] > 0:
            flags.append(f"{r['recentCommits']} recent")
        lines.append(f"  {r['name']} ({r['branch']}) — {', '.join(flags)}")

    if not interesting and data["dirtyRepos"] == 0:
        lines.append("All clean!")
    return "\n".join(lines)


def _fmt_system(data):
    if data.get("error"):
        return f"🖥️ System\nError: {data['error']}"
    lines = [
        "🖥️ System Health",
        f"Uptime: {data['uptime']} | CPUs: {data['cpus']}",
        f"Load: {data['load']['1m']} / {data['load']['5m']} / {data['load']['15m']}",
        f"Memory: {data['memory']['percent']}% ({data['memory']['used_gb']}/{data['memory']['total_gb']} GB)",
    ]
    disks = data.get("disks", [])
    warns = [d for d in disks if d.get("warning")]
    if warns:
        for d in warns:
            lines.append(f"⚠️ Disk {d['mount']}: {d['percent']}% ({d['used']}/{d['size']})")
    else:
        lines.append("Disks: All healthy")
    return "\n".join(lines)


def _fmt_k8s(data):
    if not data.get("available"):
        return f"☸️ Kubernetes\n{data.get('note', 'Not available')}"
    if data.get("error"):
        return f"☸️ Kubernetes\nError: {data['error']}"

    lines = ["☸️ Kubernetes"]
    if data.get("nodes"):
        lines.append(f"Nodes: {data['nodesReady']}/{data['nodeCount']} ready")
    lines.append(f"Pods: {data['totalPods']} total")

    if data.get("unhealthyCount", 0) > 0:
        lines.append(f"⚠ {data['unhealthyCount']} unhealthy pods:")
        for p in data["unhealthyPods"][:5]:
            lines.append(f"  {p['namespace']}/{p['name']} ({p['phase']})")
    else:
        lines.append("All pods healthy ✓")

    if data.get("restartIssueCount", 0) > 0:
        lines.append(f"🔄 {data['restartIssueCount']} restart loops:")
        for r in data["restartIssues"][:5]:
            lines.append(f"  {r['namespace']}/{r['pod']}:{r['container']} ({r['restarts']}x)")

    return "\n".join(lines)


def format_plain(results):
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p").lstrip("0")

    parts = [f"☀️ DAILY BRIEFING — {date_str} {time_str}", ""]

    s = results["sections"]
    for key in ["weather", "calendar", "reminders", "git", "system", "kubernetes"]:
        if key in s:
            formatter = {
                "weather": _fmt_weather,
                "calendar": _fmt_calendar,
                "reminders": _fmt_reminders,
                "git": _fmt_git,
                "system": _fmt_system,
                "kubernetes": _fmt_k8s,
            }[key]
            parts.append(formatter(s[key]))
            parts.append("")

    return "\n".join(parts)
