const { execFile } = require('child_process');

function run(cmd, args, opts = {}) {
  return new Promise((resolve) => {
    execFile(cmd, args, { timeout: 15000, maxBuffer: 10 * 1024 * 1024, ...opts }, (err, stdout, stderr) => {
      if (err) resolve({ error: err.message, stdout: '', stderr });
      else resolve({ stdout: stdout.trim(), stderr: stderr.trim() });
    });
  });
}

async function getKubernetes() {
  // Check if kubectl is available
  const check = await run('which', ['kubectl']);
  if (check.error || !check.stdout) {
    return { available: false, note: 'kubectl not installed — skipping Kubernetes' };
  }

  const info = { available: true };

  // Get all pods as JSON
  const podsResult = await run('kubectl', ['get', 'pods', '--all-namespaces', '-o', 'json']);
  if (podsResult.error) {
    return { available: true, error: podsResult.error };
  }

  let pods;
  try {
    pods = JSON.parse(podsResult.stdout);
  } catch {
    return { available: true, error: 'Failed to parse kubectl output' };
  }

  const items = pods.items || [];
  info.totalPods = items.length;

  // Healthy states
  const healthyPhases = new Set(['Running', 'Succeeded', 'Completed']);
  const unhealthy = items.filter(p => {
    const phase = p.status?.phase || '';
    return !healthyPhases.has(phase);
  });

  info.unhealthyPods = unhealthy.map(p => ({
    name: p.metadata?.name,
    namespace: p.metadata?.namespace,
    phase: p.status?.phase,
  }));
  info.unhealthyCount = unhealthy.length;

  // Check for restart loops
  const restartIssues = [];
  for (const pod of items) {
    const containers = pod.status?.containerStatuses || [];
    for (const c of containers) {
      if (c.restartCount > 5) {
        restartIssues.push({
          pod: pod.metadata?.name,
          namespace: pod.metadata?.namespace,
          container: c.name,
          restarts: c.restartCount,
        });
      }
    }
  }
  info.restartIssues = restartIssues;
  info.restartIssueCount = restartIssues.length;

  // Node status
  const nodesResult = await run('kubectl', ['get', 'nodes', '-o', 'json']);
  if (!nodesResult.error) {
    try {
      const nodes = JSON.parse(nodesResult.stdout);
      info.nodes = (nodes.items || []).map(n => {
        const conditions = n.status?.conditions || [];
        const ready = conditions.find(c => c.type === 'Ready');
        return {
          name: n.metadata?.name,
          ready: ready?.status === 'True',
          roles: Object.keys(n.metadata?.labels || {})
            .filter(l => l.startsWith('node-role.kubernetes.io/'))
            .map(l => l.replace('node-role.kubernetes.io/', '')),
        };
      });
      info.nodeCount = info.nodes.length;
      info.nodesReady = info.nodes.filter(n => n.ready).length;
    } catch {
      // skip node info
    }
  }

  return info;
}

module.exports = { getKubernetes };
