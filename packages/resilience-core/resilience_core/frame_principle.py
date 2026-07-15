"""Frame-Principle boundary analysis.

σ_Φ ≈ 1/16 = 0.0625 marks the last buffer before total stability loss.
Ρ → 0 when Γ → 1 − σ_Φ ≈ 0.9375 AND C_ij → C_critical simultaneously.
"""

from __future__ import annotations

from resilience_core.constants import GAMMA_MAX, SIGMA_PHI


def frame_principle_limit(gamma: float, coupling_load: float) -> dict[str, float | bool]:
    """Evaluate proximity to the Frame-Principle boundary.

    Args:
        gamma:         Current CREP Γ value.
        coupling_load: Normalised coupling load Σ|C_ij|/C_critical ∈ [0, 1].

    Returns:
        Dict with distance metrics and a boolean warning flag.
    """
    gamma_boundary = 1.0 - SIGMA_PHI  # ≈ 0.9375
    gamma_distance = max(0.0, gamma_boundary - gamma)
    coupling_distance = max(0.0, 1.0 - coupling_load)

    # Joint proximity: both must approach their limits for cascade collapse
    joint_proximity = (1.0 - gamma_distance / gamma_boundary) * coupling_load
    warn = gamma > GAMMA_MAX * 0.95 and coupling_load > 0.5  # noqa: PLR2004

    return {
        "sigma_phi": SIGMA_PHI,
        "gamma_boundary": gamma_boundary,
        "gamma_distance_to_boundary": gamma_distance,
        "coupling_distance_to_critical": coupling_distance,
        "joint_proximity": joint_proximity,
        "frame_principle_warn": warn,
    }
