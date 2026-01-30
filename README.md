# daily-briefing ☀️

A CLI tool that generates a morning briefing — weather, calendar, git status, system health, and Kubernetes status — all in one command.

Zero dependencies. Just Node.js and your existing tools.

## Install

```bash
# Clone and link
git clone https://github.com/wortmanb/daily-briefing.git
cd daily-briefing
npm link

# Or just run directly
node src/index.js
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
| **Calendar** | `gcalcli` | gcalcli installed + configured |
| **Git Status** | Local git repos | git |
| **System** | OS stats + `df` | Linux/macOS |
| **Kubernetes** | `kubectl` | kubectl + cluster access |

All sections degrade gracefully — if a tool isn't available, it skips with a note instead of crashing.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BRIEFING_LOCATION` | `Austin, TX` | Weather location |
| `BRIEFING_GIT_DIRS` | `~/git` | Comma-separated directories to scan for git repos |

### CLI Flags

| Flag | Description |
|------|-------------|
| `--format <terminal\|plain\|json>` | Output format (default: terminal) |
| `--sections <list>` | Comma-separated sections to include |
| `--location <city>` | Override weather location |
| `--git-dirs <dirs>` | Override git directories to scan |
| `--help` | Show help |

## Example Output

```
☀️ DAILY BRIEFING — Friday, January 30, 2026 7:00 AM

🌤️ Weather — Austin, TX
Partly Cloudy | 45°F (feels like 42°F)
High: 62°F / Low: 38°F
Humidity: 65% | Wind: 8 mph NNW
UV: 3 | Rain chance: 10%
Sunrise: 07:18 AM | Sunset: 06:02 PM

📅 Calendar — 3 events
  09:00 — Team standup
  11:30 — 1:1 with Sarah
  14:00 — Architecture review @ Conf Room B

📦 Git Status — 12 repos
⚠ 2 with uncommitted changes
✓ 3 with recent commits
  homelab (main) — 4 uncommitted, ↑2
  daily-briefing (main) — 1 uncommitted
  clawdbot (main) — 5 recent

🖥️ System Health
Uptime: 14d 6h 32m | CPUs: 16
Load: 1.24 / 0.98 / 0.87
Memory: 42% (13.4/32.0 GB)
Disks: All healthy

☸️ Kubernetes
Nodes: 4/4 ready
Pods: 47 total
All pods healthy ✓
```

## Integration Ideas

- **Cron job**: Run every morning and pipe to Telegram
- **Clawdbot**: Use as a morning briefing source for your AI assistant
- **tmux**: Show in a tmux pane on login

```bash
# Example: send plain briefing via curl to Telegram
daily-briefing --format plain | curl -s -X POST \
  "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
  -d chat_id="$CHAT_ID" \
  -d text="$(cat -)"
```

## License

MIT
