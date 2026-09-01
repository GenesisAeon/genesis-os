# GenesisAeon Ecosystem — Dependency Analysis Report

Repositories analyzed: **48 / 48**

## 1. Circular Dependencies

✅ No circular dependencies detected among analyzed repositories.

## 2. Diamond-Interface Method Coverage

Checks for definitions of: `run_cycle`, `get_crep_state`, `get_utac_state`, `get_phase_events`, `to_zenodo_record`

| Repository | run_cycle | get_crep_state | get_utac_state | get_phase_events | to_zenodo_record | Coverage |
|---|---|---|---|---|---|---|
| AdvancedWeightingSystems | — | — | — | — | — | 0/5 |
| Feldtheorie | — | — | — | — | — | 0/5 |
| HexaAgent | — | — | — | — | — | 0/5 |
| aeon-ai | — | — | — | — | — | 0/5 |
| afet-tensions | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| amazon-utac | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| amoc-utac | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| beta-clustering-utac | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| cellular-genesis | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| climate-dashboard | — | — | — | — | — | 0/5 |
| cosmic-moment | — | — | — | — | — | 0/5 |
| cosmic-web | — | — | — | — | — | 0/5 |
| cygnus-jet-utac | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| diamond-setup | — | — | — | — | — | 0/5 |
| diffusive-routing | — | — | — | — | — | 0/5 |
| eml-utac-bridge | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| entropy-governance | — | — | — | — | — | 0/5 |
| entropy-table | — | — | — | — | — | 0/5 |
| epi-sigillin | — | — | — | — | — | 0/5 |
| fieldtheory | — | — | — | — | — | 0/5 |
| gemeinwohl | — | — | — | — | — | 0/5 |
| genesis-os | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| genesis-q4-core | — | — | — | — | — | 0/5 |
| genesis-scope | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| hikari-ledger | — | — | — | — | — | 0/5 |
| implosive-genesis | — | — | — | — | — | 0/5 |
| implosive-origin-utac | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| mandala-visualize | — | — | — | — | — | 0/5 |
| medium-modulation | — | — | — | — | — | 0/5 |
| mirror-machine | — | — | — | — | — | 0/5 |
| neural-avalanche-utac | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| phaethon-chimera | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| phi-scaling-validator | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| quantum-genesis | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| sa-sv-duality | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| sandpile-utac | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| seismic-utac | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| sigillin | — | — | — | — | — | 0/5 |
| solar-flare-utac | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| sonification | — | — | — | — | — | 0/5 |
| spiking-aeon | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| theta-resonance | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| unified-mandala | ✅ | — | — | — | — | 1/5 |
| unified-mandala-Demo | — | — | — | — | — | 0/5 |
| universums-sim | — | — | — | — | — | 0/5 |
| utac-core | — | — | — | — | — | 0/5 |
| vrig-cosmological | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 |
| worldview | — | — | — | — | — | 0/5 |

## 3. Version Constraint Conflicts

Cases where a repo requires a higher version of a sibling package than its
`current_version` listed in `release_map.yml`.

| Repository | Dependency | Required | Current (release_map) |
|---|---|---|---|
| implosive-origin-utac | utac-core | `>=0.3.1` | `0.1.0` |

## 4. Unresolved (External) Dependencies

Dependencies that are not part of the GenesisAeon ecosystem (third-party PyPI packages).

<details><summary><b>AdvancedWeightingSystems</b> (15 external deps)</summary>

- `mkdocs-autorefs>=0.5.0`
- `mkdocs-material>=9.4.0`
- `mkdocs>=1.5.3`
- `mkdocstrings[python]>=0.24.0`
- `mypy>=1.7.0`
- `numpy>=1.26.0`
- `pydantic>=2.5.0`
- `pytest-cov>=4.1.0`
- `pytest-mock>=3.12.0`
- `pytest>=7.4.0`
- `rich>=13.0.0`
- `ruff>=0.1.8`
- `scipy>=1.11.0`
- `torch>=2.1.0`
- `typer[all]>=0.9.0`

</details>
<details><summary><b>Feldtheorie</b> (25 external deps)</summary>

