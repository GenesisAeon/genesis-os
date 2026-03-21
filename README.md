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
  <a href="https://doi.org/10.5281/zenodo.19140088"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.19140088.svg" alt="DOI"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License"/></a>
</p>

---

## Overview

**genesis-os** v0.2.0 is a unified Python framework implementing the GenesisAeon
architecture: a self-reflecting, entropy-governed, phase-transitioning system
described by the **Unified Lagrangian** formalism. It integrates CREP
(Coherence-Resonance-Emergence-Poetics) evaluation, a UTAC-Logistic entropy ODE,
live **cosmic-web emergence simulation** via `CosmicWebSimulator`, a real-time
**Dash web GUI**, Mandala visualisation, and sonification.

### The Unified Lagrangian

```
L = T - V + Phi(H) + Gamma(C, R, E, P)
```

where:

- `T = (1/2) * kappa * R^2` — kinetic resonance-coupling energy
- `V = (1/2) * eta * H^2` — entropic resistance potential
- `Phi(H) = phi0 * ln(1 + H)` — self-reflection potential
- `Gamma(C,R,E,P) = ((C*R + E*P) / 2) * exp(-(1-C)^2 / (2*sigma_C^2))` — CREP coupling term

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

#### `[full-stack]` — All Optional Adapters

`pip install "genesis-os[full-stack]"` installs:

| Package | Version | Purpose |
|---------|---------|---------|
| `aeon-ai` | >=0.2.0 | PhaseDetector + SelfReflector |
| `advanced-weighting-systems` | >=0.1.0 | CREP vector weighting |
| `fieldtheory` | >=0.1.0 | Field-theoretic potentials |
| `mirror-machine` | >=0.1.0 | Recursive resonance mirroring |
| `cosmic-web` | >=0.2.0 | Large-scale structure simulation |
| `sigillin` | >=0.1.0 | Symbolic trigger generation |
| `entropy-governance` | >=0.1.0 | Policy-based entropy control |
| `utac-core` | >=0.1.0 | External UTAC implementation |
| `mandala-visualizer` | >=0.1.0 | Advanced mandala rendering |
| `sonification` | >=0.1.0 | Audio synthesis output |
| `climate-dashboard` | >=0.1.0 | Environmental entropy coupling |
| `implosive-genesis` | >=0.1.0 | Implosive field dynamics |
| `entropy-table` | >=0.1.0 | Tabular entropy state lookup |

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
│   │   ├── crep.py          # CREPEvaluator, CREPScore
│   │   ├── phase.py         # Phase, PhaseMatrix, PhaseTransition
│   │   └── orchestrator.py  # GenesisOS (main entry point) + EmergenceEvent
│   ├── runtime/
│   │   ├── engine.py        # RuntimeEngine (Unified Lagrangian)
│   │   ├── utac.py          # UTACLogistic ODE
│   │   └── emergence.py     # CosmicWebSimulator, EmergenceEvent (v0.2.0)
│   ├── cli/
│   │   └── main.py          # Typer CLI
│   ├── dashboard/
│   │   ├── mandala.py       # MandalaDashboard
│   │   ├── sonification.py  # Sonifier
│   │   └── web_gui.py       # GenesisWebGUI – Dash live dashboard (v0.2.0)
│   └── plugins/
│       ├── registry.py      # PluginRegistry
│       └── adapters/        # One adapter per optional package
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

```bibtex
@software{genesis_os_2025,
  author    = {GenesisAeon},
  title     = {genesis-os: Live cosmic-web emergence simulation and Dash GUI
               for self-reflecting phase-transition systems},
  year      = {2025},
  version   = {0.2.0},
  doi       = {10.5281/zenodo.19140088},
  url       = {https://github.com/GenesisAeon/genesis-os},
}
```

---

## License

- **Code**: MIT License
- **Documentation**: CC BY 4.0
- **UI Assets**: MPL-2.0

> *"A system that listens - a pattern that lives."*
> *Im Kreis der Genesis erwacht das Mandala.*
