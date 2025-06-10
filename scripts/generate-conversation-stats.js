const fs = require('fs');
const path = require('path');

const summaryPath = path.join('docs', 'sigils', 'conversations-summary.json');
const kontextPath = 'kontext.json';
const statsPath = path.join('docs', 'sigils', 'conversations-stats.json');

if (!fs.existsSync(summaryPath)) {
  console.error(`Summary file not found: ${summaryPath}`);
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
const total = Array.isArray(data) ? data.length : 0;

const stats = { total_conversations: total };
fs.writeFileSync(statsPath, JSON.stringify(stats, null, 2));

if (fs.existsSync(kontextPath)) {
  const kData = JSON.parse(fs.readFileSync(kontextPath, 'utf8'));
  kData.total_conversations = total;
  fs.writeFileSync(kontextPath, JSON.stringify(kData, null, 2));
}

console.log(`wrote ${statsPath} and updated kontext.json`);
