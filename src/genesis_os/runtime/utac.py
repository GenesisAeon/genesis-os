"""UTAC-Logistic equation for entropy evolution.

The Unified Transition Adaptive Coupling (UTAC) logistic model governs how
entropy H evolves as a function of the CREP coupling term Γ:

.. math::
    \\frac{dH}{dt} = r H \\left(1 - \\frac{H}{K}\\right) \\tanh(\\sigma \\Gamma)

A forward-Euler step of size ``dt=1`` is used by default.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class UTACLogistic:
    """UTAC-Logistic entropy evolution model.

    Args:
        r: Logistic growth rate (default 0.3).
        K: Carrying capacity for entropy (default 1.0).
        sigma: Sensitivity of growth to the CREP coupling Γ (default 2.0).
        dt: Integration step size (default 1.0).
    """

    r: float = 0.3
    K: float = 1.0
    sigma: float = 2.0
    dt: float = 1.0
    _t: float = field(default=0.0, init=False)

    def step(self, entropy: float, gamma: float) -> float:
        """Advance entropy by one UTAC-Logistic step.

        .. math::
            H_{t+1} = H_t + r H_t \\left(1 - \\frac{H_t}{K}\\right)
                      \\tanh(\\sigma \\Gamma) \\cdot \\Delta t

        Args:
            entropy: Current entropy level H_t ∈ [0, K].
            gamma: CREP coupling value Γ.

        Returns:
            Updated entropy H_{t+1} clamped to [0.0, K].
        """
        h = max(0.0, min(entropy, self.K))
        dh_dt = self.r * h * (1.0 - h / self.K) * math.tanh(self.sigma * gamma)
        h_new = h + dh_dt * self.dt
        self._t += self.dt
        return float(max(0.0, min(h_new, self.K)))

    @property
    def t(self) -> float:
        """Current integration time."""
        return self._t

    def reset(self) -> None:
        """Reset integration time to zero."""
        self._t = 0.0

    def equilibrium(self, gamma: float) -> float:
        """Compute the non-trivial equilibrium entropy for given Γ.

        At equilibrium dH/dt=0; for H≠0: H* = K (when tanh(σΓ) ≠ 0 the
        equilibrium depends on the sign of the coupling).

        Args:
            gamma: CREP coupling value.

        Returns:
            Equilibrium entropy H* (K for positive Γ, 0 for negative Γ).
        """
        if math.tanh(self.sigma * gamma) > 0:
            return self.K
        if math.tanh(self.sigma * gamma) < 0:
            return 0.0
        # gamma == 0: no change
        return self.K / 2.0
