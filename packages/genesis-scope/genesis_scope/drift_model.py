"""DriftModel — ODE for semantic drift in Human-AI collaboration space.

Multiplicative form — anchors reduce the effective drift rate:
    dD/dt = (kappa - lambda_ * A_avg) * D

    Without anchors (A_avg = 0): dD/dt = kappa * D  → exponential divergence
    With sufficient anchors:     kappa < lambda_ * A_avg → D → 0 (stable)

Stability condition: lambda_ * A_avg > kappa
i.e. anchor damping overcomes drift rate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from genesis_scope.constants import KAPPA_DEFAULT, LAMBDA_DEFAULT
from genesis_scope.semantic_anchor import SemanticAnchor


@dataclass
class DriftModel:
    """ODE model for semantic drift with Sigillin damping.

    Args:
        kappa:    Drift rate (divergence per session without anchors).
        lambda_:  Anchor damping coefficient.
        d0:       Initial drift amplitude.
    """

    kappa: float = KAPPA_DEFAULT
    lambda_: float = LAMBDA_DEFAULT
    d0: float = 1.0

    _anchors: list[SemanticAnchor] = field(default_factory=list, init=False)

    def add_anchor(self, anchor: SemanticAnchor) -> None:
        self._anchors.append(anchor)

    def anchor_strength(self) -> float:
        """Effective anchor damping A_avg ∈ [0, 1] — normalised by tanh.

        Each anchor contributes tanh(compression_ratio / 10) to A_avg.
        """
        if not self._anchors:
            return 0.0
        import math
        strengths = [math.tanh(a.compression_ratio() / 10.0) for a in self._anchors]
        return sum(strengths) / len(strengths)

    def fixed_point(self) -> float:
        """Effective drift rate: kappa - lambda_ * A_avg.

        Negative = stable (drift decays). Positive = unstable (drift grows).
        """
        return self.kappa - self.lambda_ * self.anchor_strength()

    def simulate(self, n_sessions: int = 38) -> np.ndarray:
        """Simulate drift trajectory over n_sessions using Euler integration.

        Returns:
            Array of shape (n_sessions,) with D(t) values.
        """
        dt = 1.0  # one session = one time step
        trajectory = np.zeros(n_sessions)
        d = self.d0
        eff_rate = self.fixed_point()

        for i in range(n_sessions):
            trajectory[i] = d
            d = max(0.0, d + eff_rate * d * dt)

        return trajectory

    def is_stable(self) -> bool:
        """Returns True if lambda_ * A_avg > kappa (drift decays to 0)."""
        return self.fixed_point() < 0.0

    def sessions_to_stable(self, tolerance: float = 0.05) -> int:
        """Estimate sessions until D(t) / D0 < tolerance (stable means near-zero)."""
        if not self.is_stable():
            return -1  # never converges
        traj = self.simulate(n_sessions=200)
        for i, d in enumerate(traj):
            if d / max(self.d0, 1e-9) < tolerance:
                return i
        return -1

    def summary(self) -> dict[str, float]:
        return {
            "kappa": self.kappa,
            "lambda_": self.lambda_,
            "d0": self.d0,
            "n_anchors": float(len(self._anchors)),
            "anchor_strength": self.anchor_strength(),
            "fixed_point": self.fixed_point(),
            "is_stable": float(self.is_stable()),
            "sessions_to_stable": float(self.sessions_to_stable()),
        }
