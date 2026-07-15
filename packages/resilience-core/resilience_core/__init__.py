"""resilience-core: UTAC-derived system resilience (Ρ) for GenesisAeon.

Package 40 — domänenübergreifende Systemresilienzgröße Ρ.
"""

from __future__ import annotations

from resilience_core.cascade import detect_cascade
from resilience_core.constants import (
    C_CRITICAL,
    COLLAPSE_THRESHOLD,
    GAMMA_MAX,
    SIGMA,
    SIGMA_PHI,
)
from resilience_core.coupling import CouplingMatrix
from resilience_core.eigenrate import ResilienceEigenrate
from resilience_core.frame_principle import frame_principle_limit
from resilience_core.rho_calculator import ResilienceState, RhoCalculator
from resilience_core.system import ResilienceCore

__version__ = "1.0.0"
__all__ = [
    "ResilienceCore",
    "ResilienceState",
    "ResilienceEigenrate",
    "CouplingMatrix",
    "RhoCalculator",
    "detect_cascade",
    "frame_principle_limit",
    "C_CRITICAL",
    "COLLAPSE_THRESHOLD",
    "GAMMA_MAX",
    "SIGMA",
    "SIGMA_PHI",
]
