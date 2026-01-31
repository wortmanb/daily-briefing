"""Kubernetes section — pod health, node status, restart loops."""

import json
import subprocess
import shutil


def _run(cmd, timeout=15):
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return "", result.stderr.strip()
        return result.stdout.strip(), None
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return "", str(e)


def get_kubernetes(args):
    # Check if kubectl is available
    if not shutil.which("kubectl"):
        return {"available": False, "note": "kubectl not installed — skipping Kubernetes"}

    info = {"available": True}

    # Get all pods as JSON
    out, err = _run(["kubectl", "get", "pods", "--all-namespaces", "-o", "json"])
    if err:
        return {"available": True, "error": err}

    try:
        pods = json.loads(out)
    except json.JSONDecodeError:
        return {"available": True, "error": "Failed to parse kubectl output"}

    items = pods.get("items", [])
    info["totalPods"] = len(items)

    # Healthy states
    healthy_phases = {"Running", "Succeeded", "Completed"}
    unhealthy = [
        p for p in items
        if p.get("status", {}).get("phase", "") not in healthy_phases
    ]
    info["unhealthyPods"] = [
        {
            "name": p.get("metadata", {}).get("name"),
            "namespace": p.get("metadata", {}).get("namespace"),
            "phase": p.get("status", {}).get("phase"),
        }
        for p in unhealthy
    ]
    info["unhealthyCount"] = len(unhealthy)

    # Check for restart loops (>5 restarts)
    restart_issues = []
    for pod in items:
        for c in pod.get("status", {}).get("containerStatuses", []):
            restarts = c.get("restartCount", 0)
            if restarts > 5:
                restart_issues.append({
                    "pod": pod.get("metadata", {}).get("name"),
                    "namespace": pod.get("metadata", {}).get("namespace"),
                    "container": c.get("name"),
                    "restarts": restarts,
                })
    info["restartIssues"] = restart_issues
    info["restartIssueCount"] = len(restart_issues)

    # Node status
    out, err = _run(["kubectl", "get", "nodes", "-o", "json"])
    if not err and out:
        try:
            nodes = json.loads(out)
            info["nodes"] = []
            for n in nodes.get("items", []):
                conditions = n.get("status", {}).get("conditions", [])
                ready = next((c for c in conditions if c.get("type") == "Ready"), None)
                labels = n.get("metadata", {}).get("labels", {})
                roles = [
                    l.replace("node-role.kubernetes.io/", "")
                    for l in labels
                    if l.startswith("node-role.kubernetes.io/")
                ]
                info["nodes"].append({
                    "name": n.get("metadata", {}).get("name"),
                    "ready": ready.get("status") == "True" if ready else False,
                    "roles": roles,
                })
            info["nodeCount"] = len(info["nodes"])
            info["nodesReady"] = len([n for n in info["nodes"] if n["ready"]])
        except (json.JSONDecodeError, KeyError):
            pass

    return info
