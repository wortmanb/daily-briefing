const { execFile } = require('child_process');

function run(cmd, args, opts = {}) {
  return new Promise((resolve) => {
    execFile(cmd, args, { timeout: 15000, ...opts }, (err, stdout, stderr) => {
      if (err) {
        resolve({ error: err.message, stdout: '', stderr });
      } else {
        resolve({ stdout: stdout.trim(), stderr: stderr.trim() });
      }
    });
  });
}

async function getCalendar() {
  // Check if gcalcli is available
  const check = await run('which', ['gcalcli']);
  if (check.error || !check.stdout) {
    return { available: false, note: 'gcalcli not installed — skipping calendar' };
  }

  const now = new Date();
  const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
  const startStr = now.toISOString().split('T')[0];
  const endStr = tomorrow.toISOString().split('T')[0];

  const result = await run('gcalcli', [
    'agenda', startStr, endStr,
    '--nocolor',
    '--tsv',
  ]);

  if (result.error) {
    return { available: true, error: result.error };
  }

  const lines = result.stdout.split('\n').filter(l => l.trim());
  const events = lines.map(line => {
    const parts = line.split('\t');
    // TSV format: start_date start_time end_date end_time title location
    if (parts.length >= 5) {
      return {
        start_date: parts[0],
        start_time: parts[1],
        end_date: parts[2],
        end_time: parts[3],
        title: parts[4] || 'Untitled',
        location: parts[5] || '',
      };
    }
    return { raw: line };
  });

  return { available: true, events, count: events.length };
}

module.exports = { getCalendar };
