const fs = require('fs');
const path = require('path');

const keyword = process.argv[2];
const inputFile = process.argv[3] || path.join('docs', 'sigils', 'conversations.json');
if (!keyword) {
  console.error('Usage: node filter-conversations.js <keyword> [file]');
  process.exit(1);
}

if (!fs.existsSync(inputFile)) {
  console.error(`Input file not found: ${inputFile}`);
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
const filtered = data.filter(item => JSON.stringify(item).toLowerCase().includes(keyword.toLowerCase()));

const outPath = path.join('docs', 'sigils', `conversations-filter-${keyword}.json`);
fs.writeFileSync(outPath, JSON.stringify(filtered, null, 2));
console.log(`wrote ${outPath}`);
