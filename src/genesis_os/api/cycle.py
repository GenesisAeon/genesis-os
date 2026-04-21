"""GenesisAeon cycle phase definitions.

Updated cycle phases after Feldtheorie integration (Phase 8).
"""

from __future__ import annotations

from typing import Final

CYCLE_PHASES: Final[list[str]] = [
    "core",       # Unified Lagrangian + UTACBridge
    "afet",       # Field entropy computation (AFET)
    "crep",       # Enhanced CREP tensor (C, R, E, P empirical metrics)
    "utac_ode",   # Logistic ODE integration
    "vrig",       # Information-geometric velocity (v_RIG)
    "mirror",     # Mirror-Machine + Phase-Transition-Loop
    "aeon",       # Nullkern + AeonShell + LanternNet     ← NEW
    "science",    # Empirical β-pipeline (78 systems)    ← NEW
    "cosmicweb",  # N-Body resonance module
    "api",        # FastAPI + WebSocket telemetry         ← UPGRADED
    "sigillin",   # Trilayer sync check                   ← NEW
]
