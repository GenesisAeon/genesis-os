const { execSync } = require('child_process');

try {
  const output = execSync('python3 scripts/validate_crep_phase_matrix.py');
  if (!output.toString().includes('CREPPhaseMatrix validated.')) {
    throw new Error('Validation output missing');
  }
  console.log('CREP phase matrix validated.');
} catch (err) {
  console.error(err);
  process.exit(1);
}
