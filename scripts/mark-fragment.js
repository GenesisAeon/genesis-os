const fs = require('fs');
const path = require('path');

const progressFile = path.join('docs', 'sigils', 'conversations-progress.json');
const fragment = process.argv[2];
if (!fragment) {
  console.error('Usage: node mark-fragment.js <fragment-file>');
  process.exit(1);
}

let progress = [];
if (fs.existsSync(progressFile)) {
  progress = JSON.parse(fs.readFileSync(progressFile, 'utf8'));
}

if (!progress.includes(fragment)) {
  progress.push(fragment);
  fs.writeFileSync(progressFile, JSON.stringify(progress, null, 2));
  console.log(`marked ${fragment}`);
} else {
  console.log(`${fragment} already marked`);
}
