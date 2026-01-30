const https = require('https');

function fetch(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'daily-briefing/1.0' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 400) {
          reject(new Error(`HTTP ${res.statusCode}: ${data.slice(0, 200)}`));
        } else {
          resolve(data);
        }
      });
    }).on('error', reject);
  });
}

async function getWeather(args) {
  const location = encodeURIComponent(args.location);
  const url = `https://wttr.in/${location}?format=j1`;
  const raw = await fetch(url);
  const data = JSON.parse(raw);

  const current = data.current_condition?.[0] || {};
  const today = data.weather?.[0] || {};
  const hourly = today.hourly || [];

  // Find afternoon temp (around 3pm)
  const afternoon = hourly.find(h => h.time === '1500') || hourly[hourly.length - 1] || {};

  return {
    location: args.location,
    condition: current.weatherDesc?.[0]?.value || 'Unknown',
    temp_f: current.temp_F || '?',
    temp_c: current.temp_C || '?',
    feels_like_f: current.FeelsLikeF || '?',
    humidity: current.humidity || '?',
    wind_mph: current.windspeedMiles || '?',
    wind_dir: current.winddir16Point || '',
    high_f: today.maxtempF || '?',
    low_f: today.mintempF || '?',
    high_c: today.maxtempC || '?',
    low_c: today.mintempC || '?',
    uv_index: current.uvIndex || '?',
    sunrise: today.astronomy?.[0]?.sunrise || '?',
    sunset: today.astronomy?.[0]?.sunset || '?',
    precip_chance: afternoon.chanceofrain || '0',
  };
}

module.exports = { getWeather };
