<p align="center">
  <img src="docs/assets/unified-mandala.svg" alt="Unified Mandala Logo" width="200"/>
</p>

<h1 align="center">genesis-os</h1>
<p align="center">
  <b>Self-reflecting OS framework with real-time phase transitions, resonance coupling,<br>and cosmic-web simulation for GenesisAeon.</b>
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

**genesis-os** is a unified Python framework implementing the GenesisAeon
architecture: a self-reflecting, entropy-governed, phase-transitioning system
described by the **Unified Lagrangian** formalism. It integrates CREP
(Coherence-Resonance-Emergence-Poetics) evaluation, a UTAC-Logistic entropy
ODE, real-time Mandala visualisation, and sonification.

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

# Full stack with all optional packages
pip install "genesis-os[full-stack]"

# Development mode
pip install "genesis-os[dev]"
```

### Full-Stack Extra Packages

`pip install "genesis-os[full-stack]"` installs:

| Package | Version | Purpose |
|---------|---------|---------|
| `aeon-ai` | >=0.2.0 | PhaseDetector + SelfReflector |
| `advanced-weighting-systems` | >=0.1.0 | CREP vector weighting |
| `fieldtheory` | >=0.1.0 | Field-theoretic potentials |
| `mirror-machine` | >=0.1.0 | Recursive resonance mirroring |
| `cosmic-web` | >=0.1.0 | Large-scale structure simulation |
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
# Run a cycle with real-time output
genesis-os cycle --entropy 0.4 --max-cycles 50 --phases

# Headless simulation, JSON output
genesis-os cycle --simulate --entropy 0.3 --max-cycles 100 --seed 42

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
| `--phases` | False | Print phase transitions |
| `--simulate` | False | Headless mode, JSON output |
| `--visualize` | False | Render Mandala dashboard |
| `--sonify` | False | Generate sonification output |

---

## Architecture

```
genesis-os/
├── src/genesis_os/
│   ├── core/
│   │   ├── crep.py          # CREPEvaluator, CREPScore
│   │   ├── phase.py         # Phase, PhaseMatrix, PhaseTransition
│   │   └── orchestrator.py  # GenesisOS (main entry point)
│   ├── runtime/
│   │   ├── engine.py        # RuntimeEngine (Unified Lagrangian)
│   │   └── utac.py          # UTACLogistic ODE
│   ├── cli/
│   │   └── main.py          # Typer CLI
│   ├── dashboard/
│   │   ├── mandala.py       # MandalaDashboard
│   │   └── sonification.py  # Sonifier
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
@software{genesis_os_2024,
  author    = {GenesisAeon},
  title     = {genesis-os: Self-reflecting OS framework for phase transitions
               and resonance coupling},
  year      = {2024},
  version   = {0.1.0},
  doi       = {10.5281/zenodo.genesis-os},
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
