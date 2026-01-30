const { execFile } = require('child_process');
const os = require('os');
const fs = require('fs');

function run(cmd, args, opts = {}) {
  return new Promise((resolve) => {
    execFile(cmd, args, { timeout: 5000, ...opts }, (err, stdout) => {
      if (err) resolve({ error: err.message, stdout: '' });
      else resolve({ stdout: stdout.trim() });
    });
  });
}

async function getSystem() {
  const info = {};

  // Uptime
  const uptimeSec = os.uptime();
  const days = Math.floor(uptimeSec / 86400);
  const hours = Math.floor((uptimeSec % 86400) / 3600);
  const mins = Math.floor((uptimeSec % 3600) / 60);
  info.uptime = days > 0 ? `${days}d ${hours}h ${mins}m` : `${hours}h ${mins}m`;

  // Load average
  const load = os.loadavg();
  info.load = {
    '1m': load[0].toFixed(2),
    '5m': load[1].toFixed(2),
    '15m': load[2].toFixed(2),
  };
  info.cpus = os.cpus().length;

  // Memory
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const usedMem = totalMem - freeMem;
  info.memory = {
    total_gb: (totalMem / 1e9).toFixed(1),
    used_gb: (usedMem / 1e9).toFixed(1),
    free_gb: (freeMem / 1e9).toFixed(1),
    percent: ((usedMem / totalMem) * 100).toFixed(0),
  };

  // Disk usage
  const dfResult = await run('df', ['-h', '--output=target,size,used,avail,pcent', '-x', 'tmpfs', '-x', 'devtmpfs', '-x', 'overlay']);
  if (!dfResult.error && dfResult.stdout) {
    const lines = dfResult.stdout.split('\n').slice(1); // skip header
    info.disks = lines.filter(l => l.trim()).map(line => {
      const parts = line.trim().split(/\s+/);
      const pct = parseInt(parts[4]) || 0;
      return {
        mount: parts[0],
        size: parts[1],
        used: parts[2],
        avail: parts[3],
        percent: pct,
        warning: pct > 80,
      };
    });
    info.diskWarnings = info.disks.filter(d => d.warning).length;
  }

  return info;
}

module.exports = { getSystem };
