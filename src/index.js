#!/usr/bin/env node

const { parseArgs } = require('./args');
const { runBriefing } = require('./briefing');
const { formatTerminal } = require('./formatters/terminal');
const { formatPlain } = require('./formatters/plain');
const { formatJson } = require('./formatters/json');

const formatters = {
  terminal: formatTerminal,
  plain: formatPlain,
  json: formatJson,
};

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    console.log(`
daily-briefing — Your morning briefing, one command away.

Usage:
  daily-briefing [options]

Options:
  --format <terminal|plain|json>   Output format (default: terminal)
  --sections <list>                Comma-separated sections to include
                                   (weather,calendar,git,system,kubernetes)
                                   Default: all
  --location <city>                Weather location (default: env BRIEFING_LOCATION or "Austin, TX")
  --git-dirs <dirs>                Comma-separated dirs to scan (default: env BRIEFING_GIT_DIRS or ~/git)
  --help                           Show this help

Environment Variables:
  BRIEFING_LOCATION    Default weather location
  BRIEFING_GIT_DIRS    Comma-separated git directories to scan

Examples:
  daily-briefing
  daily-briefing --format plain
  daily-briefing --sections weather,git --location "New York"
  daily-briefing --format json | jq '.weather'
`);
    process.exit(0);
  }

  const formatter = formatters[args.format];
  if (!formatter) {
    console.error(`Unknown format: ${args.format}. Use terminal, plain, or json.`);
    process.exit(1);
  }

  const results = await runBriefing(args);
  const output = formatter(results);
  console.log(output);
}

main().catch(err => {
  console.error('Briefing failed:', err.message);
  process.exit(1);
});
