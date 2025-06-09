const fs = require('fs');
const path = require('path');

const keyword = process.argv[2];
if (!keyword) {
  console.error('Usage: node search-conversations.js <keyword>');
  process.exit(1);
}

const summaryPath = path.join(__dirname, '..', 'docs', 'sigils', 'conversations-summary.json');
let data;
try {
  const content = fs.readFileSync(summaryPath, 'utf8');
  data = JSON.parse(content);
} catch (err) {
  console.error('Failed to read conversations-summary.json');
  process.exit(1);
}

const lower = keyword.toLowerCase();
const results = data.filter(item =>
  item.title.toLowerCase().includes(lower) ||
  (item.summary && item.summary.toLowerCase().includes(lower))
);

if (!results.length) {
  console.log('No matches found');
  process.exit(0);
}
results.forEach(r => {
  console.log(`- ${r.title}: ${r.summary}`);
});
