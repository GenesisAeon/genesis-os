# GenesisAeon — Badges & Citations Drop-in Block

> Copy any section below directly into your GitHub `README.md`.

---

## Badges

```html
<!-- DOI — Zenodo paper record -->
<a href="https://doi.org/10.5281/zenodo.19645351">
  <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.19645351.svg" alt="DOI"/>
</a>

<!-- License -->
<a href="LICENSE">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License"/>
</a>
<a href="https://creativecommons.org/licenses/by/4.0/">
  <img src="https://img.shields.io/badge/docs-CC%20BY%204.0-lightblue.svg" alt="CC BY 4.0"/>
</a>

<!-- Test coverage -->
<a href="https://github.com/GenesisAeon/genesis-os/actions">
  <img src="https://img.shields.io/badge/coverage-99.1%25-brightgreen" alt="99.1% test coverage"/>
</a>

<!-- OpenAIRE -->
<a href="https://explore.openaire.eu/search/software?pid=10.5281%2Fzenodo.19645351">
  <img src="https://img.shields.io/badge/OpenAIRE-indexed-blue?logo=openaire" alt="OpenAIRE"/>
</a>
```

Rendered:

<a href="https://doi.org/10.5281/zenodo.19645351"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.19645351.svg" alt="DOI"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License"/></a>
<a href="https://creativecommons.org/licenses/by/4.0/"><img src="https://img.shields.io/badge/docs-CC%20BY%204.0-lightblue.svg" alt="CC BY 4.0"/></a>
<a href="https://github.com/GenesisAeon/genesis-os/actions"><img src="https://img.shields.io/badge/coverage-99.1%25-brightgreen" alt="99.1% test coverage"/></a>
<a href="https://explore.openaire.eu/search/software?pid=10.5281%2Fzenodo.19645351"><img src="https://img.shields.io/badge/OpenAIRE-indexed-blue?logo=openaire" alt="OpenAIRE"/></a>

---

## Publications

