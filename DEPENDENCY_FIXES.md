# GenesisAeon Ecosystem — Dependency Fix Proposals

This document turns the 21 version-constraint conflicts from
`DEPENDENCY_REPORT.md` (section 3) into concrete, reviewable fix proposals.
**Nothing here has been applied automatically** — these are suggestions for
the maintainers of the listed repos (or for Copilot batch-PRs once available).

## Root cause

Two ecosystem packages are required at higher versions than the
`current_version` recorded in `release_map.yml` — but the actual
*released* version of both is already **`0.3.1`**, not `0.1.0`. The
`release_map.yml` entries are stale placeholders left over from initial
scaffolding.

| Package | `release_map.yml` `current_version` | Actual version (repo) | Required by consumers |
|---|---|---|---|
| `entropy-table` | `0.1.0` | `0.3.1` (git tag `v0.3.1`, version is dynamic via `setuptools_scm`) | `>=1.0.1` |
| `implosive-genesis` | `0.1.0` | `0.3.1` (`pyproject.toml` `version = "0.3.1"`) | `>=0.4.0` |

So the real gap is smaller than it looks (`0.3.1` → required version), but
**both packages still need a version bump before their 10 dependents can be
released at `1.0.0`**.

## Fix 1 — Update `release_map.yml` (genesis-os, low risk)

Correct the stale `current_version` fields to reflect reality. This does not
change any package, just the bookkeeping:

```yaml
entropy-table:
  current_version: "0.3.1"   # was "0.1.0" — actual tag is v0.3.1 (setuptools_scm dynamic)
  notes: "Contract-first relational entropy atlas engine. Needs release >=1.0.1 before 10 dependents can target 1.0.0."

implosive-genesis:
  current_version: "0.3.1"   # was "0.1.0"
  notes: "Needs release >=0.4.0 before 10 dependents can target 1.0.0."
```

## Fix 2 — Release `entropy-table` at `>=1.0.1`

`entropy-table`'s `pyproject.toml` uses `dynamic = ["version"]` with
`setuptools_scm` (`version_scheme = "guess-next-dev"`), so the version is
derived from git tags. To satisfy the 10 dependents requiring
`entropy-table>=1.0.1`:

1. Tag the repo `v1.0.1` (or `v1.0.0` if the ecosystem-wide 1.0.0 milestone
   applies here too — check with `release_map.yml`'s `target_version: "1.0.0"`).
2. Confirm `pyproject.toml` also gains a static `version`/`authors`/`license`
   per `METADATA_REPORT.md` (currently `version` and `authors` are flagged
   missing/dynamic).

Affected consumers (10): `climate-dashboard`, `cosmic-moment`, `cosmic-web`,
`fieldtheory`, `mandala-visualize`, `medium-modulation`, `mirror-machine`,
`sigillin`, `sonification`, `utac-core`.

## Fix 3 — Release `implosive-genesis` at `>=0.4.0`

`implosive-genesis` is statically versioned at `0.3.1` in `pyproject.toml`.
To satisfy the 10 dependents requiring `implosive-genesis>=0.4.0`:

1. Bump `version = "0.3.1"` → `version = "0.4.0"` (or directly to `1.0.0`
   per the ecosystem milestone) in `pyproject.toml`.
2. Tag and release `v0.4.0` (or `v1.0.0`).

Affected consumers (10): `climate-dashboard`, `cosmic-moment`, `cosmic-web`,
`entropy-governance`, `fieldtheory`, `mandala-visualize`, `medium-modulation`,
`mirror-machine`, `sigillin`, `sonification`.

## Suggested release order (Phase 0, before the 6 phases in `release_map.yml`)

Both `entropy-table` and `implosive-genesis` should release **first**, ahead
of any of their 10 dependents, since every dependent's CI will fail to
resolve dependencies otherwise:

1. `entropy-table` → tag `v1.0.1`+ (or `v1.0.0` if target version applies)
2. `implosive-genesis` → bump to `0.4.0`/`1.0.0`, tag and release
3. Re-run `scripts/analyze_deps.py --repos all` to confirm conflicts = 0
4. Proceed with the 6 phases already defined in `release_map.yml`

## Not addressed here

- The 21 conflicts above are the *only* version conflicts detected; no
  circular dependencies were found (`DEPENDENCY_REPORT.md` section 1).
- External (non-GenesisAeon) dependency version ranges were not audited —
  out of scope for this pass.
