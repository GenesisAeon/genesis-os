"""genesis-os: Self-reflecting OS framework with real-time phase transitions.

A unified platform for GenesisAeon's CREP-based orchestration, resonance coupling,
live cosmic-web emergence simulation, and Dash GUI. Implements the Unified
Lagrangian formalism with self-reflection loops, entropy-governed phase transitions,
and :class:`~genesis_os.runtime.emergence.CosmicWebSimulator`.
"""

from __future__ import annotations

__version__ = "0.2.0"
__author__ = "GenesisAeon"
__license__ = "MIT"
__all__ = [
    "CREPEvaluator",
    "CosmicWebSimulator",
    "GenesisOS",
    "PhaseMatrix",
    "RuntimeEngine",
    "__version__",
    "utac_core",
]

from genesis_os.core.crep import CREPEvaluator
from genesis_os.core.orchestrator import GenesisOS
from genesis_os.core.phase import PhaseMatrix
from genesis_os.plugins.adapters import utac_core
from genesis_os.runtime.emergence import CosmicWebSimulator
from genesis_os.runtime.engine import RuntimeEngine
