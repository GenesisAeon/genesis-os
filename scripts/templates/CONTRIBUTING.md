# Contributing

Thanks for your interest in contributing to this GenesisAeon package! This
repository is part of the [GenesisAeon ecosystem](https://github.com/GenesisAeon/genesis-os),
a coordinated set of 48 packages around the CREP/UTAC criticality framework.

## Getting started

```bash
git clone https://github.com/GenesisAeon/<this-repo>.git
cd <this-repo>
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Development workflow

1. Create a branch for your change: `git checkout -b feature/my-change`.
2. Make your change with tests.
3. Run the test suite:

   ```bash
   pytest -q
   ```

4. Run lint/type checks if configured (`ruff`, `mypy`).
5. Open a pull request describing the change and its motivation.

## Diamond-Interface contract

If your change touches the package's public runtime interface, make sure it
remains compatible with the Diamond-Interface methods used across the
ecosystem (`run_cycle`, `get_crep_state`, `get_utac_state`,
`get_phase_events`, `to_zenodo_record`). See `genesis-os/DEPENDENCY_REPORT.md`
for current coverage.

## Releases

See [`RELEASE_GUIDE.md`](./RELEASE_GUIDE.md) for the release process and tag
conventions.

## Code of Conduct

Be respectful and constructive. This project follows the GenesisAeon
[Code of Conduct](https://github.com/GenesisAeon/genesis-os/blob/main/CODE_OF_CONDUCT.md).
