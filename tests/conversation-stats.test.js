const { execSync } = require('child_process');

try {
  execSync('node scripts/generate-conversation-stats.js');
  const stats = require('../docs/sigils/conversations-stats.json');
  if (!stats.total_conversations || stats.total_conversations < 1) {
    throw new Error('stats not generated');
  }
  console.log('conversation stats generated');
} catch (err) {
  console.error(err);
  process.exit(1);
} finally {
  const fs = require('fs');
  const p = require('path').join(__dirname, '..', 'docs', 'sigils', 'conversations-stats.json');
  if (fs.existsSync(p)) fs.unlinkSync(p);
}
