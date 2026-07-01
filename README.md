<p align="center">
  <img src="docs/assets/unified-mandala.svg" alt="Unified Mandala Logo" width="200"/>
</p>

<h1 align="center">genesis-os</h1>
<p align="center">
  <b>Self-reflecting OS framework with live cosmic-web emergence simulation, Dash GUI,<br>real-time phase transitions, and resonance coupling for GenesisAeon.</b>
</p>

<p align="center">
  <a href="https://pypi.org/project/genesis-os/"><img src="https://img.shields.io/pypi/v/genesis-os.svg" alt="PyPI version"/></a>
  <a href="https://pypi.org/project/genesis-os/"><img src="https://img.shields.io/pypi/pyversions/genesis-os.svg" alt="Python versions"/></a>
  <a href="https://github.com/GenesisAeon/genesis-os/actions"><img src="https://github.com/GenesisAeon/genesis-os/workflows/CI/badge.svg" alt="CI status"/></a>
  <a href="https://doi.org/10.5281/zenodo.19645351"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.19645351.svg" alt="DOI"/></a>
  <a href="docs/whitepaper.md"><img src="https://img.shields.io/badge/whitepaper-v1.0.0-blue" alt="Whitepaper"/></a>
  <a href="https://github.com/GenesisAeon/genesis-os/actions"><img src="https://img.shields.io/badge/coverage-92%25-brightgreen" alt="92% test coverage"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="GPLv3 License"/></a>
  <a href="https://creativecommons.org/licenses/by/4.0/"><img src="https://img.shields.io/badge/docs-CC%20BY%204.0-lightblue.svg" alt="CC BY 4.0"/></a>
  <a href="https://explore.openaire.eu/search/software?pid=10.5281%2Fzenodo.19645351"><img src="https://img.shields.io/badge/OpenAIRE-indexed-blue?logo=openaire" alt="OpenAIRE"/></a>
</p>

---

## Overview

**genesis-os** v1.0.1 is a unified Python framework implementing the GenesisAeon
architecture: a self-reflecting, entropy-governed, phase-transitioning system
described by the **Unified Lagrangian** formalism. It integrates CREP
(Coherence-Resonance-Emergence-Poetics) evaluation, a UTAC-Logistic entropy ODE,
live **cosmic-web emergence simulation** via `CosmicWebSimulator`, a real-time
**Dash web GUI**, Mandala visualisation, and sonification.

v1.0.0 was the **ecosystem milestone release**: all 40 domain packages (P17–P40)
reach production-stable status, spanning the full CREP criticality spectrum from
astrophysics (Γ ≈ 0.014) to network science (Γ ≈ 0.443). **v1.0.1** synchronises
the `[full-stack]` extra to **48 GenesisAeon ecosystem packages** on PyPI (correct
distribution names, floor pins `>=1.0.0`) — no API or logic changes.

### unified-mandala Integration — Phases A–H

| Phase | Module | Feature |
|-------|--------|---------|
| **A** | `core/crep_engine.py` | Canonical CREP Engine (Γ-weighted, TypeScript bridge) |
| **B** | `core/utac_stoch_bridge.py` | SDE/Stochastic UTAC Bridge (Euler–Maruyama + JAX) |
| **C** | `afet/` | AFET + Landauer Consistency (thermodynamic KI-energy bounds) |
| **D** | `mirror/` | Mirror Machine (Tension Metric, DualDetector, 87.2× damping) |
| **E** | `sigillin/` | Sigillin & Ritual Hooks (symbolic trigger generation) |
| **F** | `runtime/fraktalrun_engine.py` | FraktalRun Engine (fractal phase-space, Lyapunov exponent) |
| **G** | `runtime/nats_publisher.py` + `monitoring/` | Live NATS streaming + Prometheus `/metrics` |
| **H** | `governance/` | EthicsGate circuit-breaker + OPA Bridge + PersonhoodLevel |

### The Unified Lagrangian

```
L = T - V + Phi(H) + Gamma(C, R, E, P)
```

where:

- `T = (1/2) * kappa * R^2` — kinetic resonance-coupling energy
- `V = (1/2) * eta * H^2` — entropic resistance potential
- `Phi(H) = phi0 * ln(1 + H)` — self-reflection potential
- `Gamma(C,R,E,P) = (C * R * E * P)^(1/4)` — CREP coupling term (geometric mean; any zero component yields Γ=0)

### UTAC-Logistic Entropy Evolution

