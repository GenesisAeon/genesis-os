const fs = require('fs');
const { execSync } = require('child_process');

const backup = fs.readFileSync('README.md');
try {
  execSync('npm run docs:build', { stdio: 'inherit' });
  const content = fs.readFileSync('README.md', 'utf8');
  if (!content.includes('Unified Mandala Logo')) {
    throw new Error('README generation failed');
  }
  console.log('readme generated');
} catch (err) {
  console.error(err);
  process.exit(1);
} finally {
  fs.writeFileSync('README.md', backup);
}