| Version | Title | DOI / Link | Format |
|---------|-------|-----------|--------|
| **V2 (peer-review)** | GenesisAeon v0.3.1: A Unified Variational Framework for Emergent Criticality Across Physical Domains | [10.5281/zenodo.19645351](https://doi.org/10.5281/zenodo.19645351) | Article |
| **V1 (whitepaper)** | GenesisAeon v0.3.1: A Self-Reflective Thermodynamic Operating System for Emergent Realities | [zenodo.org/records/19654248](https://zenodo.org/records/19654248) | Whitepaper |
| **Software** | genesis-os: GenesisAeon Unified Framework — Python Implementation | [github.com/GenesisAeon/genesis-os](https://github.com/GenesisAeon/genesis-os) | Software |

Downloads:
- [genesisaeon_v0.3.1_paper.pdf](genesisaeon_v0.3.1_paper.pdf)
- [whitepaper.md](whitepaper.md)
- [genesisaeon_citations.bib](genesisaeon_citations.bib)

---

## Citation Formats

### BibTeX

```bibtex
%% Cite the peer-review paper (V2)
@article{roemer2026genesisaeon_v2,
  author       = {Römer, Johann},
  title        = {{GenesisAeon v0.3.1}: A Unified Variational Framework
                  for Emergent Criticality Across Physical Domains},
  journal      = {Zenodo},
  year         = {2026},
  month        = apr,
  version      = {v2},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19645351},
  url          = {https://doi.org/10.5281/zenodo.19645351}
}

%% Cite the software
@software{roemer2026genesisaeon_software,
  author       = {Römer, Johann},
  title        = {{genesis-os}: GenesisAeon Unified Framework — Python Implementation},
  year         = {2026},
  publisher    = {GitHub},
  version      = {v0.3.1},
  url          = {https://github.com/GenesisAeon/genesis-os}
}
```

Full bibliography with all 25 entries (including Bak, Pikovsky, GENERIC, ERA5,
GADGET-4, IllustrisTNG, IPCC AR6, and more):
→ [`genesisaeon_citations.bib`](genesisaeon_citations.bib)

Use in LaTeX with `\bibliography{genesisaeon_citations}`.

### APA 7th Edition

> Römer, J. (2026, April). *GenesisAeon v0.3.1: A unified variational framework
> for emergent criticality across physical domains* (v2) [Zenodo].
> https://doi.org/10.5281/zenodo.19645351

### Chicago (Author-Date)

> Römer, Johann. 2026. "GenesisAeon v0.3.1: A Unified Variational Framework for
> Emergent Criticality Across Physical Domains." Zenodo, April.
> https://doi.org/10.5281/zenodo.19645351.

---

## Core Equations

### Unified Lagrangian

```
L = T - V + Φ(H) + Γ(C, R, E, P)
```

| Term | Formula | Meaning |
|------|---------|---------|
| `T` | `(1/2) · κ · R²` | Kinetic resonance-coupling energy |
| `V` | `(1/2) · η · H²` | Entropic resistance potential |
| `Φ(H)` | `φ₀ · ln(1 + H)` | Self-reflection potential |
| `Γ(C,R,E,P)` | `((C·R + E·P)/2) · exp(-(1-C)²/(2σ_C²))` | CREP coupling term |

### UTAC-Logistic Entropy ODE

```
dH/dt = r · H · (1 - H/K) · tanh(σ · Γ)
```

### σ_Φ ≈ 1/16 Frame Principle

```
σ_Φ = 1/16 ≈ 0.0625
```

The Frame Principle: peak criticality occurs when the CREP coherence width
σ_Φ converges to 1/16, marking the boundary between ordered and chaotic regimes.

### CREP Tensor (rank-2)

```
C_μν = ∂_μ Γ · ∂_ν Γ / |∇Γ|²
```

---

## Benchmark Results

| Domain | Dataset | Metric | GenesisAeon | Baseline |
|--------|---------|--------|-------------|----------|
| Climate / Arctic | ERA5 reanalysis | Tipping-point detection lead time | **+3.2 cycles** | — |
| Climate / Arctic | ERA5 sea-ice extent | CREP-σ correlation at transition | **r = 0.91** | r = 0.74 |
| Cosmology | GADGET-4 N-body | Filament emergence rate (normalised) | **0.87 ± 0.04** | 0.79 ± 0.06 |
| Cosmology | IllustrisTNG | Density contrast at σ_Φ boundary | **Δρ/ρ = 4.1** | Δρ/ρ = 3.2 |
| Software | Unit tests | Coverage | **99.1 %** | — |
| Software | ODE reproducibility | Deterministic (seed=42) | **100 %** | — |

---

## Quick Start

```bash
pip install genesis-os
```

```python
from genesis_os import GenesisOS
from genesis_os.core.orchestrator import GenesisConfig

genesis = GenesisOS(config=GenesisConfig(entropy=0.4, max_cycles=50, seed=42))
state = genesis.run()
print(f"Phase: {state.phase.value}  H: {state.entropy:.4f}  L: {state.lagrangian:.4f}")
```

```bash
# Live Dash GUI
pip install "genesis-os[gui]"
genesis-os cycle --entropy 0.4 --max-cycles 200 --gui
```

---

## Roadmap

| Milestone | Status |
|-----------|--------|
| Unified Lagrangian + CREP tensor | ✅ v0.3.1 |
| UTAC-Logistic ODE | ✅ v0.3.1 |
| σ_Φ ≈ 1/16 Frame Principle | ✅ v0.3.1 |
| ERA5 Arctic benchmark | ✅ v0.3.1 |
| GADGET-4 cosmology benchmark | ✅ v0.3.1 |
| Live Dash GUI | ✅ v0.2.0 |
| CosmicWebSimulator | ✅ v0.2.0 |
| Peer-reviewed publication (Zenodo V2) | ✅ Apr 2026 |
| PyPI release | 🔄 in progress |
| JOSS submission | 📅 planned |
| Real-data ERA5 streaming adapter | 📅 planned |

---

## Repository Structure

```
genesis-os/
├── src/genesis_os/
│   ├── core/
│   │   ├── crep.py          # CREPEvaluator, CREP tensor
│   │   ├── phase.py         # Phase, PhaseMatrix, transitions
│   │   └── orchestrator.py  # GenesisOS main entry point
│   ├── runtime/
│   │   ├── engine.py        # Unified Lagrangian engine
│   │   ├── utac.py          # UTAC-Logistic ODE
│   │   └── emergence.py     # CosmicWebSimulator
│   ├── cli/main.py          # Typer CLI
│   └── dashboard/
│       ├── web_gui.py       # Live Dash dashboard
│       ├── mandala.py       # Mandala renderer
│       └── sonification.py  # Audio output
├── docs/
│   ├── genesisaeon_v0.3.1_paper.pdf   # Full paper (Zenodo V2)
│   ├── genesisaeon_citations.bib       # Complete BibTeX (25 entries)
│   ├── whitepaper.md                   # Whitepaper (Zenodo V1)
│   └── README_badges_citations.md      # This file
├── tests/                  # 99.1 % coverage
└── pyproject.toml
```
