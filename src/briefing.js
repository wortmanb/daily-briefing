const { getWeather } = require('./sections/weather');
const { getCalendar } = require('./sections/calendar');
const { getGitStatus } = require('./sections/gitstatus');
const { getSystem } = require('./sections/system');
const { getKubernetes } = require('./sections/kubernetes');

const sectionRunners = {
  weather: getWeather,
  calendar: getCalendar,
  git: getGitStatus,
  system: getSystem,
  kubernetes: getKubernetes,
};

async function runBriefing(args) {
  const results = {};
  const promises = args.sections.map(async (section) => {
    const runner = sectionRunners[section];
    if (!runner) {
      results[section] = { error: `Unknown section: ${section}` };
      return;
    }
    try {
      results[section] = await runner(args);
    } catch (err) {
      results[section] = { error: err.message };
    }
  });

  await Promise.all(promises);
  return { sections: results, timestamp: new Date().toISOString() };
}

module.exports = { runBriefing };
