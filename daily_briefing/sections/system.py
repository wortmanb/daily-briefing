"""System health section — uptime, load, memory, disk usage."""

import os
import subprocess
import shutil


def _run(cmd, timeout=5):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), None
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return "", str(e)


def get_system(args):
    info = {}

    # Uptime
    try:
        with open("/proc/uptime") as f:
            uptime_sec = float(f.read().split()[0])
        days = int(uptime_sec // 86400)
        hours = int((uptime_sec % 86400) // 3600)
        mins = int((uptime_sec % 3600) // 60)
        info["uptime"] = f"{days}d {hours}h {mins}m" if days > 0 else f"{hours}h {mins}m"
    except OSError:
        info["uptime"] = "unknown"

    # Load average
    try:
        load = os.getloadavg()
        info["load"] = {
            "1m": f"{load[0]:.2f}",
            "5m": f"{load[1]:.2f}",
            "15m": f"{load[2]:.2f}",
        }
    except OSError:
        info["load"] = {"1m": "?", "5m": "?", "15m": "?"}

    # CPU count
    info["cpus"] = os.cpu_count() or 0

    # Memory
    try:
        with open("/proc/meminfo") as f:
            meminfo = {}
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip().split()[0]  # value in kB
                    meminfo[key] = int(val) * 1024  # convert to bytes

        total = meminfo.get("MemTotal", 0)
        available = meminfo.get("MemAvailable", 0)
        used = total - available
        pct = int((used / total) * 100) if total else 0

        info["memory"] = {
            "total_gb": f"{total / 1e9:.1f}",
            "used_gb": f"{used / 1e9:.1f}",
            "free_gb": f"{available / 1e9:.1f}",
            "percent": str(pct),
        }
    except OSError:
        info["memory"] = {"total_gb": "?", "used_gb": "?", "free_gb": "?", "percent": "?"}

    # Disk usage
    out, err = _run(
        ["df", "-h", "--output=target,size,used,avail,pcent", "-x", "tmpfs", "-x", "devtmpfs", "-x", "overlay"]
    )
    if not err and out:
        lines = out.splitlines()[1:]  # skip header
        disks = []
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 5:
                pct = int(parts[4].rstrip("%")) if parts[4].rstrip("%").isdigit() else 0
                disks.append({
                    "mount": parts[0],
                    "size": parts[1],
                    "used": parts[2],
                    "avail": parts[3],
                    "percent": pct,
                    "warning": pct > 80,
                })
        info["disks"] = disks
        info["diskWarnings"] = len([d for d in disks if d["warning"]])

    return info
