const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const templatePath = path.join('repositorypflege', 'ReadMeVorlage.yaml');
const outPath = 'README.md';

if (!fs.existsSync(templatePath)) {
  console.error('template not found');
  process.exit(1);
}

const doc = yaml.load(fs.readFileSync(templatePath, 'utf8'));
let content = '';
for (const section of doc.sections || []) {
  if (section.example) {
    content += section.example.trim() + '\n\n';
  }
}
fs.writeFileSync(outPath, content.trim() + '\n');
console.log(`Generated ${outPath}`);
