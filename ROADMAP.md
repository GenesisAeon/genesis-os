# GenesisAeon v1.0.0 — Release Roadmap & Claude Code Prompts

This roadmap turns `DEPENDENCY_REPORT.md`, `METADATA_REPORT.md`, and
`DEPENDENCY_FIXES.md` into an ordered, step-by-step plan with ready-to-paste
prompts for **Claude Code** (one session per repo/step is recommended).

Each step lists:
- **Repo(s)** to open Claude Code in
- **Goal**
- **Prompt** — copy-paste into Claude Code in that repo

General notes:
- All prompts assume Claude Code has access to `GenesisAeon/<repo>` and
  (read-only) to `GenesisAeon/genesis-os` for the shared reports/templates.
- Steps are ordered by dependency: Phase 0 unblocks everything else; Phase 1
  standardizes tooling; Phase 2 cleans up metadata; Phases 3–8 release each
  cluster in dependency order; Phase 9 wraps up Zenodo + the 1.0.0 tag on
  `genesis-os`.
- After each release step, re-run
  `python scripts/analyze_deps.py --repos all --output DEPENDENCY_REPORT.md`
  in `genesis-os` to confirm conflicts are resolved before moving on.

---

## Phase 0 — Unblock the two stale dependencies

These two packages block 10 dependents each (see `DEPENDENCY_FIXES.md`).
Do these **first**.

### 0.1 — `entropy-table`

**Repo:** `GenesisAeon/entropy-table`

