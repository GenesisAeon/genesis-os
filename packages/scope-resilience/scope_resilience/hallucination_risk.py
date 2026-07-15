"""Hallucination resilience Ρ_sem and risk classification.

Ρ_sem(P, t) = r_sem · tanh²(σ · Γ_sem(P))
            · (1 − Γ_sem(P)/Γ_max)
            · (1 − |dΓ_sem/dt| / Γ̇_critical)

r_sem comes from a DomainProfile — it is NOT a global constant.
"""

from __future__ import annotations

import numpy as np

from scope_resilience.constants import (
    GAMMA_DOT_CRITICAL,
    GAMMA_MAX,
    SIGMA,
)
from scope_resilience.domain_profile import DomainProfile


_RISK_LEVELS: list[tuple[float, float, str, str]] = [
    (0.70, float("inf"), "safe",      "Path is semantically stable. Proceed."),
    (0.40, 0.70,         "moderate",  "Moderate drift risk. Inject grounding anchors."),
    (0.10, 0.40,         "high_risk", "High hallucination risk. Consider alternative path."),
    (0.00, 0.10,         "critical",  "Critical: near semantic phase boundary. "
                                       "Do not initialize on this path."),
]


class HallucinationRisk:
    """Compute Ρ_sem and classify hallucination risk for a semantic path."""

    def compute_rho(
        self,
        gamma_sem: float,
        domain_profile: DomainProfile | None = None,
        r_sem: float | None = None,
        d_gamma_dt: float = 0.0,
    ) -> float:
        """Compute Ρ_sem.

        r_sem is taken from domain_profile if provided; falls back to the
        explicit r_sem kwarg; finally defaults to 1.0 (uncalibrated raw).
        """
        if domain_profile is not None:
            r = domain_profile.r
        elif r_sem is not None:
            r = r_sem
        else:
            r = 1.0

        tanh_term = float(np.tanh(SIGMA * gamma_sem) ** 2)
        crit_term = max(0.0, 1.0 - gamma_sem / GAMMA_MAX)
        drift_term = max(0.0, 1.0 - abs(d_gamma_dt) / GAMMA_DOT_CRITICAL)
        return r * tanh_term * crit_term * drift_term

    def classify_risk(self, rho_sem: float) -> tuple[str, str]:
        """Return (risk_level, message) for a given Ρ_sem."""
        for low, high, level, msg in _RISK_LEVELS:
            if low <= rho_sem < high:
                return level, msg
        return "critical", "Ρ_sem below minimum expected range."
