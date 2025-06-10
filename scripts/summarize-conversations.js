const fs = require('fs');
const path = require('path');

const outFile = path.join('docs', 'sigils', 'conversations-summary.json');

const inputs = process.argv.slice(2);
if (!inputs.length) {
  const fragDir = path.join('docs', 'sigils', 'conversations-fragments');
  if (fs.existsSync(fragDir)) {
    inputs.push(
      ...fs
        .readdirSync(fragDir)
        .filter(f => f.endsWith('.json'))
        .map(f => path.join(fragDir, f))
    );
  } else {
    inputs.push(path.join('docs', 'sigils', 'conversations.json'));
  }
}

let summaries = [];
if (fs.existsSync(outFile)) {
  try {
    summaries = JSON.parse(fs.readFileSync(outFile, 'utf8'));
  } catch {
    summaries = [];
  }
}

for (const inputFile of inputs) {
  if (!fs.existsSync(inputFile)) {
    console.error(`Input file not found: ${inputFile}`);
    continue;
  }
  const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
  if (!Array.isArray(data)) {
    console.error(`Expected an array of conversations in ${inputFile}`);
    continue;
  }

  const part = data.map(conv => {
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
  let summary = '';
  if (firstMsg && typeof firstMsg === 'string') {
    summary = firstMsg.split(/\s+/).slice(0,10).join(' ');
  }
    return { title, summary };
  });
  summaries = summaries.concat(part);
}

fs.writeFileSync(outFile, JSON.stringify(summaries, null, 2));
console.log(`wrote ${outFile}`);