```
dH/dt = r * H * (1 - H/K) * tanh(sigma * Gamma)
```

### Self-Reflection Update

```
Phi_{n+1}(H) = Phi_n(H) * (1 + alpha * grad_H L)
```

where `alpha` is the reflection learning rate and `grad_H L` is
approximated from the L2 norm of the CREP gradient vector.

---

## Installation

```bash
# Core package
pip install genesis-os

# Core + live Dash web GUI
pip install "genesis-os[gui]"

# Full stack with all optional packages + GUI
pip install "genesis-os[full-stack,gui]"

# Development mode
pip install "genesis-os[dev]"
```

### Extra Packages

#### `[gui]` — Live Dash Web Dashboard

`pip install "genesis-os[gui]"` installs:

| Package | Version | Purpose |
|---------|---------|---------|
| `dash` | >=2.14.0 | Reactive web framework |
| `dash-bootstrap-components` | >=1.5.0 | Bootstrap theming |
| `plotly` | >=5.15.0 | Interactive charts (CREP radar, H/L/emergence) |

#### `[full-stack]` — GenesisAeon Ecosystem (48 packages)

`pip install "genesis-os[full-stack]"` installs **48 optional GenesisAeon packages**
(all pinned `>=1.0.0` unless noted), including:

| Category | Packages (examples) |
|----------|---------------------|
| **Core adapters** | `aeon-ai`, `utac-core`, `sigillin`, `mirror-machine`, `entropy-governance` |
| **Simulation** | `cosmic-web`, `universums-sim`, `cosmic-moment`, `feldtheorie`, `fieldtheory` |
| **UTAC domain (P17–P38)** | `amoc-utac`, `sandpile-utac`, `neural-avalanche-utac`, `hikari-ledger`, `diffusive-routing`, … |
| **Governance / Q4** | `genesis-scope`, `genesis-q4-core`, `worldview`, `gemeinwohl` |
| **Visualisation** | `mandala-visualizer`, `unified-mandala`, `climate-dashboard` |
| **Infrastructure** | `diamond-setup`, `entropy-table` (>=2.0.1), `genesisaeon-hexaagent` |

Full list: see `[project.optional-dependencies] full-stack` in `pyproject.toml`.
Audio output uses the separate `[audio]` extra (`genesisaeon-sonification`).

---

## Quick Start

```python
from genesis_os import GenesisOS
from genesis_os.core.orchestrator import GenesisConfig

# Create configuration
config = GenesisConfig(
    entropy=0.4,
    alpha=0.1,        # self-reflection learning rate
    max_cycles=50,
    transition_threshold=0.6,
    seed=42,
)

# Instantiate and run
genesis = GenesisOS(config=config)
final_state = genesis.run()

print(f"Phase: {final_state.phase.value}")
print(f"Entropy: {final_state.entropy:.4f}")
print(f"Phi(H): {final_state.phi:.4f}")
print(f"Lagrangian: {final_state.lagrangian:.4f}")
print(f"Transitions: {len(final_state.transitions)}")
print(f"Emergence Events: {len(final_state.emergence_events)}")
```

### Live Cosmic-Web Emergence Simulation (v0.2.0)

```python
from genesis_os import CosmicWebSimulator, GenesisOS
from genesis_os.core.orchestrator import GenesisConfig

config = GenesisConfig(entropy=0.4, max_cycles=50, seed=42)
genesis = GenesisOS(config=config, emergence_threshold=0.3)

for state in genesis.phase_transition_loop():
    summary = state.metadata.get("emergence_summary", {})
    if state.emergence_events:
        last = state.emergence_events[-1]
        print(
            f"Cycle {state.cycle}: EmergenceEvent "
            f"nodes={last.node_count} rate={last.emergence_rate:.4f} "
            f"density={summary.get('mean_density', 0.0):.3f}"
        )
```

### Real-Time Dash Web GUI (v0.2.0)

```bash
# Install GUI extra
pip install "genesis-os[gui]"

# Launch live dashboard at http://127.0.0.1:8050
genesis-os cycle --entropy 0.4 --max-cycles 200 --gui

# Custom port
genesis-os cycle --gui --gui-port 8080 --max-cycles 500
```

