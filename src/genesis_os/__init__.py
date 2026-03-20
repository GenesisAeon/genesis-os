"""genesis-os: Self-reflecting OS framework with real-time phase transitions.

A unified platform for GenesisAeon's CREP-based orchestration, resonance coupling,
and cosmic-web simulation. Implements the Unified Lagrangian formalism with
self-reflection loops and entropy-governed phase transitions.
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "GenesisAeon"
__license__ = "MIT"
__all__ = [
    "CREPEvaluator",
    "GenesisOS",
    "PhaseMatrix",
    "RuntimeEngine",
    "__version__",
]

from genesis_os.core.crep import CREPEvaluator
from genesis_os.core.orchestrator import GenesisOS
from genesis_os.core.phase import PhaseMatrix
from genesis_os.runtime.engine import RuntimeEngine
