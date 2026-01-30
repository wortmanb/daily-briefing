const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

function run(cmd, args, opts = {}) {
  return new Promise((resolve) => {
    execFile(cmd, args, { timeout: 10000, ...opts }, (err, stdout, stderr) => {
      if (err) resolve({ error: err.message, stdout: '', stderr });
      else resolve({ stdout: stdout.trim(), stderr: stderr.trim() });
    });
  });
}

async function scanRepo(repoPath) {
  const name = path.basename(repoPath);
  const cwd = repoPath;

  // Check if it's a git repo
  const gitDir = path.join(repoPath, '.git');
  try {
    fs.accessSync(gitDir);
  } catch {
    return null; // Not a git repo
  }

  const info = { name, path: repoPath };

  // Uncommitted changes
  const status = await run('git', ['status', '--porcelain'], { cwd });
  if (!status.error && status.stdout) {
    const changes = status.stdout.split('\n').filter(l => l.trim());
    info.uncommitted = changes.length;
  } else {
    info.uncommitted = 0;
  }

  // Current branch
  const branch = await run('git', ['branch', '--show-current'], { cwd });
  info.branch = branch.error ? 'unknown' : (branch.stdout || 'detached');

  // Ahead/behind
  const ab = await run('git', ['rev-list', '--left-right', '--count', `HEAD...@{upstream}`], { cwd });
  if (!ab.error && ab.stdout) {
    const parts = ab.stdout.split(/\s+/);
    info.ahead = parseInt(parts[0]) || 0;
    info.behind = parseInt(parts[1]) || 0;
  }

  // Recent commits (last 24h)
  const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  const log = await run('git', ['log', `--since=${since}`, '--oneline', '--no-merges'], { cwd });
  if (!log.error && log.stdout) {
    info.recentCommits = log.stdout.split('\n').filter(l => l.trim()).length;
  } else {
    info.recentCommits = 0;
  }

  return info;
}

async function getGitStatus(args) {
  const repos = [];
  const errors = [];

  for (const dir of args.gitDirs) {
    const expandedDir = dir.replace(/^~/, require('os').homedir());
    try {
      const entries = fs.readdirSync(expandedDir, { withFileTypes: true });
      const subdirs = entries
        .filter(e => e.isDirectory() && !e.name.startsWith('.'))
        .map(e => path.join(expandedDir, e.name));

      const results = await Promise.all(subdirs.map(scanRepo));
      repos.push(...results.filter(Boolean));
    } catch (err) {
      errors.push(`${dir}: ${err.message}`);
    }
  }

  // Sort: repos with changes first, then by name
  repos.sort((a, b) => {
    const aActive = (a.uncommitted > 0 || a.ahead > 0) ? 1 : 0;
    const bActive = (b.uncommitted > 0 || b.ahead > 0) ? 1 : 0;
    if (bActive !== aActive) return bActive - aActive;
    return a.name.localeCompare(b.name);
  });

  const dirty = repos.filter(r => r.uncommitted > 0);
  const withRecent = repos.filter(r => r.recentCommits > 0);

  return {
    totalRepos: repos.length,
    dirtyRepos: dirty.length,
    reposWithRecentCommits: withRecent.length,
    repos,
    errors: errors.length ? errors : undefined,
  };
}

module.exports = { getGitStatus };