```python
# Programmatic GUI usage
from genesis_os import GenesisOS
from genesis_os.core.orchestrator import GenesisConfig
from genesis_os.dashboard.web_gui import GenesisWebGUI, GUISnapshot
import threading

config = GenesisConfig(entropy=0.4, max_cycles=200, seed=7)
genesis = GenesisOS(config=config)
gui = GenesisWebGUI(interval_ms=500)
gui.build_app()

# Run GUI in background
t = threading.Thread(target=lambda: gui.run(host="127.0.0.1", port=8050), daemon=True)
t.start()

for state in genesis.phase_transition_loop():
    esummary = state.metadata.get("emergence_summary", {})
    gui.push_snapshot(GUISnapshot(
        cycle=state.cycle,
        phase=state.phase.value,
        entropy=state.entropy,
        phi=state.phi,
        lagrangian=state.lagrangian,
        gamma=state.crep.gamma if state.crep else 0.0,
        mean_density=float(esummary.get("mean_density", 0.0)),
        active_nodes=int(esummary.get("active_nodes", 0)),
        emergence_events=len(state.emergence_events),
    ))
```

### Real-Time Loop with Mandala

```python
from genesis_os import GenesisOS
from genesis_os.core.orchestrator import GenesisConfig
from genesis_os.dashboard.mandala import MandalaDashboard

config = GenesisConfig(entropy=0.5, max_cycles=20, seed=7)
genesis = GenesisOS(config=config)
dashboard = MandalaDashboard()

for state in genesis.phase_transition_loop():
    if state.crep:
        print(dashboard.render_ascii(state.crep, state.phase, state.cycle))
```

### Sonification

```python
from genesis_os import GenesisOS
from genesis_os.core.orchestrator import GenesisConfig
from genesis_os.dashboard.sonification import Sonifier

config = GenesisConfig(max_cycles=10, seed=1)
genesis = GenesisOS(config=config)
sonifier = Sonifier()

for state in genesis.phase_transition_loop():
    if state.crep:
        frame = sonifier.crep_to_frequencies(state.crep, state.cycle)
        print(f"Cycle {state.cycle}: C={frame.frequencies['C']:.1f} Hz")
```

### Canonical CREP + Mandala Bridge (v0.4.0)

```python
from genesis_os import GenesisOS
from genesis_os.core.orchestrator import GenesisConfig
from genesis_os.core.crep_engine import CanonicalCREPEngine
from genesis_os.dashboard.mandala import MandalaDashboard

config = GenesisConfig(entropy=0.5, max_cycles=30, seed=42)
genesis = GenesisOS(config=config)
crep_engine = CanonicalCREPEngine()
mandala = MandalaDashboard()

for state in genesis.phase_transition_loop():
    if state.crep:
        # Canonical Γ with Gaussian coherence weighting
        canonical = crep_engine.evaluate(state.crep)
        tension = float(state.metadata.get("tension", 0.0))
        print(
            f"Cycle {state.cycle:3d} | "
            f"Γ_canonical={canonical.gamma:.4f} | "
            f"Tension={tension:.3f} | "
            f"Phase={state.phase.value}"
        )
        print(mandala.render_ascii(state.crep, state.phase, state.cycle))
```

### EthicsGate + Tension Circuit-Breaker (v0.4.0)

```python
from genesis_os import GenesisOS
from genesis_os.core.orchestrator import GenesisConfig

# EthicsGate enabled by default; halts cycles when tension > 5.0
config = GenesisConfig(
    entropy=0.6,
    max_cycles=100,
    ethics_gate_enabled=True,
    tension_threshold=5.0,   # Tension(t) = Γ_Klima · Q_KI / (V_Eis + ε)
    min_personhood_level=1,  # Require at least REACTIVE level
    seed=7,
)
genesis = GenesisOS(config=config)

for state in genesis.phase_transition_loop():
    tension = state.metadata.get("tension", 0.0)
    print(f"Cycle {state.cycle}: tension={tension:.3f}")
# Loop stops automatically if EthicsGate triggers
```

---

## CLI

```bash
# Run a cycle with real-time output + emergence events
genesis-os cycle --entropy 0.4 --max-cycles 50 --phases

# Headless simulation, JSON output (includes emergence_events + emergence_summary)
genesis-os cycle --simulate --entropy 0.3 --max-cycles 100 --seed 42

# Launch live Dash GUI at http://127.0.0.1:8050
genesis-os cycle --gui --entropy 0.4 --max-cycles 200

# GUI on custom port
genesis-os cycle --gui --gui-port 8080 --max-cycles 500

# With visualisation and sonification (requires [full-stack])
genesis-os cycle --visualize --sonify --max-cycles 20

# List phase information
genesis-os phases

# System info
genesis-os info
```

### CLI Reference

