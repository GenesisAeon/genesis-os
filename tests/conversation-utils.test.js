const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

const fragPath = path.join('docs', 'sigils', 'conversations-fragments', 'fragment-1.json');
const backup = fs.readFileSync(fragPath);

try {
  execSync(`node scripts/split-conversations.js 1 ${fragPath}`, { stdio: 'inherit' });
  execSync(`node scripts/filter-conversations.js Mandala ${fragPath}`, { stdio: 'inherit' });
  execSync(`node scripts/mark-fragment.js ${fragPath}`, { stdio: 'inherit' });
  if (!fs.existsSync(path.join('docs', 'sigils', 'conversations-filter-Mandala.json'))) {
    throw new Error('filter output missing');
  }
  console.log('Conversation util scripts executed successfully.');
} finally {
  fs.writeFileSync(fragPath, backup);
  if (fs.existsSync(path.join('docs', 'sigils', 'conversations-filter-Mandala.json'))) {
    fs.unlinkSync(path.join('docs', 'sigils', 'conversations-filter-Mandala.json'));
  }
}
