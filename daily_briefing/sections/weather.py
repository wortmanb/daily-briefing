"""Weather section — fetches current conditions from wttr.in."""

import json
import urllib.request
import urllib.parse


def get_weather(args):
    location = urllib.parse.quote(args.location)
    url = f"https://wttr.in/{location}?format=j1"
    req = urllib.request.Request(url, headers={"User-Agent": "daily-briefing/2.0"})

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

    current = data.get("current_condition", [{}])[0]
    today = data.get("weather", [{}])[0]
    hourly = today.get("hourly", [])

    # Find afternoon temp (~3pm)
    afternoon = next((h for h in hourly if h.get("time") == "1500"), hourly[-1] if hourly else {})

    return {
        "location": args.location,
        "condition": (current.get("weatherDesc", [{}])[0]).get("value", "Unknown"),
        "temp_f": current.get("temp_F", "?"),
        "temp_c": current.get("temp_C", "?"),
        "feels_like_f": current.get("FeelsLikeF", "?"),
        "humidity": current.get("humidity", "?"),
        "wind_mph": current.get("windspeedMiles", "?"),
        "wind_dir": current.get("winddir16Point", ""),
        "high_f": today.get("maxtempF", "?"),
        "low_f": today.get("mintempF", "?"),
        "high_c": today.get("maxtempC", "?"),
        "low_c": today.get("mintempC", "?"),
        "uv_index": current.get("uvIndex", "?"),
        "sunrise": (today.get("astronomy", [{}])[0]).get("sunrise", "?"),
        "sunset": (today.get("astronomy", [{}])[0]).get("sunset", "?"),
        "precip_chance": afternoon.get("chanceofrain", "0"),
    }
