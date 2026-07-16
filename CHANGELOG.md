# Changelog

All notable changes to **genesis-os** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.0.7] — 2026-07-16

### Fixed
- `scope-resilience>=1.0.0` (P41, `full` extra) now actually resolves —
  the package didn't exist on PyPI until this same day, so
  `pip install "genesis-os[full]"` was previously uninstallable. No pin
  change needed, just a real target to install now.

### Removed
- Pruned `gemeinwohl`, `worldview`, `universums-sim` from the `full`
  extra. All three declare `genesis-os` as their own dependency, so
  `genesis-os[full]` was pulling itself back in transitively
  (`genesis-os` ↔ `gemeinwohl`/`worldview`/`universums-sim`). Not a
  build-time cycle, but an architecture smell worth removing. Their
  `genesis_os.plugins.adapters.*` modules already guard the import with
  `try/except ImportError` and degrade to `{"<pkg>_available": False}`,
  so this is a non-breaking change for anyone not already relying on
  `full` to auto-install these three — install them alongside
  `genesis-os` explicitly if you want those adapters active.

---

## [1.0.6] — 2026-07-02

### Fixed
- Full-stack dependency pin: `cosmic-web>=1.0.1` — prevents `genesis_os` namespace
  collision that broke `from genesis_os import GenesisOS` after
  `pip install "genesis-os[full-stack]"` (fixed upstream in cosmic-web 1.0.1).

---

## [1.0.5] — 2026-07-01

### Fixed
- Zenodo version sync: `parse_release_tag()` — never use `lstrip('v1.')` on tags
  (`v1.0.2` → `0.2` bug that produced `0.2.0`-style Zenodo versions).
- `scripts/sync_zenodo_version.py` syncs `.zenodo.json` from `pyproject.toml` or `--tag`.
- `bump_versions` now updates `.zenodo.json` and requires an explicit version argument.
- `release.yml`: sync Zenodo metadata before archive; read `.zenodo.json` (not only `zenodo.json`).
- `__version__` in `genesis_os` aligned with package metadata.

---

## [1.0.4] — 2026-07-01

### Added
- `contracts/diamond.interface.yaml` — machine-readable Diamond spec (synced with diamond-setup).
- `scripts/validate_diamond_ci.py` + `tests/contract/test_diamond_utac_batch.py`.
- CI job `diamond-contract`: validates amoc / beta-clustering / implosive-origin / phi-scaling UTACs.
- Optional extra `[diamond-contract]` for local ecosystem validation.

### Changed
- `unified-mandala-demo` floor pin `>=1.0.1` (importable Python shim; fixes empty wheel).

---

## [1.0.3] — 2026-07-01

### Fixed
- `AgentMemory.record`: `sequence` in Sigillin content — FIFO eviction with distinct
  snapshots in tight loops (`test_max_depth_fifo`).
- `test_use_plugin_true_without_package_sets_plugin_none`: mock `mandala_visualizer`
  when package is installed locally.

### Changed
- `release.yml` tag trigger: `v*` (fixes workflow showing 0 jobs on `v*.*.*`).

---

## [1.0.2] — 2026-07-01

### Changed
- `diamond-setup` pinned to `>=2.1.0` (DiamondPackage ABC, `NotConvergedError`,
  `validate_diamond_instance`; published from diamond-setup v2.1.0).

---

## [1.0.1] — 2026

### Changed
- Dependency floor pins synchronised to match actual released versions
  across all 48 GenesisAeon ecosystem packages:
  - `entropy-table` pinned to `>=2.0.1` (latest on PyPI; supersedes `>=2.0.0`)
  - `diamond-setup` pinned to `>=1.0.0` (latest on PyPI)
  - `hexaagent` renamed to `genesisaeon-hexaagent>=1.0.0` (actual PyPI name)
  - `sonification` renamed to `genesisaeon-sonification>=1.0.0` (actual PyPI name)
  - All other ecosystem packages pinned to `>=1.0.0`