- `black>=24.4,<27`
- `fastapi>=0.104,<0.129`
- `httpx>=0.25`
- `jsonschema>=4.20,<5`
- `matplotlib>=3.8,<3.11`
- `mypy>=1.10,<1.20`
- `myst-parser>=2.0,<5`
- `nox>=2024.4.15,<2025.12`
- `numpy>=1.26,<2.3`
- `openai>=1.0,<3`
- `pandas>=2.1,<2.4`
- `pytest-cov>=4.1,<8`
- `pytest>=8.2,<10`
- `python-dotenv>=1.0,<2`
- `pyyaml>=6.0,<7`
- `requests>=2.31,<3`
- `rich>=13.7,<15`
- `ruff>=0.5.0,<0.15`
- `scikit-learn>=1.4,<1.8`
- `scipy>=1.11,<1.16`
- `sphinx>=7.3,<9`
- `statsmodels>=0.14,<0.15`
- `typer>=0.12,<1`
- `uvicorn[standard]>=0.24,<0.41`
- `websockets>=12.0,<17`

</details>
<details><summary><b>HexaAgent</b> (2 external deps)</summary>

- `pytest-asyncio>=0.23`
- `pytest>=8`

</details>
<details><summary><b>aeon-ai</b> (10 external deps)</summary>

- `mkdocs-material>=9.5`
- `mkdocs>=1.6`
- `mkdocstrings[python]>=0.25`
- `numpy>=1.26`
- `pydantic>=2.0`
- `pytest-cov>=5.0`
- `pytest>=8.0`
- `rich>=13.0`
- `ruff>=0.4`
- `typer>=0.12`

