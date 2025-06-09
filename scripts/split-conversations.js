const fs = require('fs');
const path = require('path');

const inputFile = process.argv[3] || path.join('docs', 'sigils', 'conversations.json');
const outDir = path.join('docs', 'sigils', 'conversations-fragments');
const chunkSize = parseInt(process.argv[2], 10) || 100;

if (!fs.existsSync(inputFile)) {
  console.error(`Input file not found: ${inputFile}`);
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
if (!Array.isArray(data)) {
  console.error('Expected an array of conversations');
  process.exit(1);
}

if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

for (let i = 0; i < data.length; i += chunkSize) {
  const chunk = data.slice(i, i + chunkSize);
  const file = path.join(outDir, `fragment-${Math.floor(i / chunkSize) + 1}.json`);
  fs.writeFileSync(file, JSON.stringify(chunk, null, 2));
  console.log(`wrote ${file}`);
}
