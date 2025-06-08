import yaml
from pathlib import Path

matrix_path = Path('docs/CREPPhaseMatrix.yaml')
try:
    data = yaml.safe_load(matrix_path.read_text())
except FileNotFoundError:
    raise SystemExit('CREPPhaseMatrix.yaml not found')

for entry in data.get('phases', []):
    assert 'phase' in entry and 'crep_focus' in entry, 'missing keys in phase'
print('CREPPhaseMatrix validated.')
