"""Reference calibration points from the CREP Atlas.

r_required = Ρ_atlas / (tanh²(σ·Γ) · (1 − Γ/Γ_max))

All r values listed here are analytically derived from Atlas targets;
status = "estimated" until real time-series fits are available.
"""

from __future__ import annotations

import numpy as np

from resilience_core.constants import GAMMA_MAX, SIGMA

# (gamma, rho_atlas_target) → r_required
_ATLAS_POINTS: dict[str, tuple[float, float]] = {
    "amoc":     (0.251, 0.65),
    "arctic":   (0.920, 0.05),
    "sandpile": (0.296, 0.75),
    "quantum":  (0.050, 0.90),
}

RESILIENCE_BENCHMARKS: dict[str, tuple[float, float]] = {
    "amoc_rho":              (0.65, 0.10),
    "arctic_rho":            (0.05, 0.02),
    "sandpile_rho":          (0.75, 0.10),
    "quantum_rho":           (0.90, 0.05),
    "frame_limit_rho":       (0.00, 0.01),
    "lambda_star_amoc":      (0.25, 0.05),   # r=1.0, tanh²(2.2·0.251) ≈ 0.252
    "recovery_time_arctic":  (20.0, 5.00),
}


def r_required(gamma: float, rho_target: float) -> float:
    """Calculate r_domain from an Atlas Ρ target and measured Γ."""
    tanh_sq = float(np.tanh(SIGMA * gamma) ** 2)
    crit = max(1e-10, 1.0 - gamma / GAMMA_MAX)
    return rho_target / (tanh_sq * crit)


ATLAS_R_VALUES: dict[str, dict[str, float | str]] = {
    name: {
        "gamma": gamma,
        "rho_target": rho,
        "r_required": r_required(gamma, rho),
        "status": "estimated",
    }
    for name, (gamma, rho) in _ATLAS_POINTS.items()
}
