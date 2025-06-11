const fs = require('fs');
const { execSync } = require('child_process');

try {
  execSync('node runDryAgent.ts', { stdio: 'inherit' });
  const log = fs.readFileSync('docs/agents_drycheck.md', 'utf8');
  if (!log.includes('Dry run completed')) {
    throw new Error('dry run log missing completion message');
  }
  console.log('dry agent test passed');
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
