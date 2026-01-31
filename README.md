# daily-briefing ☀️

A CLI tool that generates a morning briefing — weather, calendar, git status, system health, and Kubernetes status — all in one command.

Minimal dependencies. Python 3.9+ and your existing tools.

## Install

```bash
# Clone and install
git clone git@github.com:wortmanb/daily-briefing.git
cd daily-briefing
pip install -e .

# Or install directly from GitHub
pip install git+ssh://git@github.com/wortmanb/daily-briefing.git
```

## Usage

```bash
# Full briefing with colors
daily-briefing

# Plain text (great for Telegram/messaging)
daily-briefing --format plain

# JSON output (pipe to jq, etc.)
daily-briefing --format json | jq '.sections.weather'

# Only specific sections
daily-briefing --sections weather,git

# Custom location
daily-briefing --location "Portland, OR"

# Custom git directories
daily-briefing --git-dirs ~/projects,~/work
```

## Sections

| Section | Source | Requires |
|---------|--------|----------|
| **Weather** | [wttr.in](https://wttr.in) API | Internet |
| **Calendar** | Google Calendar API | Service account (see setup below) |
| **Git Status** | Local git repos | git |
| **System** | OS stats (`/proc`, `df`) | Linux |
| **Kubernetes** | `kubectl` | kubectl + cluster access |

All sections degrade gracefully — if a tool isn't available or not configured, it skips with a note instead of crashing.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BRIEFING_LOCATION` | `Jeffersonton, VA 22724` | Weather location |
| `BRIEFING_GIT_DIRS` | `~/git` | Comma-separated directories to scan for git repos |
| `GOOGLE_SA_KEY` | `~/.config/daily-briefing/service-account.json` | Path to Google service account JSON key |

### CLI Flags

| Flag | Description |
|------|-------------|
| `--format <terminal\|plain\|json>` | Output format (default: terminal) |
| `--sections <list>` | Comma-separated sections to include |
| `--location <city>` | Override weather location |
| `--git-dirs <dirs>` | Override git directories to scan |
| `--help` | Show help |

## Google Calendar Setup

The calendar section uses a Google Cloud service account (works headless — no browser needed).

1. **Create a GCP project** (or use an existing one)
2. **Enable the Google Calendar API** in the project
3. **Create a service account** and download the JSON key file
4. **Share your calendar(s)** with the service account email (found in the JSON key as `client_email`)
5. **Place the key file** at one of:
   - `~/.config/daily-briefing/service-account.json` (default)
   - Any path, then set `GOOGLE_SA_KEY=/path/to/key.json`

If no key file is found, the calendar section gracefully skips with setup instructions.

## Example Output

```
☀️ DAILY BRIEFING — Saturday, January 31, 2026 7:00 AM

🌤️ Weather — Jeffersonton, VA 22724
Partly Cloudy | 32°F (feels like 28°F)
High: 45°F / Low: 25°F
Humidity: 72% | Wind: 5 mph NNW
UV: 2 | Rain chance: 10%
Sunrise: 07:15 AM | Sunset: 05:32 PM

📅 Calendar
Google Calendar not configured — skipping.

📦 Git Status — 12 repos
⚠ 2 repos with uncommitted changes
✓ 3 repos with commits in last 24h

  daily-briefing (python-rewrite) — 5 uncommitted
  friday-ui (main) — 2 recent

🖥️ System Health
Uptime: 15d 3h 42m | CPUs: 8
Load: 0.45 / 0.38 / 0.31
Memory: 42% (6.7/16.0 GB)
Disks: All healthy

☸️ Kubernetes
Nodes: 6/6 ready
Pods: 47 total
All pods healthy ✓
```

## Development

```bash
# Install in dev mode
pip install -e .

# Run directly
python -m daily_briefing

# Run specific sections
daily-briefing --sections weather,system --format plain
```

## Migration from v1 (Node.js)

v2 is a complete rewrite in Python. Key changes:
- **Calendar**: Uses Google Calendar API with a service account instead of `gcalcli` (works headless)
- **Default location**: Changed from Austin, TX to Jeffersonton, VA 22724
- **Dependencies**: Only `google-api-python-client` and `google-auth` (for calendar); everything else uses Python stdlib
- **Concurrency**: Uses `concurrent.futures.ThreadPoolExecutor` for parallel section execution

The CLI interface is identical — same flags, same env vars, same output formats.

## License

MIT
