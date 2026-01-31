#!/bin/bash
exec "$(dirname "$(readlink -f "$0")")/.venv/bin/daily-briefing" "$@"