</details>
<details><summary><b>afet-tensions</b> (13 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.13`
- `typer>=0.12.0`

</details>
<details><summary><b>amazon-utac</b> (16 external deps)</summary>

- `ipykernel>=6.0`
- `jupyter>=1.0`
- `matplotlib>=3.8`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.12`
- `typer>=0.12.0`

</details>
<details><summary><b>amoc-utac</b> (12 external deps)</summary>

- `ipykernel>=6.0.0`
- `jupyter>=1.0.0`
- `matplotlib>=3.9`
- `mypy>=1.10.0`
- `numpy>=1.26`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.13`
- `typer>=0.12.0`

</details>
<details><summary><b>beta-clustering-utac</b> (11 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `typer>=0.12.0`

</details>
<details><summary><b>cellular-genesis</b> (13 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26.0`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.12.0`
- `typer>=0.12.0`

</details>
<details><summary><b>climate-dashboard</b> (12 external deps)</summary>

- `dash>=2.17.0`
- `mkdocs-material>=9.6`
- `mkdocs>=1.6`
- `mkdocstrings[python]>=0.27`
- `numpy>=2.0.0`
- `pandas>=2.2.0`
- `plotly>=5.22.0`
- `pytest-cov>=5.0`
- `pytest>=8.0`
- `rich>=13.0.0`
- `ruff>=0.9`
- `typer>=0.15.0`

</details>
<details><summary><b>cosmic-moment</b> (10 external deps)</summary>

- `mkdocs-material>=9.6`
- `mkdocs>=1.6`
- `mkdocstrings[python]>=0.27`
- `numpy>=2.0.0`
- `pytest-cov>=5.0`
- `pytest>=8.0`
- `rich>=13.0.0`
- `ruff>=0.9`
- `sympy>=1.13.0`
- `typer>=0.15.0`

</details>
<details><summary><b>cosmic-web</b> (14 external deps)</summary>

- `dash>=2.17.0`
- `mkdocs-material>=9.6`
- `mkdocs>=1.6`
- `mkdocstrings[python]>=0.27`
- `mypy>=1.0`
- `networkx>=3.3`
- `numpy>=2.0.0`
- `pandas>=2.0.0`
- `plotly>=5.22.0`
- `pytest-cov>=5.0`
- `pytest>=8.0`
- `rich>=13.0.0`
- `ruff>=0.9`
- `typer>=0.15.0`

</details>
<details><summary><b>cygnus-jet-utac</b> (17 external deps)</summary>

- `astropy>=5.3`
- `ipywidgets`
- `jupyter`
- `matplotlib>=3.7`
- `mypy>=1.10`
- `nbconvert`
- `numpy>=1.24`
- `pandas>=2.0`
- `plotly`
- `pytest-cov>=5.0`
- `pytest>=7.0`
- `pyyaml>=6.0`
- `rich>=13.0`
- `ruff>=0.6.0`
- `scipy>=1.10`
- `tqdm>=4.65`
- `typer>=0.12.0`

</details>
<details><summary><b>diamond-setup</b> (11 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `typer>=0.12.0`

</details>
<details><summary><b>diffusive-routing</b> (11 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `typer>=0.12.0`

</details>
<details><summary><b>eml-utac-bridge</b> (12 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `typer>=0.12.0`

</details>
<details><summary><b>entropy-governance</b> (12 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mkdocstrings[python]>=0.27.0`
- `numpy>=2.0.0`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.0.0`
- `ruff>=0.6.0`
- `sympy>=1.13.0`
- `typer>=0.15.0`

</details>
<details><summary><b>entropy-table</b> (18 external deps)</summary>

- `black>=24.8`
- `jsonschema>=4.17`
- `mkdocs-gen-files>=0.5`
- `mkdocs-literate-nav>=0.6`
- `mkdocs-material>=9.5`
- `mkdocs>=1.6`
- `mkdocstrings[python]>=0.25`
- `mypy>=1.11`
- `pre-commit>=4.0`
- `pymdown-extensions>=10.0`
- `pytest-cov>=5.0`
- `pytest>=8.3`
- `pyyaml>=6.0`
- `ruff>=0.6`
- `sympy>=1.13`
- `typer[all]>=0.12`
- `types-PyYAML>=6.0`
- `types-jsonschema>=4.17`

</details>
<details><summary><b>epi-sigillin</b> (11 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `typer>=0.12.0`

</details>
<details><summary><b>fieldtheory</b> (11 external deps)</summary>

- `mkdocs-material>=9.6`
- `mkdocs>=1.6`
- `mkdocstrings[python]>=0.27`
- `numpy>=2.0.0`
- `pytest-cov>=5.0`
- `pytest>=8.0`
- `pyyaml>=6.0`
- `rich>=13.0.0`
- `ruff>=0.9`
- `sympy>=1.13.0`
- `typer>=0.15.0`

</details>
<details><summary><b>gemeinwohl</b> (17 external deps)</summary>

- `click>=8.1.0`
- `mkdocs-gen-files>=0.5.0`
- `mkdocs-literate-nav>=0.6.0`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.5.0`
- `mkdocstrings[python]>=0.24.0`
- `mypy>=1.9.0`
- `numpy>=1.26.0`
- `pydantic>=2.6.0`
- `pymdown-extensions>=10.7.0`
- `pytest-asyncio>=0.23.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `rich>=13.7.0`
- `ruff>=0.4.0`
- `scipy>=1.12.0`
- `typer>=0.12.0`

</details>
<details><summary><b>genesis-os</b> (24 external deps)</summary>

- `dash-bootstrap-components>=1.5.0`
- `dash>=2.14.0`
- `jax>=0.4.20`
- `jaxlib>=0.4.20`
- `matplotlib>=3.7.0`
- `mkdocs-autorefs>=0.5.0`
- `mkdocs-material>=9.2.0`
- `mkdocs>=1.5.0`
- `mkdocstrings[python]>=0.23.0`
- `mypy>=1.5.0`
- `networkx>=3.2`
- `numpy>=1.24.0`
- `plotly>=5.15.0`
- `pydantic>=2.0.0`
- `pytest-asyncio>=0.21.0`
- `pytest-cov>=4.1.0`
- `pytest>=7.4.0`
- `pyyaml>=6.0`
- `rich>=13.0.0`
- `ruff>=0.1.0`
- `scikit-learn>=1.3`
- `scipy>=1.10.0`
- `statsmodels>=0.14`
- `typer>=0.9.0`

</details>
<details><summary><b>genesis-q4-core</b> (10 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `typer>=0.12.0`

</details>
<details><summary><b>genesis-scope</b> (9 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `ruff>=0.6.0`
- `typer>=0.12.0`

</details>
<details><summary><b>hikari-ledger</b> (11 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `typer>=0.12.0`

</details>
<details><summary><b>implosive-genesis</b> (13 external deps)</summary>

- `matplotlib[animation]>=3.8.0`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `numpy>=1.26.0`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `sympy>=1.12`
- `typer>=0.12.0`

</details>
<details><summary><b>implosive-origin-utac</b> (11 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `typer>=0.12.0`

</details>
<details><summary><b>mandala-visualize</b> (13 external deps)</summary>

- `field-theory>=0.1.0`
- `matplotlib>=3.8.0`
- `mkdocs-material>=9.6`
- `mkdocs>=1.6`
- `mkdocstrings[python]>=0.27`
- `networkx>=3.3`
- `numpy>=1.26.0`
- `pytest-cov>=5.0`
- `pytest>=8.0`
- `pyyaml>=6.0`
- `rich>=13.0.0`
- `ruff>=0.9`
- `typer>=0.15.0`

</details>
<details><summary><b>medium-modulation</b> (9 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `numpy>=2.0.0`
- `pytest-cov>=5.0`
- `pytest>=8.0`
- `rich>=13.0.0`
- `ruff>=0.9`
- `sympy>=1.13.0`
- `typer>=0.15.0`

</details>
<details><summary><b>mirror-machine</b> (10 external deps)</summary>

- `mkdocs-material>=9.6`
- `mkdocs>=1.6`
- `mkdocstrings[python]>=0.27`
- `numpy>=2.0.0`
- `pytest-cov>=5.0`
- `pytest>=8.0`
- `pyyaml>=6.0`
- `rich>=13.0.0`
- `ruff>=0.9`
- `typer>=0.15.0`

</details>
<details><summary><b>neural-avalanche-utac</b> (13 external deps)</summary>

- `matplotlib>=3.8.0`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26.0`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.12.0`
- `typer>=0.12.0`

</details>
<details><summary><b>phaethon-chimera</b> (14 external deps)</summary>

- `jupyter>=1.0.0`
- `matplotlib>=3.8.0`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26.0`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.12.0`
- `typer>=0.12.0`

</details>
<details><summary><b>phi-scaling-validator</b> (15 external deps)</summary>

- `jupyter>=1.0`
- `matplotlib>=3.9`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.13`
- `typer>=0.12.0`

</details>
<details><summary><b>quantum-genesis</b> (13 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `qiskit-ibm-runtime>=0.20`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `stim>=1.13.0`
- `typer>=0.12.0`

</details>
<details><summary><b>sa-sv-duality</b> (12 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26.0`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.12.0`
- `typer>=0.12.0`

</details>
<details><summary><b>sandpile-utac</b> (14 external deps)</summary>

- `matplotlib>=3.8.0`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26.0`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.12.0`
- `typer>=0.12.0`

</details>
<details><summary><b>seismic-utac</b> (14 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.13`
- `typer>=0.12.0`
- `types-PyYAML>=6.0`

</details>
<details><summary><b>sigillin</b> (13 external deps)</summary>

- `mkdocs-material>=9.6`
- `mkdocs>=1.6`
- `mkdocstrings[python]>=0.27`
- `mypy>=1.10`
- `numpy>=1.26`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0`
- `pytest>=8.0`
- `pyyaml>=6.0`
- `rich>=13.0`
- `ruff>=0.9`
- `typer>=0.15.0`
- `types-PyYAML>=6.0`

</details>
<details><summary><b>solar-flare-utac</b> (14 external deps)</summary>

- `astropy>=6.0`
- `matplotlib>=3.9`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.13`
- `typer>=0.12.0`

</details>
<details><summary><b>sonification</b> (14 external deps)</summary>

- `matplotlib>=3.8.0`
- `midiutil>=1.2.1`
- `mkdocs-material>=9.6.0`
- `mkdocs>=1.6.0`
- `mkdocstrings[python]>=0.27.0`
- `mypy>=1.10.0`
- `numpy>=2.0.0`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `rich>=13.0.0`
- `ruff>=0.9.0`
- `scipy>=1.14.0`
- `typer>=0.15.0`

</details>
<details><summary><b>spiking-aeon</b> (7 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `ruff>=0.6.0`

</details>
<details><summary><b>theta-resonance</b> (7 external deps)</summary>

- `mne>=1.7`
- `mypy>=1.10.0`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `ruff>=0.6.0`

</details>
<details><summary><b>unified-mandala</b> (34 external deps)</summary>

- `aiohttp>=3.9.0`
- `fastapi>=0.110.0`
- `gradio>=4.20.0`
- `hatch>=1.9.0`
- `httpx>=0.27.0`
- `loguru>=0.7.2`
- `matplotlib>=3.8.0`
- `mkdocs-autorefs>=1.0.0`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.5.3`
- `mkdocstrings[python]>=0.24.0`
- `mypy>=1.9.0`
- `netCDF4>=1.6.0`
- `networkx>=3.2.0`
- `numpy>=1.26.0`
- `pandas>=2.2.0`
- `plotly>=5.18.0`
- `pydantic>=2.6.0`
- `pytest-asyncio>=0.23.0`
- `pytest-cov>=5.0.0`
- `pytest-mock>=3.14.0`
- `pytest-xdist>=3.5.0`
- `pytest>=8.1.0`
- `pyyaml>=6.0.1`
- `requests>=2.31.0`
- `rich>=13.7.0`
- `ruff>=0.3.0`
- `scipy>=1.12.0`
- `sounddevice>=0.4.6`
- `streamlit>=1.32.0`
- `toml>=0.10.2`
- `typer>=0.12.0`
- `uvicorn>=0.27.0`
- `xarray>=2024.1.0`

</details>
<details><summary><b>universums-sim</b> (27 external deps)</summary>

- `dash>=2.16.0`
- `factory-boy>=3.3.0`
- `freezegun>=1.4.0`
- `hypothesis>=6.100.0`
- `matplotlib>=3.8.0`
- `mkdocs-autorefs>=1.0.0`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.5.3`
- `mkdocstrings[python]>=0.24.0`
- `mypy>=1.9.0`
- `numpy>=1.26.0`
- `pillow>=10.2.0`
- `plotly>=5.20.0`
- `pydantic>=2.6.0`
- `pytest-asyncio>=0.23.0`
- `pytest-benchmark>=4.0.0`
- `pytest-cov>=5.0.0`
- `pytest-mock>=3.14.0`
- `pytest-xdist>=3.5.0`
- `pytest>=8.1.0`
- `rich>=13.7.0`
- `ruff>=0.4.0`
- `scipy>=1.12.0`
- `sounddevice>=0.4.6`
- `soundfile>=0.12.1`
- `structlog>=24.1.0`
- `typer>=0.12.0`

</details>
<details><summary><b>utac-core</b> (12 external deps)</summary>

- `field-theory>=0.1.0`
- `mkdocs-material>=9.6`
- `mkdocs>=1.6`
- `mkdocstrings[python]>=0.27`
- `numpy>=2.0.0`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0`
- `pytest>=8.0`
- `rich>=13.0.0`
- `ruff>=0.9`
- `sympy>=1.13.0`
- `typer>=0.15.0`

</details>
<details><summary><b>vrig-cosmological</b> (11 external deps)</summary>

- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mypy>=1.10.0`
- `numpy>=1.26`
- `pre-commit>=3.7.0`
- `pytest-cov>=5.0.0`
- `pytest>=8.0.0`
- `pyyaml>=6.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `typer>=0.12.0`

</details>
<details><summary><b>worldview</b> (16 external deps)</summary>

- `hypothesis>=6.100.0`
- `mkdocs-autorefs>=1.0.0`
- `mkdocs-material>=9.5.0`
- `mkdocs>=1.6.0`
- `mkdocstrings[python]>=0.25.0`
- `mypy>=1.10.0`
- `numpy>=1.26`
- `pre-commit>=3.7.0`
- `pydantic>=2.7`
- `pytest-cov>=5.0.0`
- `pytest-mock>=3.14.0`
- `pytest>=8.0.0`
- `rich>=13.7.0`
- `ruff>=0.6.0`
- `scipy>=1.13`
- `typer>=0.12.0`

</details>

## 5. Intra-Org Dependency Graph

| Repository | Depends on (GenesisAeon) |
|---|---|
| AdvancedWeightingSystems | cosmic-web, entropy-governance, mandala-visualize, mirror-machine, sigillin, utac-core |
| Feldtheorie | — |
| HexaAgent | — |
| aeon-ai | AdvancedWeightingSystems, cosmic-web, entropy-governance, fieldtheory, mandala-visualize, mirror-machine, sigillin, utac-core |
| afet-tensions | — |
| amazon-utac | — |
| amoc-utac | — |
| beta-clustering-utac | — |
| cellular-genesis | — |
| climate-dashboard | cosmic-moment, entropy-governance, entropy-table, fieldtheory, implosive-genesis, mandala-visualize, medium-modulation, sigillin, sonification, utac-core |
| cosmic-moment | entropy-governance, entropy-table, implosive-genesis, medium-modulation |
| cosmic-web | climate-dashboard, cosmic-moment, entropy-governance, entropy-table, fieldtheory, implosive-genesis, mandala-visualize, medium-modulation, mirror-machine, sigillin, sonification, utac-core |
| cygnus-jet-utac | genesis-os |
| diamond-setup | — |
| diffusive-routing | — |
| eml-utac-bridge | — |
| entropy-governance | implosive-genesis |
| entropy-table | — |
| epi-sigillin | — |
| fieldtheory | cosmic-moment, entropy-governance, entropy-table, implosive-genesis, medium-modulation |
| gemeinwohl | aeon-ai, entropy-governance, genesis-os, sigillin, unified-mandala, universums-sim, worldview |
| genesis-os | AdvancedWeightingSystems, aeon-ai, climate-dashboard, cosmic-web, entropy-governance, entropy-table, fieldtheory, implosive-genesis, mandala-visualize, mirror-machine, sigillin, sonification, utac-core |
| genesis-q4-core | — |
| genesis-scope | — |
| hikari-ledger | — |
| implosive-genesis | — |
| implosive-origin-utac | implosive-genesis, utac-core |
| mandala-visualize | cosmic-moment, entropy-governance, entropy-table, implosive-genesis, medium-modulation, sigillin, utac-core |
| medium-modulation | entropy-governance, entropy-table, implosive-genesis |
| mirror-machine | climate-dashboard, cosmic-moment, entropy-governance, entropy-table, fieldtheory, implosive-genesis, mandala-visualize, medium-modulation, sigillin, sonification, utac-core |
| neural-avalanche-utac | — |
| phaethon-chimera | — |
| phi-scaling-validator | — |
| quantum-genesis | — |
| sa-sv-duality | — |
| sandpile-utac | — |
| seismic-utac | — |
| sigillin | cosmic-moment, entropy-governance, entropy-table, fieldtheory, implosive-genesis, medium-modulation |
| solar-flare-utac | — |
| sonification | cosmic-moment, entropy-governance, entropy-table, fieldtheory, implosive-genesis, mandala-visualize, medium-modulation, sigillin, utac-core |
| spiking-aeon | — |
| theta-resonance | — |
| unified-mandala | — |
| unified-mandala-Demo | — |
| universums-sim | AdvancedWeightingSystems, aeon-ai, climate-dashboard, cosmic-web, entropy-governance, entropy-table, fieldtheory, genesis-os, implosive-genesis, mandala-visualize, mirror-machine, sigillin, sonification, utac-core |
| utac-core | cosmic-moment, entropy-governance, entropy-table, implosive-genesis, medium-modulation, sigillin |
| vrig-cosmological | — |
| worldview | aeon-ai, entropy-governance, genesis-os, sigillin, unified-mandala, universums-sim, utac-core |
