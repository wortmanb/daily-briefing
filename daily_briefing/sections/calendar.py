"""Calendar section — Google Calendar API with service account."""

import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Default paths
DEFAULT_KEY_PATH = Path.home() / ".config" / "daily-briefing" / "service-account.json"
DEFAULT_CALENDARS_PATH = Path.home() / ".config" / "daily-briefing" / "calendars.json"


def _get_key_path():
    """Resolve the service account key file path."""
    env_path = os.environ.get("GOOGLE_SA_KEY")
    if env_path:
        p = Path(env_path).expanduser()
        if p.exists():
            return p
    if DEFAULT_KEY_PATH.exists():
        return DEFAULT_KEY_PATH
    return None


def _get_calendar_ids():
    """Load calendar IDs from config file or env var.

    Config file format (JSON array):
        [{"id": "user@example.com", "name": "Personal"}, ...]

    Env var format (comma-separated):
        GOOGLE_CALENDAR_IDS=user@example.com,work@example.com
    """
    env_ids = os.environ.get("GOOGLE_CALENDAR_IDS")
    if env_ids:
        return [{"id": c.strip(), "name": c.strip()} for c in env_ids.split(",") if c.strip()]

    cal_path = os.environ.get("GOOGLE_CALENDARS_FILE")
    if cal_path:
        p = Path(cal_path).expanduser()
    else:
        p = DEFAULT_CALENDARS_PATH

    if p.exists():
        try:
            with open(p) as f:
                cals = json.load(f)
            return [{"id": c["id"], "name": c.get("name", c["id"])} for c in cals]
        except (json.JSONDecodeError, KeyError):
            pass

    return []


def get_calendar(args):
    key_path = _get_key_path()
    if not key_path:
        return {
            "available": False,
            "note": (
                "Google Calendar not configured — skipping.\n"
                "  To set up:\n"
                "  1. Create a GCP service account with Calendar API enabled\n"
                "  2. Download the JSON key\n"
                "  3. Place it at ~/.config/daily-briefing/service-account.json\n"
                "     or set GOOGLE_SA_KEY=/path/to/key.json\n"
                "  4. Share your calendar(s) with the service account email\n"
                "  5. Add calendar IDs to ~/.config/daily-briefing/calendars.json"
            ),
        }

    calendar_ids = _get_calendar_ids()
    if not calendar_ids:
        return {
            "available": False,
            "note": (
                "No calendar IDs configured — skipping.\n"
                "  Add calendars to ~/.config/daily-briefing/calendars.json:\n"
                '  [{"id": "you@example.com", "name": "Personal"}]\n'
                "  Or set GOOGLE_CALENDAR_IDS=you@example.com,work@example.com"
            ),
        }

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        return {
            "available": False,
            "note": (
                "google-api-python-client / google-auth not installed.\n"
                "  Run: pip install google-api-python-client google-auth"
            ),
        }

    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(key_path),
            scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        )
        service = build("calendar", "v3", credentials=credentials, cache_discovery=False)

        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        time_min = start_of_day.isoformat()
        time_max = end_of_day.isoformat()

        all_events = []
        for cal in calendar_ids:
            cal_id = cal["id"]
            cal_name = cal["name"]
            try:
                events_result = (
                    service.events()
                    .list(
                        calendarId=cal_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        singleEvents=True,
                        orderBy="startTime",
                        maxResults=50,
                    )
                    .execute()
                )
            except Exception:
                # Calendar not accessible — skip silently
                continue

            for event in events_result.get("items", []):
                start = event.get("start", {})
                start_dt = start.get("dateTime", start.get("date", ""))

                # Extract time portion
                start_time = ""
                if "T" in start_dt:
                    try:
                        t = datetime.fromisoformat(start_dt)
                        start_time = t.strftime("%I:%M %p").lstrip("0")
                    except ValueError:
                        start_time = start_dt
                else:
                    start_time = "All day"

                all_events.append({
                    "start_time": start_time,
                    "title": event.get("summary", "Busy"),
                    "location": event.get("location", ""),
                    "calendar": cal_name,
                    "_sort": start_dt,
                })

        # Sort by start time
        all_events.sort(key=lambda e: e.get("_sort", ""))
        # Remove sort key
        for e in all_events:
            e.pop("_sort", None)

        return {
            "available": True,
            "events": all_events,
            "count": len(all_events),
        }

    except Exception as e:
        return {"available": True, "error": str(e)}
