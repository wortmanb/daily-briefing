const c = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  bgBlue: '\x1b[44m',
};

function header(emoji, title) {
  return `\n${c.bold}${c.cyan}${emoji}  ${title}${c.reset}\n${'─'.repeat(50)}`;
}

function formatWeather(data) {
  if (data.error) return `${header('🌤️', 'Weather')}  \n  ${c.red}Error: ${data.error}${c.reset}`;
  const lines = [
    header('🌤️', `Weather — ${data.location}`),
    `  ${c.bold}${data.condition}${c.reset}  ${data.temp_f}°F (feels like ${data.feels_like_f}°F)`,
    `  ${c.dim}High: ${data.high_f}°F  Low: ${data.low_f}°F${c.reset}`,
    `  💧 Humidity: ${data.humidity}%  🌬️  Wind: ${data.wind_mph} mph ${data.wind_dir}`,
    `  ☀️  UV: ${data.uv_index}  🌧️  Rain: ${data.precip_chance}%`,
    `  🌅 Sunrise: ${data.sunrise}  🌇 Sunset: ${data.sunset}`,
  ];
  return lines.join('\n');
}

function formatCalendar(data) {
  if (data.error) return `${header('📅', 'Calendar')}\n  ${c.red}Error: ${data.error}${c.reset}`;
  if (!data.available) return `${header('📅', 'Calendar')}\n  ${c.dim}${data.note}${c.reset}`;
  if (!data.events || data.events.length === 0) {
    return `${header('📅', 'Calendar')}\n  ${c.green}No events today — wide open!${c.reset}`;
  }
  const lines = [header('📅', `Calendar — ${data.count} event${data.count !== 1 ? 's' : ''}`)];
  for (const e of data.events) {
    if (e.raw) {
      lines.push(`  ${e.raw}`);
    } else {
      const loc = e.location ? `  ${c.dim}@ ${e.location}${c.reset}` : '';
      lines.push(`  ${c.bold}${e.start_time}${c.reset} ${e.title}${loc}`);
    }
  }
  return lines.join('\n');
}

function formatGit(data) {
  if (data.error) return `${header('📦', 'Git Status')}\n  ${c.red}Error: ${data.error}${c.reset}`;
  const lines = [header('📦', `Git Status — ${data.totalRepos} repos`)];

  if (data.dirtyRepos > 0) {
    lines.push(`  ${c.yellow}⚠ ${data.dirtyRepos} repo${data.dirtyRepos > 1 ? 's' : ''} with uncommitted changes${c.reset}`);
  }
  if (data.reposWithRecentCommits > 0) {
    lines.push(`  ${c.green}✓ ${data.reposWithRecentCommits} repo${data.reposWithRecentCommits > 1 ? 's' : ''} with commits in last 24h${c.reset}`);
  }

  const interesting = data.repos.filter(r => r.uncommitted > 0 || r.ahead > 0 || r.behind > 0 || r.recentCommits > 0);
  if (interesting.length > 0) {
    lines.push('');
    for (const r of interesting) {
      const flags = [];
      if (r.uncommitted > 0) flags.push(`${c.yellow}${r.uncommitted} uncommitted${c.reset}`);
      if (r.ahead > 0) flags.push(`${c.green}↑${r.ahead}${c.reset}`);
      if (r.behind > 0) flags.push(`${c.red}↓${r.behind}${c.reset}`);
      if (r.recentCommits > 0) flags.push(`${c.cyan}${r.recentCommits} recent${c.reset}`);
      lines.push(`  ${c.bold}${r.name}${c.reset} (${r.branch}) — ${flags.join(', ')}`);
    }
  }

  if (data.errors) {
    for (const e of data.errors) lines.push(`  ${c.red}${e}${c.reset}`);
  }

  if (interesting.length === 0 && data.dirtyRepos === 0) {
    lines.push(`  ${c.green}All clean!${c.reset}`);
  }

  return lines.join('\n');
}

function formatSystem(data) {
  if (data.error) return `${header('🖥️', 'System')}\n  ${c.red}Error: ${data.error}${c.reset}`;
  const memColor = parseInt(data.memory.percent) > 80 ? c.red : parseInt(data.memory.percent) > 60 ? c.yellow : c.green;
  const lines = [
    header('🖥️', 'System Health'),
    `  ⏱️  Uptime: ${data.uptime}  |  CPUs: ${data.cpus}`,
    `  📊 Load: ${data.load['1m']} / ${data.load['5m']} / ${data.load['15m']}`,
    `  🧠 Memory: ${memColor}${data.memory.percent}%${c.reset} (${data.memory.used_gb}/${data.memory.total_gb} GB)`,
  ];

  if (data.disks) {
    lines.push(`  💾 Disks:`);
    for (const d of data.disks) {
      const dColor = d.warning ? c.red : c.green;
      const warn = d.warning ? ' ⚠️' : '';
      lines.push(`     ${d.mount}: ${dColor}${d.percent}%${c.reset} (${d.used}/${d.size})${warn}`);
    }
  }

  return lines.join('\n');
}

function formatK8s(data) {
  if (data.error) return `${header('☸️', 'Kubernetes')}\n  ${c.red}Error: ${data.error}${c.reset}`;
  if (!data.available) return `${header('☸️', 'Kubernetes')}\n  ${c.dim}${data.note}${c.reset}`;

  const lines = [header('☸️', 'Kubernetes')];

  if (data.nodes) {
    const readyStr = data.nodesReady === data.nodeCount
      ? `${c.green}${data.nodesReady}/${data.nodeCount} ready${c.reset}`
      : `${c.red}${data.nodesReady}/${data.nodeCount} ready${c.reset}`;
    lines.push(`  🖧  Nodes: ${readyStr}`);
  }

  lines.push(`  📦 Pods: ${data.totalPods} total`);

  if (data.unhealthyCount > 0) {
    lines.push(`  ${c.red}⚠ ${data.unhealthyCount} unhealthy pod${data.unhealthyCount > 1 ? 's' : ''}:${c.reset}`);
    for (const p of data.unhealthyPods.slice(0, 10)) {
      lines.push(`     ${c.red}${p.namespace}/${p.name} (${p.phase})${c.reset}`);
    }
  } else {
    lines.push(`  ${c.green}✓ All pods healthy${c.reset}`);
  }

  if (data.restartIssueCount > 0) {
    lines.push(`  ${c.yellow}🔄 ${data.restartIssueCount} container${data.restartIssueCount > 1 ? 's' : ''} with restart loops:${c.reset}`);
    for (const r of data.restartIssues.slice(0, 10)) {
      lines.push(`     ${c.yellow}${r.namespace}/${r.pod}:${r.container} (${r.restarts} restarts)${c.reset}`);
    }
  }

  return lines.join('\n');
}

function formatTerminal(results) {
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

  const parts = [
    `\n${c.bold}${c.bgBlue}${c.white} ☀️  DAILY BRIEFING — ${dateStr} ${timeStr} ${c.reset}\n`,
  ];

  const s = results.sections;
  if (s.weather) parts.push(formatWeather(s.weather));
  if (s.calendar) parts.push(formatCalendar(s.calendar));
  if (s.git) parts.push(formatGit(s.git));
  if (s.system) parts.push(formatSystem(s.system));
  if (s.kubernetes) parts.push(formatK8s(s.kubernetes));

  parts.push(`\n${c.dim}Generated at ${results.timestamp}${c.reset}\n`);

  return parts.join('\n');
}

module.exports = { formatTerminal };