| Option | Default | Description |
|--------|---------|-------------|
| `--entropy FLOAT` | 0.5 | Initial entropy H in [0,1] |
| `--max-cycles INT` | 20 | Number of orchestration cycles |
| `--alpha FLOAT` | 0.1 | Self-reflection learning rate alpha |
| `--seed INT` | None | Random seed for reproducibility |
| `--phases` | False | Print phase transitions + emergence events |
| `--simulate` | False | Headless mode, JSON output |
| `--visualize` | False | Render Mandala dashboard |
| `--sonify` | False | Generate sonification output |
| `--gui` | False | Launch live Dash web GUI (requires `[gui]`) |
| `--gui-port INT` | 8050 | Dash server port |
| `--gui-host STR` | 127.0.0.1 | Dash server host |

---

## Architecture

```
genesis-os/
├── src/genesis_os/
│   ├── core/
│   │   ├── crep.py               # CREPEvaluator, CREPScore
│   │   ├── crep_engine.py        # CanonicalCREPEngine (Phase A)
│   │   ├── utac_stoch_bridge.py  # SDE/JAX bridge (Phase B)
│   │   ├── phase.py              # Phase, PhaseMatrix, PhaseTransition
│   │   └── orchestrator.py       # GenesisOS orchestrator
│   ├── afet/                     # AFET + Landauer thermodynamics (Phase C)
│   ├── mirror/
│   │   ├── tension_metric.py     # Tension(t) = Γ·Q_KI/(V_Eis+ε) (Phase D)
│   │   └── dual_detector.py      # Collapse + regeneration detector
│   ├── sigillin/                 # Symbolic trigger generation (Phase E)
│   ├── runtime/
│   │   ├── engine.py             # RuntimeEngine (Unified Lagrangian)
│   │   ├── utac.py               # UTACLogistic ODE
│   │   ├── emergence.py          # CosmicWebSimulator
│   │   ├── fraktalrun_engine.py  # Fractal phase-space exploration (Phase F)
│   │   └── nats_publisher.py     # Async NATS streaming (Phase G)
│   ├── monitoring/
│   │   └── prometheus_exporter.py  # /metrics endpoint (Phase G)
│   ├── governance/
│   │   ├── ethics_gate.py        # EthicsGate circuit-breaker (Phase H)
│   │   ├── opa_bridge.py         # OPA policy bridge (Phase H)
│   │   └── personhood.py         # PersonhoodLevel CREP assessment
│   ├── dashboard/
│   │   ├── mandala.py            # MandalaDashboard
│   │   ├── sonification.py       # Sonifier
│   │   └── web_gui.py            # Dash live dashboard
│   └── plugins/
│       ├── registry.py           # PluginRegistry
│       └── adapters/             # One adapter per optional package
```

---

## Development

```bash
git clone https://github.com/GenesisAeon/genesis-os.git
cd genesis-os
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src tests

# Type check
mypy src

# Build docs
mkdocs serve
```

---

## Citation

If you use **genesis-os** in academic work, please cite:

**Paper (V2 — peer-review expanded):**

```bibtex
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
```

**Software:**

```bibtex
@software{roemer2026genesisaeon_software,
  author       = {Römer, Johann},
  title        = {{genesis-os}: GenesisAeon Unified Framework — Python Implementation},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {v1.0.1},
  doi          = {10.5281/zenodo.19645351},
  url          = {https://doi.org/10.5281/zenodo.19645351}
}
```

Full bibliography (25 BibTeX entries including Bak, Pikovsky, GENERIC, ERA5,
GADGET-4, IllustrisTNG, IPCC AR6):
→ [`docs/genesisaeon_citations.bib`](docs/genesisaeon_citations.bib)

Paper PDF: [`docs/genesisaeon_v0.3.1_paper.pdf`](docs/genesisaeon_v0.3.1_paper.pdf)

APA: Römer, J. (2026, April). *GenesisAeon v0.3.1: A unified variational framework for emergent criticality across physical domains* (v2). Zenodo. https://doi.org/10.5281/zenodo.19645351

---

## License

- **Code**: [GNU General Public License v3 or later (GPLv3+)](LICENSE)
- **Documentation**: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

The dual-licence model allows free academic use and redistribution under GPLv3
while ensuring documentation and scientific content remain openly citable under
CC BY 4.0.  See `LICENSE` for the full GPLv3 text.

> *"A system that listens - a pattern that lives."*
> *Im Kreis der Genesis erwacht das Mandala.*
