"""UTAC eigenrate: local return rate at the fixed point.

λ*(t) = −r · tanh²(σ · Γ(t))

Physical meaning: how fast a system recovers from a small perturbation.
Pimm (1984) engineering resilience: τ_recovery ≈ 1/|λ*|.
"""

from __future__ import annotations

import math

import numpy as np

from resilience_core.constants import SIGMA


class ResilienceEigenrate:
    """Compute the local return rate |λ*| at the UTAC fixed point.

    Args:
        r:     Domain-specific return rate (the only free parameter per domain).
        sigma: CREP coupling constant (default 2.2, universal).
    """

    def __init__(self, r: float = 1.0, sigma: float = SIGMA) -> None:
        self.r = r
        self.sigma = sigma

    def compute(self, gamma: float) -> float:
        """Return |λ*| = r · tanh²(σΓ).  Always ≥ 0."""
        if gamma is None or math.isnan(gamma):
            return 0.0
        return self.r * float(np.tanh(self.sigma * gamma) ** 2)

    def recovery_time(self, gamma: float) -> float:
        """Return τ_recovery ≈ 1/|λ*| in system time units (∞ when λ*→0)."""
        lam = self.compute(gamma)
        return 1.0 / lam if lam > 1e-10 else float("inf")
