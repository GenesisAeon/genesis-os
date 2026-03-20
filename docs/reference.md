# API Reference

## Mathematical Foundations

### Unified Lagrangian

The core formalism of genesis-os is the Unified Lagrangian:

$$\mathcal{L} = T - V + \Phi(H) + \Gamma(C, R, E, P)$$

**Kinetic Term** (resonance-coupling energy):

$$T = \frac{1}{2} \kappa R^2$$

**Potential Term** (entropic resistance):

$$V = \frac{1}{2} \eta H^2$$

**Self-Reflection Potential**:

$$\Phi(H) = \phi_0 \ln(1 + H)$$

**CREP Coupling Term**:

$$\Gamma(C, R, E, P) = \frac{C \cdot R + E \cdot P}{2} \cdot
\exp\!\left(-\frac{(1-C)^2}{2\sigma_C^2}\right)$$

### UTAC-Logistic Entropy Evolution

$$\frac{dH}{dt} = r H \left(1 - \frac{H}{K}\right) \tanh(\sigma \Gamma)$$

Forward-Euler integration with step $\Delta t = 1$:

$$H_{t+1} = H_t + r H_t \left(1 - \frac{H_t}{K}\right) \tanh(\sigma \Gamma) \cdot \Delta t$$

**Equilibria:**

- $H^* = K$ when $\tanh(\sigma\Gamma) > 0$ (positive CREP coupling)
- $H^* = 0$ when $\tanh(\sigma\Gamma) < 0$ (negative CREP coupling)

### Self-Reflection Update

$$\Phi_{n+1}(H) = \Phi_n(H) \cdot \left(1 + \alpha \cdot \left\|\nabla_H \mathcal{L}\right\|\right)$$

The gradient $\nabla_H \mathcal{L}$ is approximated by the finite-difference
CREP gradient vector $\Delta \mathbf{CREP} = \mathbf{CREP}_{n} - \mathbf{CREP}_{n-1}$.

---

## Module Reference

### `genesis_os.core.crep`

::: genesis_os.core.crep
    options:
      show_root_heading: true
      heading_level: 4

### `genesis_os.core.phase`

::: genesis_os.core.phase
    options:
      show_root_heading: true
      heading_level: 4

### `genesis_os.core.orchestrator`

::: genesis_os.core.orchestrator
    options:
      show_root_heading: true
      heading_level: 4

### `genesis_os.runtime.engine`

::: genesis_os.runtime.engine
    options:
      show_root_heading: true
      heading_level: 4

### `genesis_os.runtime.utac`

::: genesis_os.runtime.utac
    options:
      show_root_heading: true
      heading_level: 4

### `genesis_os.dashboard.mandala`

::: genesis_os.dashboard.mandala
    options:
      show_root_heading: true
      heading_level: 4

### `genesis_os.dashboard.sonification`

::: genesis_os.dashboard.sonification
    options:
      show_root_heading: true
      heading_level: 4

### `genesis_os.plugins.registry`

::: genesis_os.plugins.registry
    options:
      show_root_heading: true
      heading_level: 4

---

## Phase Matrix

| Phase | CREP Focus | Description |
|-------|-----------|-------------|
| Initiation | C (Coherence) | Concept and coherence — seeding the field |
| Activation | R (Resonance) | Resonance and exchange — coupling subsystems |
| Integration | E (Emergence) | Emergence and development — complex patterns |
| Reflection | P (Poetics) | Poetics and persistence — self-reflection update |

---

## Plugin Adapters

Each plugin in `genesis_os.plugins.adapters` exposes a single `plugin_fn`:

```python
def plugin_fn(state: GenesisState) -> dict[str, Any]: ...
```

The function must:
1. Accept a `GenesisState` instance
2. Return a `dict` (never raise)
3. Include an `*_available: bool` key

| Adapter | Target Package | Key Output |
|---------|----------------|------------|
| `aeon_ai` | aeon-ai >=0.2.0 | `aeon_phase`, `aeon_reflection` |
| `advanced_weighting` | advanced-weighting-systems | `crep_weights` |
| `fieldtheory` | fieldtheory | `field_potential` |
| `mirror_machine` | mirror-machine | `mirror_resonance` |
| `cosmic_web` | cosmic-web | `node_density` |
| `sigillin` | sigillin | `sigil_token` |
| `entropy_governance` | entropy-governance | `governed_entropy` |
| `utac_core` | utac-core | `utac_entropy` |
| `mandala_visualizer` | mandala-visualizer | `mandala_visualizer_available` |
| `sonification_adapter` | sonification | `sonification_available` |
| `climate_dashboard` | climate-dashboard | `climate_entropy` |
| `implosive_genesis` | implosive-genesis | `implosive_strength` |
| `entropy_table` | entropy-table | `entropy_table_entry` |

---

## Sonification Frequency Mapping

Each CREP axis maps to a frequency band using logarithmic scaling:

$$f = f_{\min} \cdot \exp\!\left(v \cdot \ln\frac{f_{\max}}{f_{\min}}\right)$$

where $v \in [0,1]$ is the CREP axis value.

| Axis | Band | Default Range |
|------|------|---------------|
| C (Coherence) | Fundamental | 220 – 440 Hz |
| R (Resonance) | Harmonic overtone | 440 – 880 Hz |
| E (Emergence) | Sub-octave | 110 – 220 Hz |
| P (Poetics) | Upper harmonic | 880 – 1760 Hz |

---

## Scientific References

1. Haken, H. (1983). *Synergetics: An Introduction*. Springer.
2. Prigogine, I., & Stengers, I. (1984). *Order Out of Chaos*. Bantam.
3. Wolfram, S. (2002). *A New Kind of Science*. Wolfram Media.
4. Friston, K. (2010). The free-energy principle: a unified brain theory?
   *Nature Reviews Neuroscience*, 11(2), 127–138.
5. GenesisAeon (2024). *genesis-os v0.1.0*. Zenodo.
   https://doi.org/10.5281/zenodo.genesis-os
