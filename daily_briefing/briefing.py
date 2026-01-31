"""Orchestrator — runs all sections concurrently."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from .sections.weather import get_weather
from .sections.calendar import get_calendar
from .sections.gitstatus import get_git_status
from .sections.system import get_system
from .sections.kubernetes import get_kubernetes

SECTION_RUNNERS = {
    "weather": get_weather,
    "calendar": get_calendar,
    "git": get_git_status,
    "system": get_system,
    "kubernetes": get_kubernetes,
}


def run_briefing(args):
    results = {}

    def run_section(name):
        runner = SECTION_RUNNERS.get(name)
        if not runner:
            return name, {"error": f"Unknown section: {name}"}
        try:
            return name, runner(args)
        except Exception as e:
            return name, {"error": str(e)}

    with ThreadPoolExecutor(max_workers=len(args.sections)) as pool:
        futures = {pool.submit(run_section, s): s for s in args.sections}
        for future in as_completed(futures):
            name, data = future.result()
            results[name] = data

    return {
        "sections": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
