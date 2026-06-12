# Release Guide

This repository follows the **GenesisAeon ecosystem release process**, shared
across all 48 packages coordinated via [`genesis-os`](https://github.com/GenesisAeon/genesis-os)
(`release_map.yml`, `DEPENDENCY_REPORT.md`).

## Versioning

- We follow [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).
- The target version for the v1.0.0 ecosystem milestone is tracked in
  `release_map.yml` in `genesis-os` under this repo's entry
  (`target_version`, `current_version`).
- Pre-releases use suffixes: `-alpha.N`, `-beta.N`, `-rc.N`.

## Release types

| Tag pattern              | PyPI target        | Zenodo target     |
|---------------------------|---------------------|-------------------|
| `vX.Y.Z`                  | PyPI (production)   | Zenodo (production) |
| `vX.Y.Z-rc*`              | Test PyPI (canary)   | Zenodo Sandbox    |
| `vX.Y.Z-alpha*` / `-beta*`| Test PyPI (canary)   | Zenodo Sandbox    |

## Cutting a release

1. Ensure `pyproject.toml` `version` (or `setuptools_scm`/dynamic tag) matches
   the intended release version.
2. Update `CHANGELOG.md` with the new version section.
3. Ensure `zenodo.json` exists at the repo root with up-to-date metadata.
   If `concept_doi` is set, the new version archives under the same
   Zenodo concept; if null, a new concept deposition is created.
4. Push a tag matching `vX.Y.Z` (or `vX.Y.Z-rc1` for a canary):

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

5. The `.github/workflows/release.yml` workflow (see `genesis-os` template
   in `scripts/templates/publish.yml`) automatically:
   - builds wheel + sdist (`python -m build`)
   - runs the pytest matrix on Python 3.10 / 3.11 / 3.12
   - publishes to PyPI or Test PyPI depending on the tag
   - creates a GitHub Release with auto-generated notes and attaches `dist/*`
   - archives the release on Zenodo or Zenodo Sandbox

## Required secrets

Configure these as GitHub Environment secrets (`production` and `canary`):

- `PYPI_API_TOKEN` (production environment)
- `TEST_PYPI_API_TOKEN` (canary environment)
- `ZENODO_TOKEN` (production environment)
- `ZENODO_SANDBOX_TOKEN` (canary environment)

## Diamond-Interface contract

If this package implements the Diamond-Interface, it must define:

- `run_cycle`
- `get_crep_state`
- `get_utac_state`
- `get_phase_events`
- `to_zenodo_record`

Coverage across the ecosystem is tracked in `DEPENDENCY_REPORT.md` (genesis-os).
