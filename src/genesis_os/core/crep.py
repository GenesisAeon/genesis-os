"""CREP evaluation engine: Coherence, Resonance, Emergence, Poetics.

The CREP framework evaluates system states across four orthogonal axes:
- **C** (Coherence): structural integrity and self-consistency of the system
- **R** (Resonance): coupling strength between subsystems and external fields
- **E** (Emergence): complexity arising from low-level interactions
- **P** (Poetics): symbolic density and meaning-richness of state configurations

The CREP score drives phase transitions via:

.. math::
    \\Gamma(C, R, E, P) = \\frac{C \\cdot R + E \\cdot P}{2} \\cdot
    \\exp\\left(-\\frac{(1 - C)^2}{2\\sigma_C^2}\\right)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from pydantic import BaseModel, Field, field_validator


class CREPScore(BaseModel):
    """Immutable CREP score snapshot.

    Attributes:
        coherence: Structural integrity score [0.0, 1.0].
        resonance: Coupling strength score [0.0, 1.0].
        emergence: Complexity score [0.0, 1.0].
        poetics: Symbolic density score [0.0, 1.0].
        timestamp: Cycle index when this score was computed.
    """

    coherence: float = Field(ge=0.0, le=1.0, description="Coherence C ∈ [0,1]")
    resonance: float = Field(ge=0.0, le=1.0, description="Resonance R ∈ [0,1]")
    emergence: float = Field(ge=0.0, le=1.0, description="Emergence E ∈ [0,1]")
    poetics: float = Field(ge=0.0, le=1.0, description="Poetics P ∈ [0,1]")
    timestamp: int = Field(default=0, ge=0, description="Cycle index")

    @field_validator("coherence", "resonance", "emergence", "poetics", mode="before")
    @classmethod
    def clamp_to_unit_interval(cls, v: float) -> float:
        """Clamp value to [0, 1]."""
        return float(np.clip(float(v), 0.0, 1.0))

    @property
    def gamma(self) -> float:
        """CREP coupling term Γ(C,R,E,P).

        .. math::
            \\Gamma = \\frac{C \\cdot R + E \\cdot P}{2} \\cdot
            \\exp\\left(-\\frac{(1-C)^2}{2\\sigma_C^2}\\right)
        """
        sigma_c = 0.3
        base = (self.coherence * self.resonance + self.emergence * self.poetics) / 2.0
        coherence_weight = math.exp(-((1.0 - self.coherence) ** 2) / (2.0 * sigma_c**2))
        return base * coherence_weight

    @property
    def mean(self) -> float:
        """Arithmetic mean of all four CREP components."""
        return (self.coherence + self.resonance + self.emergence + self.poetics) / 4.0

    @property
    def dominant(self) -> str:
        """Return the dominant CREP axis label."""
        scores = {
            "C": self.coherence,
            "R": self.resonance,
            "E": self.emergence,
            "P": self.poetics,
        }
        return max(scores, key=lambda k: scores[k])

    def to_vector(self) -> np.ndarray:
        """Return CREP as a 4-dimensional numpy array."""
        return np.array([self.coherence, self.resonance, self.emergence, self.poetics])

    def __add__(self, other: CREPScore) -> CREPScore:
        """Element-wise addition clamped to [0,1]."""
        return CREPScore(
            coherence=min(1.0, self.coherence + other.coherence),
            resonance=min(1.0, self.resonance + other.resonance),
            emergence=min(1.0, self.emergence + other.emergence),
            poetics=min(1.0, self.poetics + other.poetics),
            timestamp=max(self.timestamp, other.timestamp),
        )

    def __mul__(self, scalar: float) -> CREPScore:
        """Scale all components by a scalar."""
        return CREPScore(
            coherence=self.coherence * scalar,
            resonance=self.resonance * scalar,
            emergence=self.emergence * scalar,
            poetics=self.poetics * scalar,
            timestamp=self.timestamp,
        )


@dataclass
class CREPEvaluator:
    """Evaluates and updates CREP scores from system state dictionaries.

    The evaluator maintains a history of scores and provides methods for
    computing derivatives and detecting phase-relevant thresholds.

    Args:
        sigma_c: Standard deviation for coherence weighting (default 0.3).
        learning_rate: Step size for gradient updates (default 0.05).
        history_length: Maximum number of historical scores retained.
    """

    sigma_c: float = 0.3
    learning_rate: float = 0.05
    history_length: int = 100
    _history: list[CREPScore] = field(default_factory=list, init=False, repr=False)

    def evaluate(self, state: dict[str, Any]) -> CREPScore:
        """Compute a CREPScore from a raw state dictionary.

        Expected keys (all optional, default 0.5):
        - ``coherence``, ``resonance``, ``emergence``, ``poetics``
        - ``entropy``: mapped to (1 - entropy) for coherence weighting
        - ``coupling``: forwarded to resonance

        Args:
            state: Dictionary containing state variables.

        Returns:
            CREPScore snapshot for the given state.
        """
        entropy = float(state.get("entropy", 0.5))
        coupling = float(state.get("coupling", 0.5))

        coherence = float(state.get("coherence", 1.0 - entropy))
        resonance = float(state.get("resonance", coupling))
        emergence = float(state.get("emergence", 0.5))
        poetics = float(state.get("poetics", 0.5))

        cycle = int(state.get("cycle", len(self._history)))
        score = CREPScore(
            coherence=coherence,
            resonance=resonance,
            emergence=emergence,
            poetics=poetics,
            timestamp=cycle,
        )
        self._history.append(score)
        if len(self._history) > self.history_length:
            self._history.pop(0)
        return score

    def gradient(self) -> np.ndarray | None:
        """Return the finite-difference gradient of the CREP vector over time.

        Returns:
            A 4-element array ``[dC/dt, dR/dt, dE/dt, dP/dt]`` or ``None``
            if fewer than two data points exist.
        """
        if len(self._history) < 2:
            return None
        prev = self._history[-2].to_vector()
        curr = self._history[-1].to_vector()
        return curr - prev

    def threshold_exceeded(self, score: CREPScore, threshold: float = 0.6) -> bool:
        """Return True if the gamma coupling term exceeds the given threshold.

        Args:
            score: CREP score to test.
            threshold: Coupling threshold for phase-transition trigger.

        Returns:
            Whether the threshold is exceeded.
        """
        return score.gamma >= threshold

    def weighted_average(
        self, weights: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    ) -> float:
        """Compute the weighted average of the last recorded CREP score.

        Args:
            weights: Tuple of (w_C, w_R, w_E, w_P).

        Returns:
            Weighted mean score, or 0.0 if no history exists.
        """
        if not self._history:
            return 0.0
        last = self._history[-1]
        w_total = sum(weights)
        if w_total == 0.0:
            return 0.0
        return (
            last.coherence * weights[0]
            + last.resonance * weights[1]
            + last.emergence * weights[2]
            + last.poetics * weights[3]
        ) / w_total

    @property
    def history(self) -> list[CREPScore]:
        """Return a copy of the score history."""
        return list(self._history)

    def reset(self) -> None:
        """Clear the score history."""
        self._history.clear()
