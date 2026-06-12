# 🚀 Claude Code Execution Prompt: GenesisAeon Release Orchestration v1.0.0

**Status:** Ready for Claude Code Execution  
**Target:** Genesis-OS Repo (primary coordination hub)  
**Scope:** Full orchestration of 48 packages to v1.0.0 release-ready state  
**Duration:** 72 hours (Phase 1 output generation)  

---

## 📋 Executive Summary for Claude

You are tasked with orchestrating a **multi-repository, coordinated software release** across the **GenesisAeon ecosystem (48 public GitHub repositories)**. This is not a simple version bump—it is a **systemic architectural alignment** to ensure:

1. **Structural Homogeneity:** All repos use identical scaffolding, CI/CD templates, and metadata standards
2. **Emergent Coupling Validation:** The Diamond-Interface contract is uniformly enforced
3. **Academic Citability:** Every package receives a DOI via Zenodo integration
4. **Reproducibility:** Deterministic build pipelines, pinned dependencies, and locked versions

**Your role:** Generate **4 production-ready artifacts** in the `genesis-os` repository under branch `release-orchestration`, then coordinate the analysis and dry-run reports.

---

## 🎯 Phase 1: Artifact Generation (Hours 0–24)

### Task 1.1: Create Canonical `release.yml` Workflow

**Location:** `.github/workflows/release.yml`

**Requirements:**
- Trigger on git tags matching `v*.*.*`
- **Build Stage:** Create wheel + source distribution using `python -m build`
- **Test Stage:** Run pytest matrix across Python 3.10, 3.11, 3.12
- **Publish Stage (Conditional):**
  - **Production:** Tag `vX.Y.Z` (no rc/alpha/beta) → PyPI production + Zenodo production
  - **Canary:** Tag `vX.Y.Z-rc*` or `vX.Y.Z-alpha*` → Test PyPI only + Zenodo sandbox
- **Guardrails:**
  - All publish jobs depend on successful build + test
  - Use GitHub environment secrets: `PYPI_API_TOKEN`, `ZENODO_TOKEN`
  - Zenodo upload reads `concept_doi` from `zenodo.json` in repo root
- **Artifact Management:**
  - Upload build artifacts with 1-day retention
  - Create GitHub Release with generate_release_notes
  - Attach dist/* files to release

**File:** `release.yml` (should contain ~250 lines of YAML with extensive comments)

---

### Task 1.2: Create Dependency Analysis Script

**Location:** `scripts/analyze_deps.py`

**Requirements:**
- **Input:** List of 48 GenesisAeon repos (names provided below)
- **Output:** `DEPENDENCY_REPORT.md` with:
  - Circular dependency detection (DFS algorithm)
  - Diamond-Interface method coverage per repo (check: `run_cycle`, `get_crep_state`, `get_utac_state`, `get_phase_events`, `to_zenodo_record`)
  - Version constraint conflicts
  - Unresolved dependencies (external to GenesisAeon)
- **Functionality:**
  - Clone/update each repo locally with `git clone --depth=1`
  - Parse `pyproject.toml` for dependencies and metadata
  - Grep source code for Diamond-Interface method definitions
  - Output structured Markdown report
- **Invocation:** `python scripts/analyze_deps.py --repos all --output DEPENDENCY_REPORT.md`

**Repo List (48 total):**
```
AdvancedWeightingSystems, aeon-ai, afet-tensions, amazon-utac, amoc-utac,
beta-clustering-utac, cellular-genesis, climate-dashboard, cosmic-moment,
cosmic-web, cygnus-jet-utac, diamond-setup, diffusive-routing, eml-utac-bridge,
entropy-governance, entropy-table, epi-sigillin, Feldtheorie, fieldtheory,
gemeinwohl, genesis-os, genesis-q4-core, genesis-scope, HexaAgent, hikari-ledger,
implosive-genesis, implosive-origin-utac, mandala-visualize, medium-modulation,
mirror-machine, neural-avalanche-utac, phaethon-chimera, phi-scaling-validator,
quantum-genesis, sa-sv-duality, sandpile-utac, seismic-utac, sigillin,
solar-flare-utac, sonification, spiking-aeon, theta-resonance, unified-mandala,
unified-mandala-Demo, universums-sim, utac-core, vrig-cosmological, worldview
```

---

### Task 1.3: Create Release Mapping Document

**Location:** `release_map.yml`

**Requirements:**
- **Schema:** YAML file mapping each repo to:
  ```yaml
  <repo-name>:
    pypi_name: <normalized PyPI name>
    import_name: <Python import path>
    target_version: "1.0.0" (or current if higher)
    current_version: <from pyproject.toml>
    zenodo_concept_doi: <DOI or null>
    zenodo_community: "genesisaeon"
    owner: "GenesisAeon"
    notes: <release strategy notes>
  ```
- **Clusters:** Group repos by function (UTAC, Cosmology, Governance, AI, Observability, Utilities)
- **Phase Planning:** Define 6 release phases with dependencies

---

### Task 1.4: Create Metadata Normalization Script

**Location:** `scripts/normalize_metadata.py`

**Requirements:**
- **Validation Targets:**
  1. `pyproject.toml`: name, version, authors, license, requires-python
  2. `zenodo.json`: title, creators, license
  3. `README.md`: Title, Description, Installation, Usage
- **Dry-Run Mode (Default):**
  - Parse all metadata files
  - Generate list of issues + suggested fixes
  - Output human-readable summary + Markdown report
  - Do NOT create PRs or commit changes
- **Output:**
  - Console: Colored summary (✅ OK, ⚠️ Warning, ❌ Error)
  - File: `METADATA_REPORT.md` with detailed fixes per repo
- **Invocation:** `python scripts/normalize_metadata.py --repos all --dry-run`

---

## 🔧 Phase 2: Execution Steps

### Step 2.1: Verify Branch

```bash
cd genesis-os
git checkout release-orchestration
```

### Step 2.2: Create Artifacts (Claude generates these files per Task 1.1–1.4)

Then run the analysis scripts:

### Step 2.3: Run Dependency Analysis

```bash
python scripts/analyze_deps.py --repos all --output DEPENDENCY_REPORT.md
```

### Step 2.4: Run Metadata Normalization (Pilot 5 Repos)

```bash
python scripts/normalize_metadata.py \
  --repos diamond-setup,genesis-os,unified-mandala,worldview,gemeinwohl \
  --dry-run
```

### Step 2.5: Commit Artifacts to Branch

```bash
git add \
  .github/workflows/release.yml \
  scripts/analyze_deps.py \
  scripts/normalize_metadata.py \
  release_map.yml \
  DEPENDENCY_REPORT.md \
  METADATA_REPORT.md

git commit -m "chore(release): orchestration scripts, mapping, and dependency reports"
git push origin release-orchestration
```

---

## 📊 Phase 3: Output & Review Artifacts

All artifacts should be committed to `GenesisAeon/genesis-os` on branch `release-orchestration`.

---

## ✅ Success Criteria

Phase 1 is **complete and successful** when:

1. ✅ All 4 scripts are committed to `release-orchestration` branch
2. ✅ `DEPENDENCY_REPORT.md` is generated with all 48 repos analyzed
3. ✅ `METADATA_REPORT.md` is generated for pilot 5 repos
4. ✅ All scripts run without errors
5. ✅ Reports are human-readable and actionable
6. ✅ No external repos modified (dry-run mode)

---

**Ready for Claude Code Execution.**