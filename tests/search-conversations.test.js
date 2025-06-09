const { execSync } = require('child_process');

try {
  const output = execSync('node scripts/search-conversations.js Unified', { encoding: 'utf8' });
  console.log(output.trim());
  console.log('search script executed');
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