- `mandala-visualizer>=1.0.0` (correct PyPI name; import `mandala_visualizer`)
- Added the remaining GenesisAeon ecosystem packages as optional `full-stack`
  dependencies (previously undeclared), each pinned `>=1.0.0` unless noted:
  `diamond-setup>=2.0.0`, `feldtheorie>=6.0.0` (PyPI version, distinct from GitHub
  tag v13.0.0), `genesisaeon-hexaagent`, `genesis-scope`, `genesis-q4-core`,
  `epi-sigillin`, `unified-mandala`, `unified-mandala-demo`, `sandpile-utac`,
  `seismic-utac`, `neural-avalanche-utac`, `amoc-utac`, `amazon-utac`,
  `solar-flare-utac`, `cygnus-jet-utac`, `eml-utac-bridge`, `beta-clustering-utac`,
  `implosive-origin-utac`, `afet-tensions`, `universums-sim`, `cosmic-moment`,
  `quantum-genesis`, `vrig-cosmological`, `cellular-genesis`, `sa-sv-duality`,
  `worldview`, `gemeinwohl`, `spiking-aeon`, `phaethon-chimera`, `theta-resonance`,
  `medium-modulation`, `phi-scaling-validator`, `diffusive-routing`, `hikari-ledger`.
- No logic, API, or interface changes. Pure metadata/dependency sync.

---

## [1.0.0] – 2026-06-02

### Milestone — GenesisAeon Ecosystem Release

- Full CREP criticality spectrum: 40 domain packages (P17–P40) at production-stable status
- **P39 genesis-scope**: semantic coordinate system for Human-AI collaboration
  (SemanticAnchor, DriftModel, CollaborationCREP, SessionTracker — Diamond interface)
- **P32 beta-clustering-utac**: Φ^(1/3) ≈ 1.174 universal scaling across 78 threshold systems
- **P37 eml-utac-bridge**: full GenesisAeon reduction to single EML operator eml(x,y) = exp(x)−ln(y)
- **P38 phi-scaling-validator**: cross-domain Φ^(1/3) universality tests P17–P38
- Propagation script `scripts/propagate.py`: Diamond interface health check for all 40 packages
- Release infrastructure: `scripts/release_all.sh` + `.github/workflows/release.yml`
  with PyPI publish (PYPITOKEN repo secret), GitHub Release, Zenodo metadata
- `.zenodo.json` updated: 29 keywords, ecosystem context, Triple Universality note
- Version bumped: 0.4.2 → 1.0.0

### Triple Universality confirmed

AMOC (P18) = Neural Criticality (P20) = Theta-Resonance (P27) = Γ ≈ 0.251

---

## [0.4.2] – 2026-04-28

### Fixed

- Moved `sonification>=0.1.0` from `full-stack` to a new `audio` extra.
  The package has no Windows wheel on PyPI, causing `ResolutionImpossible`
  for all Windows users. The internal `Sonifier` class already handles the
  missing package gracefully via `ImportError` fallback, so no functionality
  is lost. Users who need audio output can install `genesis-os[audio]`.

---

## [0.4.0] – 2026-04-22

### Summary

v0.4.0 completes the **unified-mandala Integration** (Phases A–H), uniting the
GenesisAeon physics engine with the full mirror-machine, AFET, sigillin, and
live-data stack. Two Codex-flagged correctness issues in the governance layer
are resolved, and the project transitions to a **dual licence** (GPLv3 + CC BY 4.0).

### Added

**Phase A – Canonical CREP Engine** (`core/crep_engine.py`)
- `CanonicalCREPEngine`: Γ-computation with Gaussian coherence weighting
- `CREPTimeSeries`: rolling CREP time-series with pandas integration
- `crep_ts_bridge`: TypeScript/WASM bridge for browser-side CREP evaluation

**Phase B – SDE/Stochastic Bridge** (`core/utac_stoch_bridge.py`)
- `UTACStochBridge`: Euler–Maruyama SDE integration for stochastic H evolution
- `UTACJAXIntegrator`: JAX-accelerated deterministic + stochastic UTAC ODE
- `crep_ts_bridge.CREPTSBridge`: canonical TS-serialisation of CREP scores

