"""PathDriftMonitor — live dΓ_sem/dt monitoring over a sliding window."""

from __future__ import annotations

from scope_resilience.constants import DRIFT_WINDOW_DEFAULT, GAMMA_DOT_CRITICAL


class PathDriftMonitor:
    """Monitor Γ_sem changes across conversation steps.

    At each step the new Γ_sem is appended.  The drift rate is the
    difference between the two most recent values.  When |Δ| exceeds
    GAMMA_DOT_CRITICAL a re-grounding is recommended.

    Args:
        window_size: Number of steps to retain (default 5).
    """

    def __init__(self, window_size: int = DRIFT_WINDOW_DEFAULT) -> None:
        self.window_size = window_size
        self.window: list[float] = []

    def update(self, gamma_sem: float) -> float:
        """Append new Γ_sem and return the current dΓ/dt."""
        self.window.append(gamma_sem)
        if len(self.window) > self.window_size:
            self.window.pop(0)
        if len(self.window) < 2:  # noqa: PLR2004
            return 0.0
        return self.window[-1] - self.window[-2]

    def needs_regrounding(self) -> bool:
        """True when the last step's drift exceeds the critical threshold."""
        if len(self.window) < 2:  # noqa: PLR2004
            return False
        return abs(self.window[-1] - self.window[-2]) > GAMMA_DOT_CRITICAL

    def reset(self) -> None:
        """Clear the drift window (e.g. after a re-grounding event)."""
        self.window.clear()
