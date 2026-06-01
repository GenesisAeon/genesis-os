"""SessionTracker — trajectory through (tau_A, tau_H, Sigma) coordinate space.

Three coordinate axes of the shared Human-AI space:
    tau_A  : Action-time  — LLM operation time (atemporal, discrete steps)
    tau_H  : Human-time   — continuous, integrating experience stream
    Sigma  : Semantic density — information content of the current context

Each session is a point P_i = (tau_A_i, tau_H_i, Sigma_i).
The sequence P_1, ..., P_n is the collaboration history.

The Fisher-Rao velocity in this space:
    v_collab(t) = sqrt(g_ij * theta_dot_i * theta_dot_j)

Warning threshold: v_collab > v_RIG (≈ 1352 km/s normalised) signals drift.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from genesis_scope.constants import V_RIG_KM_S


@dataclass
class SessionPoint:
    """A single session as a point in scope-space."""

    session_id: str
    tau_a: float          # LLM steps (e.g. tool calls + completions)
    tau_h: float          # Human time in hours
    sigma: float          # Semantic density ∈ [0, 1]
    gamma_collab: float   # CREP collaboration value at this session
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class SessionTracker:
    """Tracks collaboration sessions as trajectories in scope-space.

    Args:
        v_rig_threshold:  Normalised v_RIG warning threshold (default 1.0,
                          representing the natural unit v_RIG = 1352 km/s).
    """

    def __init__(self, v_rig_threshold: float = 1.0) -> None:
        self._sessions: list[SessionPoint] = []
        self.v_rig_threshold = v_rig_threshold

    def record(self, session: SessionPoint) -> None:
        """Add a session point to the trajectory."""
        self._sessions.append(session)

    def trajectory(self) -> list[SessionPoint]:
        return list(self._sessions)

    def velocity(self) -> float:
        """Fisher-Rao velocity between the two most recent sessions.

        Uses Euclidean approximation in (tau_A, tau_H, Sigma) space,
        normalised so that v_RIG = 1.0 corresponds to the warning threshold.
        """
        if len(self._sessions) < 2:
            return 0.0
        p1 = self._sessions[-2]
        p2 = self._sessions[-1]
        dt = max(p2.tau_h - p1.tau_h, 1e-9)  # hours

        d_tau_a = (p2.tau_a - p1.tau_a) / max(p1.tau_a, 1.0)
        d_sigma = p2.sigma - p1.sigma
        d_gamma = p2.gamma_collab - p1.gamma_collab

        # Fisher-Rao metric approximation: diagonal g_ij = 1/component^2
        v = math.sqrt(d_tau_a**2 + d_sigma**2 + d_gamma**2) / dt
        return v

    def is_drifting(self) -> bool:
        """Returns True when v_collab exceeds v_RIG threshold."""
        return self.velocity() > self.v_rig_threshold

    def status(self) -> str:
        """'stable' | 'drifting' | 'anchored' | 'insufficient_data'."""
        if len(self._sessions) < 2:
            return "insufficient_data"
        v = self.velocity()
        if v > self.v_rig_threshold:
            return "drifting"
        if v < self.v_rig_threshold * 0.3:
            return "anchored"
        return "stable"

    def gamma_trajectory(self) -> np.ndarray:
        """Returns array of gamma_collab values across all sessions."""
        return np.array([s.gamma_collab for s in self._sessions])

    def sigma_trajectory(self) -> np.ndarray:
        """Returns array of semantic density values across all sessions."""
        return np.array([s.sigma for s in self._sessions])

    def summary(self) -> dict[str, Any]:
        n = len(self._sessions)
        gammas = self.gamma_trajectory()
        return {
            "n_sessions": n,
            "velocity": round(self.velocity(), 4),
            "status": self.status(),
            "gamma_mean": float(gammas.mean()) if n > 0 else None,
            "gamma_last": float(gammas[-1]) if n > 0 else None,
            "v_rig_threshold": self.v_rig_threshold,
            "v_rig_km_s": V_RIG_KM_S,
        }

    @classmethod
    def from_package_history(cls, package_ids: list[int]) -> "SessionTracker":
        """Bootstrap tracker from P17–P39 development history.

        Each package represents one major session in the collaboration.
        Semantic density grows with package number (more context built up).
        """
        tracker = cls()
        base_time = 0.0

        for i, pid in enumerate(package_ids):
            # Semantic density grows logistically with package count
            sigma = 1.0 / (1.0 + math.exp(-0.2 * (i - 11)))
            # gamma estimated from CREP spectrum (critical regime grows)
            gamma = 0.35 + 0.20 * (i / len(package_ids))

            tracker.record(SessionPoint(
                session_id=f"P{pid}",
                tau_a=float(50 + i * 30),       # ~50-1200 tool calls total
                tau_h=base_time + float(i * 2.5),  # ~2.5 hours per package session
                sigma=sigma,
                gamma_collab=gamma,
                metadata={"package_id": pid},
            ))
        return tracker
