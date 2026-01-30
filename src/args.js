const os = require('os');
const path = require('path');

function parseArgs(argv) {
  const args = {
    format: 'terminal',
    sections: ['weather', 'calendar', 'git', 'system', 'kubernetes'],
    location: process.env.BRIEFING_LOCATION || 'Austin, TX',
    gitDirs: (process.env.BRIEFING_GIT_DIRS || path.join(os.homedir(), 'git')).split(',').map(s => s.trim()),
    help: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') {
      args.help = true;
    } else if (arg === '--format' && argv[i + 1]) {
      args.format = argv[++i];
    } else if (arg === '--sections' && argv[i + 1]) {
      args.sections = argv[++i].split(',').map(s => s.trim());
    } else if (arg === '--location' && argv[i + 1]) {
      args.location = argv[++i];
    } else if (arg === '--git-dirs' && argv[i + 1]) {
      args.gitDirs = argv[++i].split(',').map(s => s.trim());
    }
  }

  return args;
}

module.exports = { parseArgs };