**Phase C – AFET & Landauer Consistency** (`afet/`)
- `AFETEngine`: Anthropogenic Forcing & Emission Tracker (Esposito + Landauer)
- `LandauerConsistency`: thermodynamic bound-checker for KI-energy estimates
- `EspostoMapping`: non-equilibrium free-energy mapping onto CREP-Emergence

**Phase D – Mirror Machine** (`mirror/`)
- `TensionMetric` / `compute_tension_metric`: Γ_Klima · Q_KI / (V_Eis + ε)
- `DualDetector`: simultaneous collapse + regeneration phase detection
- `RegenerativeDamping`: 87.2× neuromorphic noise damping constant

**Phase E – Sigillin & Ritual Hooks** (`sigillin/`)
- `SigillinClient`: async metaquest bridge for symbolic trigger generation
- `RitualHooks`: pre/post cycle hooks for sigil injection
- `SigillinSync`: synchronous wrapper for non-async contexts

**Phase F – FraktalRun Engine** (`runtime/fraktalrun_engine.py`)
- `FraktalRunEngine`: fractal-depth phase-space exploration with Lyapunov exponent
- `FraktalRunConfig`: configurable depth, branching-factor, and chaos threshold

**Phase G – Live NATS/Prometheus** (`runtime/nats_publisher.py`, `monitoring/`)
- `NATSPublisher`: async NATS.io streaming of GenesisState per cycle
- `PrometheusExporter`: `/metrics` endpoint exposing CREP, entropy, tension gauges
- Phase alarms (`live_data/phase_alarm.py`) with configurable thresholds

**Phase H – Governance / OPA Bridge** (`governance/`)
- `EthicsGate`: circuit-breaker halting cycles on tension/personhood violation
- `OPABridge`: optional connection to unified-mandala OPA policy server
- `PersonhoodLevel` (INFORMATIONAL → POETIC): CREP-derived assessment

### Fixed

- **OPA Bridge boolean parsing** (`governance/opa_bridge.py`): OPA's
  `/v1/data/{policy}` returns `{"result": <bool>}` for boolean rules; the
  previous nested `.get("allow", True)` path silently returned `True` for all
  boolean policies. Now parses `result.get("result")` directly as `bool`.
- **Orchestrator tension-passing** (`core/orchestrator.py`): `phase_transition_loop`
  now extracts `tension = float(state.metadata.get("tension", 0.0))` and forwards
  it to `EthicsGate.check(state, tension=tension)`. Previously the gate received
  the default `0.0`, making the tension-based circuit-breaker inoperative even
  when live tension data was present in `state.metadata`.

### Changed

- **Licence**: from MIT to **GPLv3-or-later** (code) + **CC BY 4.0** (documentation)
- **Version**: 0.2.0 → 0.4.0 (unified-mandala integration milestone)
- `__init__.py`: `__license__` updated to `"GPL-3.0-or-later"`
- `pyproject.toml`: classifiers updated (`Development Status :: 4 - Beta`)

### Test Coverage

| Metric | Value |
|--------|-------|
| Total tests | 1221 |
| Coverage | 92 % |
| ruff | ✓ clean |
| mypy | ✓ clean |

---

## [0.2.0] – 2025-11-15

### Added
- Live cosmic-web emergence simulation via `CosmicWebSimulator`
- Real-time Dash web GUI with Mandala visualisation
- Sonification plugin (`dashboard/sonification.py`)
- JAX-accelerated UTAC integrator (`jax/integrator.py`)
- CLI (`genesis-os cycle`, `phases`, `info`)
- UTAC-Logistic entropy ODE (`runtime/utac.py`)

---

## [0.1.0] – 2025-07-01

### Added
- Initial release: GenesisOS orchestrator, CREP evaluator, PhaseMatrix
- Unified Lagrangian runtime engine
- Basic CLI and configuration system
