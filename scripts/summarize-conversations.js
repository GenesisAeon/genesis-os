const fs = require('fs');
const path = require('path');

const inputFile = process.argv[2] || path.join('docs', 'sigils', 'conversations.json');
const outFile = path.join('docs', 'sigils', 'conversations-summary.json');

if (!fs.existsSync(inputFile)) {
  console.error(`Input file not found: ${inputFile}`);
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
if (!Array.isArray(data)) {
  console.error('Expected an array of conversations');
  process.exit(1);
}

const summaries = data.map(conv => {
  const title = conv.title || 'Untitled';
  let firstMsg = '';
  if (conv.mapping) {
    const entries = Object.values(conv.mapping);
    for (const entry of entries) {
      if (entry && entry.message && entry.message.content && entry.message.content.parts) {
        firstMsg = entry.message.content.parts[0];
        if (firstMsg) break;
      }
    }
  }
  const summary = firstMsg ? firstMsg.split(/\s+/).slice(0,10).join(' ') : '';
  return { title, summary };
});

fs.writeFileSync(outFile, JSON.stringify(summaries, null, 2));
console.log(`wrote ${outFile}`);