**Prompt:**
> This repo uses `setuptools_scm` for dynamic versioning (`dynamic = ["version"]`,
> `version_scheme = "guess-next-dev"`). The GenesisAeon ecosystem needs
> `entropy-table>=1.0.1` (10 dependent packages require this — see
> `genesis-os/DEPENDENCY_FIXES.md`). Please:
> 1. Add a static `authors` entry and a `license` field to `[project]` in
>    `pyproject.toml` (currently missing per `genesis-os/METADATA_REPORT.md`).
> 2. Add a `zenodo.json` at the repo root using
>    `genesis-os/scripts/templates/zenodo.json` as a starting point, filling
>    in `PACKAGE_NAME`, `PACKAGE_DESCRIPTION`, `PACKAGE_DOMAIN`,
>    `PACKAGE_GAMMA`, `PACKAGE_ID`, `PACKAGE_REPO=entropy-table`.
> 3. Add `RELEASE_GUIDE.md` / `CONTRIBUTING.md` / `.github/workflows/release.yml`
>    from `genesis-os/scripts/templates/` (publish.yml -> release.yml).
> 4. Bump to/tag `v1.0.1` (or `v1.0.0` if appropriate — check
>    `release_map.yml`'s `target_version`), commit, and push the tag so the
>    release workflow runs.

### 0.2 — `implosive-genesis`

**Repo:** `GenesisAeon/implosive-genesis`

**Prompt:**
> The GenesisAeon ecosystem needs `implosive-genesis>=0.4.0` (10 dependent
> packages require this — see `genesis-os/DEPENDENCY_FIXES.md`). Current
> `pyproject.toml` has `version = "0.3.1"`. Please:
> 1. Bump `version` to `"0.4.0"` (or `"1.0.0"` if appropriate per
>    `release_map.yml`'s `target_version`) in `pyproject.toml`.
> 2. Add `RELEASE_GUIDE.md` / `CONTRIBUTING.md` /
>    `.github/workflows/release.yml` from `genesis-os/scripts/templates/`.
> 3. Add `zenodo.json` from `genesis-os/scripts/templates/zenodo.json`
>    (fill placeholders, `PACKAGE_REPO=implosive-genesis`).
> 4. Update `CHANGELOG.md`, commit, tag `v0.4.0` (or `v1.0.0`), and push the
>    tag.

### 0.3 — Verify

**Repo:** `GenesisAeon/genesis-os`

**Prompt:**
> Re-run `python scripts/analyze_deps.py --repos all --output
> DEPENDENCY_REPORT.md --workdir /tmp/genesisaeon-clones` (delete
> `/tmp/genesisaeon-clones/entropy-table` and
> `/tmp/genesisaeon-clones/implosive-genesis` first so they're re-cloned at
> their new versions). Confirm section 3 ("Version Constraint Conflicts") is
> now empty. Update `release_map.yml` `current_version` for both packages to
> match their new released versions.

---

## Phase 1 — Roll out the release workflow + governance templates

Apply to **all 48 repos** (skip ones already covered: `genesis-os`,
`entropy-table`, `implosive-genesis` from Phase 0).

**Per-repo prompt** (run in each target repo, or use
`genesis-os/scripts/rollout_templates.sh` if you have a `GH_TOKEN` with
cross-repo access — it automates this entire phase):

> Adopt the GenesisAeon ecosystem release tooling from
> `GenesisAeon/genesis-os` (`scripts/templates/`):
> 1. Copy `scripts/templates/publish.yml` to
>    `.github/workflows/release.yml` (production vs. canary publish split
>    based on `vX.Y.Z` vs `vX.Y.Z-rc*/-alpha*/-beta*` tags).
> 2. Add `RELEASE_GUIDE.md` and `CONTRIBUTING.md` from
>    `scripts/templates/` if not already present (don't overwrite existing
>    docs).
> 3. Add `.github/ISSUE_TEMPLATE/bug_report.md`,
>    `.github/ISSUE_TEMPLATE/feature_request.md`, and
>    `.github/PULL_REQUEST_TEMPLATE.md` from `scripts/templates/`.
> 4. If `CHANGELOG.md` doesn't exist, add it from
>    `scripts/templates/CHANGELOG_STUB.md`.
> 5. If `zenodo.json` doesn't exist, add it from
>    `scripts/templates/zenodo.json`, replacing `PACKAGE_REPO` with this
>    repo's name (leave other placeholders for Phase 2).
> Commit as `chore: adopt GenesisAeon ecosystem release workflow and
> governance templates` on a new branch and open a PR.

**Automation shortcut (recommended):** in `genesis-os`, run:
```bash
export GH_TOKEN=<token with push access to all GenesisAeon repos>
./scripts/rollout_templates.sh
```
This does Phase 1 for all 47 non-`genesis-os` repos in one go.

---

## Phase 2 — Metadata cleanup (per `METADATA_REPORT.md`)

Two repos need urgent attention (errors), the rest have warnings (mostly
missing `zenodo.json`, which Phase 1 now adds with placeholders).

### 2.1 — `unified-mandala-Demo` (missing `pyproject.toml` entirely)

**Repo:** `GenesisAeon/unified-mandala-Demo`

**Prompt:**
> This repo has no `pyproject.toml` (per `genesis-os/METADATA_REPORT.md`).
> Inspect the existing source layout and create a `pyproject.toml` following
> the pattern used in `GenesisAeon/unified-mandala` (same ecosystem,
> `import_name: unified_mandala_demo`, `pypi_name: unified-mandala-demo`,
> `target_version: 1.0.0` per `genesis-os/release_map.yml`). Include
> `[build-system]`, `[project]` with `name`, `version`, `description`,
> `authors`, `license`, `requires-python`, and `dependencies` matching
> actual imports in the source. Then complete Phase 1 (release workflow +
> templates) for this repo too.

### 2.2 — Fill in `zenodo.json` placeholders (all 48 repos)

For each repo, after Phase 1 added a templated `zenodo.json`:

**Prompt (per repo):**
> Fill in the placeholders in `zenodo.json` (added via the GenesisAeon
> template): `PACKAGE_NAME`, `PACKAGE_DESCRIPTION`, `PACKAGE_DOMAIN`,
> `PACKAGE_GAMMA` (CREP Γ value if known/applicable, otherwise remove that
> sentence), `PACKAGE_ID` (this repo's short code in the ecosystem, e.g.
> P17–P40 per other zenodo.json files), based on this repo's
> `pyproject.toml` description and `genesis-os/release_map.yml` entry/notes.
> Also add a short "Citation" section with the Zenodo badge to `README.md`
> if missing (flagged as "No DOI reference" in `genesis-os/METADATA_REPORT.md`).

### 2.3 — General warnings (lowercase names, missing license/authors/requires-python)

**Prompt (per repo flagged in `METADATA_REPORT.md`):**
> Per `genesis-os/METADATA_REPORT.md`, fix the listed `pyproject.toml`
> warnings for this repo: ensure `[project].name` is lowercase, `version`
> follows SemVer, and `authors`, `license`, `requires-python` are all
> present and correct (license should match `genesis-os` — GPL-3.0-or-later
> unless this repo specifies otherwise). Also ensure `README.md` has a `#`
> title, an "Installation" section with `pip install <name>`, and a
> "Usage"/"Quick Start" section.

---

## Phase 3 — Release CORE INFRASTRUCTURE (3 repos)

Release order matters: `diamond-setup` first (it's the scaffold template),
then `genesis-scope`, then `genesis-os` last (depends on most packages).

**Repos:** `diamond-setup`, `genesis-scope` (then `genesis-os` in Phase 9)

**Prompt (per repo):**
> This repo is ready for its `v1.0.0` release per
> `genesis-os/release_map.yml` (`target_version: "1.0.0"`,
> `current_version: "1.0.0"`). Verify `pyproject.toml` version is `1.0.0`,
> `CHANGELOG.md` has a `[1.0.0]` section, `zenodo.json` is filled in (Phase
> 2), and `.github/workflows/release.yml` is the GenesisAeon template
> (Phase 1). Then tag and push `v1.0.0`.

---

## Phase 4 — Release UTAC CLUSTER (12 repos)

**Repos (in this order due to `utac-core` being the base engine):**
`utac-core`, then: `sandpile-utac`, `seismic-utac`, `neural-avalanche-utac`,
`amoc-utac`, `amazon-utac`, `solar-flare-utac`, `cygnus-jet-utac`,
`eml-utac-bridge`, `beta-clustering-utac`, `implosive-origin-utac`,
`afet-tensions`.

**Prompt for `utac-core` (do first):**
> Per `genesis-os/release_map.yml`, `utac-core` is the base UTAC engine
> (`current_version: 0.1.0` -> `target_version: 1.0.0`). It also requires
> `entropy-table>=1.0.1` and `implosive-genesis>=0.4.0` (resolved in Phase
> 0). Bump `pyproject.toml` version to `1.0.0`, update dependency pins to
> the released versions from Phase 0, complete Phases 1–2 if not already
> done, then tag and push `v1.0.0`.

**Prompt for each remaining UTAC-cluster repo:**
> Per `genesis-os/release_map.yml`, this repo targets `v1.0.0` and depends
> on `utac-core` (now released at `1.0.0`, see Phase 4). Update the
> `utac-core` dependency pin in `pyproject.toml` to `>=1.0.0`, bump this
> repo's own version to `1.0.0`, complete Phases 1–2 if not already done,
> then tag and push `v1.0.0`.

---

## Phase 5 — Release COSMOLOGY & SPACE-TIME cluster (10 repos)

**Repos:** `implosive-genesis` (done in Phase 0), `fieldtheory`,
`Feldtheorie`, `cellular-genesis`, `universums-sim`, `cosmic-web`,
`cosmic-moment`, `quantum-genesis`, `vrig-cosmological`, `sa-sv-duality`.

**Prompt (per repo):**
> Per `genesis-os/release_map.yml`, this repo targets `v1.0.0`. Check its
> dependencies against repos already released in Phases 0/3/4 (especially
> `implosive-genesis`, `entropy-table`, `utac-core` if used) and update pins
> to the released versions. Complete Phases 1–2 if not already done, bump
> `pyproject.toml` to `1.0.0`, then tag and push `v1.0.0`.
>
> Note: `fieldtheory` and `Feldtheorie` look like duplicate/twin repos
> (German/English names) — before releasing, confirm with the maintainer
> whether both should be released independently or one should redirect to
> the other (flag this rather than guessing).

---

## Phase 6 — Release GOVERNANCE & ETHICS cluster (3 repos)

**Repos:** `entropy-governance`, `gemeinwohl`, `worldview`.

**Prompt (per repo):**
> Per `genesis-os/release_map.yml`, this repo targets `v1.0.0`.
> `entropy-governance` depends on `implosive-genesis>=0.4.0` (released in
> Phase 0) — update that pin. Complete Phases 1–2 if not already done, bump
> `pyproject.toml` to `1.0.0`, then tag and push `v1.0.0`.

---

## Phase 7 — Release COGNITIVE & AI cluster (6 repos)

**Repos:** `aeon-ai`, `AdvancedWeightingSystems`, `genesis-q4-core`,
`HexaAgent`, `spiking-aeon`, `phaethon-chimera`.

**Prompt (per repo):**
> Per `genesis-os/release_map.yml`, this repo targets `v1.0.0`. Check
> dependencies against UTAC-cluster packages released in Phase 4 (several
> of these implement the Diamond-Interface per
> `genesis-os/DEPENDENCY_REPORT.md` section 2 — verify `run_cycle`,
> `get_crep_state`, `get_utac_state`, `get_phase_events`, `to_zenodo_record`
> are still implemented and tested). Complete Phases 1–2 if not already
> done, bump `pyproject.toml` to `1.0.0`, then tag and push `v1.0.0`.

---

## Phase 8 — Release OBSERVABILITY & AESTHETICS + ROUTING & UTILITIES (14 repos)

**Repos:** `unified-mandala`, `unified-mandala-Demo` (Phase 2.1 first),
`mandala-visualize`, `sonification`, `theta-resonance`, `medium-modulation`,
`climate-dashboard`, `entropy-table` (done in Phase 0),
`phi-scaling-validator`, `diffusive-routing`, `mirror-machine`, `sigillin`,
`epi-sigillin`, `hikari-ledger`.

**Prompt (per repo):**
> Per `genesis-os/release_map.yml`, this repo targets `v1.0.0`. Several of
> these depend on `entropy-table>=1.0.1` and `implosive-genesis>=0.4.0`
> (Phase 0) — update those pins to the released versions. Complete Phases
> 1–2 if not already done, bump `pyproject.toml` to `1.0.0`, then tag and
> push `v1.0.0`.

---

## Phase 9 — `genesis-os` v1.0.0 + ecosystem wrap-up

**Repo:** `GenesisAeon/genesis-os`

**Prompt:**
> All 47 ecosystem packages should now be released at `1.0.0` (Phases 0–8).
> 1. Update `pyproject.toml`'s `full-stack`/optional dependency groups to
>    pin all GenesisAeon packages to `>=1.0.0`.
> 2. Re-run `python scripts/analyze_deps.py --repos all --output
>    DEPENDENCY_REPORT.md` and `python scripts/normalize_metadata.py --repos
>    all --dry-run --output METADATA_REPORT.md` (full 48) to confirm a clean
>    bill of health (no conflicts, no errors).
> 3. Update `CHANGELOG.md` with the `v1.0.0` ecosystem milestone summary.
> 4. Tag and push `v1.0.0` — this triggers the production release workflow
>    (PyPI + Zenodo).
> 5. Optionally, set up a Zenodo Community named `genesisaeon`
>    (`zenodo_community` field in `release_map.yml`) and link each repo's
>    Zenodo deposition to it once concept DOIs exist.

---

## Quick reference: dependency order

```
Phase 0: entropy-table, implosive-genesis        (unblock everything)
Phase 1: (cross-cutting) templates -> all 47 repos
Phase 2: (cross-cutting) metadata fixes -> all 48 repos
Phase 3: diamond-setup, genesis-scope
Phase 4: utac-core -> {sandpile, seismic, neural-avalanche, amoc, amazon,
                        solar-flare, cygnus-jet, eml-bridge,
                        beta-clustering, implosive-origin, afet-tensions}-utac
Phase 5: fieldtheory/Feldtheorie, cellular-genesis, universums-sim,
         cosmic-web, cosmic-moment, quantum-genesis, vrig-cosmological,
         sa-sv-duality
Phase 6: entropy-governance, gemeinwohl, worldview
Phase 7: aeon-ai, AdvancedWeightingSystems, genesis-q4-core, HexaAgent,
         spiking-aeon, phaethon-chimera
Phase 8: unified-mandala(+Demo), mandala-visualize, sonification,
         theta-resonance, medium-modulation, climate-dashboard,
         phi-scaling-validator, diffusive-routing, mirror-machine,
         sigillin, epi-sigillin, hikari-ledger
Phase 9: genesis-os v1.0.0 (final)
```
