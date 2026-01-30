function formatWeather(data) {
  if (data.error) return `🌤️ Weather\nError: ${data.error}`;
  return [
    `🌤️ Weather — ${data.location}`,
    `${data.condition} | ${data.temp_f}°F (feels like ${data.feels_like_f}°F)`,
    `High: ${data.high_f}°F / Low: ${data.low_f}°F`,
    `Humidity: ${data.humidity}% | Wind: ${data.wind_mph} mph ${data.wind_dir}`,
    `UV: ${data.uv_index} | Rain chance: ${data.precip_chance}%`,
    `Sunrise: ${data.sunrise} | Sunset: ${data.sunset}`,
  ].join('\n');
}

function formatCalendar(data) {
  if (!data.available) return `📅 Calendar\n${data.note}`;
  if (data.error) return `📅 Calendar\nError: ${data.error}`;
  if (!data.events || data.events.length === 0) return `📅 Calendar\nNo events today — wide open!`;
  const lines = [`📅 Calendar — ${data.count} event${data.count !== 1 ? 's' : ''}`];
  for (const e of data.events) {
    if (e.raw) {
      lines.push(`  ${e.raw}`);
    } else {
      const loc = e.location ? ` @ ${e.location}` : '';
      lines.push(`  ${e.start_time} — ${e.title}${loc}`);
    }
  }
  return lines.join('\n');
}

function formatGit(data) {
  if (data.error) return `📦 Git Status\nError: ${data.error}`;
  const lines = [`📦 Git Status — ${data.totalRepos} repos`];

  if (data.dirtyRepos > 0) lines.push(`⚠ ${data.dirtyRepos} with uncommitted changes`);
  if (data.reposWithRecentCommits > 0) lines.push(`✓ ${data.reposWithRecentCommits} with recent commits`);

  const interesting = data.repos.filter(r => r.uncommitted > 0 || r.ahead > 0 || r.behind > 0 || r.recentCommits > 0);
  for (const r of interesting) {
    const flags = [];
    if (r.uncommitted > 0) flags.push(`${r.uncommitted} uncommitted`);
    if (r.ahead > 0) flags.push(`↑${r.ahead}`);
    if (r.behind > 0) flags.push(`↓${r.behind}`);
    if (r.recentCommits > 0) flags.push(`${r.recentCommits} recent`);
    lines.push(`  ${r.name} (${r.branch}) — ${flags.join(', ')}`);
  }

  if (interesting.length === 0 && data.dirtyRepos === 0) lines.push('All clean!');
  return lines.join('\n');
}

function formatSystem(data) {
  if (data.error) return `🖥️ System\nError: ${data.error}`;
  const lines = [
    `🖥️ System Health`,
    `Uptime: ${data.uptime} | CPUs: ${data.cpus}`,
    `Load: ${data.load['1m']} / ${data.load['5m']} / ${data.load['15m']}`,
    `Memory: ${data.memory.percent}% (${data.memory.used_gb}/${data.memory.total_gb} GB)`,
  ];

  if (data.disks) {
    const warns = data.disks.filter(d => d.warning);
    if (warns.length > 0) {
      for (const d of warns) {
        lines.push(`⚠️ Disk ${d.mount}: ${d.percent}% (${d.used}/${d.size})`);
      }
    } else {
      lines.push('Disks: All healthy');
    }
  }
  return lines.join('\n');
}

function formatK8s(data) {
  if (!data.available) return `☸️ Kubernetes\n${data.note}`;
  if (data.error) return `☸️ Kubernetes\nError: ${data.error}`;

  const lines = [`☸️ Kubernetes`];

  if (data.nodes) {
    lines.push(`Nodes: ${data.nodesReady}/${data.nodeCount} ready`);
  }
  lines.push(`Pods: ${data.totalPods} total`);

  if (data.unhealthyCount > 0) {
    lines.push(`⚠ ${data.unhealthyCount} unhealthy pods:`);
    for (const p of data.unhealthyPods.slice(0, 5)) {
      lines.push(`  ${p.namespace}/${p.name} (${p.phase})`);
    }
  } else {
    lines.push('All pods healthy ✓');
  }

  if (data.restartIssueCount > 0) {
    lines.push(`🔄 ${data.restartIssueCount} restart loops:`);
    for (const r of data.restartIssues.slice(0, 5)) {
      lines.push(`  ${r.namespace}/${r.pod}:${r.container} (${r.restarts}x)`);
    }
  }

  return lines.join('\n');
}

function formatPlain(results) {
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

  const parts = [`☀️ DAILY BRIEFING — ${dateStr} ${timeStr}`, ''];

  const s = results.sections;
  if (s.weather) parts.push(formatWeather(s.weather), '');
  if (s.calendar) parts.push(formatCalendar(s.calendar), '');
  if (s.git) parts.push(formatGit(s.git), '');
  if (s.system) parts.push(formatSystem(s.system), '');
  if (s.kubernetes) parts.push(formatK8s(s.kubernetes), '');

  return parts.join('\n');
}

module.exports = { formatPlain };
