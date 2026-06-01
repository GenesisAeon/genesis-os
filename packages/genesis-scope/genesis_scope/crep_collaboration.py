"""CollaborationCREP — CREP tensor reinterpreted for session coherence.

Note: this is a *reinterpretation* of CREP for the collaboration domain.
The original CREP (Criticality, Resonance, Entropy, Persistence) applies to
physical systems. Here the four components are redefined for session context:

    C = Context-continuity   ∈ [0,1]  (0 = blank context, 1 = full continuity)
    R = Reproducibility      ∈ [0,1]  (0 = irreproducible, 1 = exact replay)
    E = Entropy              ∈ [0,1]  (0 = fully determined, 1 = maximally open)
    P = Productivity         ∈ [0,1]  (normalised meaning-units per session)

Gamma_collab = (C * R * E * P) ^ (1/4)

Hypothesis: GenesisAeon sessions operate in the critical regime:
    Gamma_collab ∈ [0.35, 0.55]  (between sandpile and Arctic tipping point)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass
class CollaborationCREP:
    """CREP tensor for Human-AI collaboration sessions.

    Args:
        C: Context-continuity score ∈ [0,1].
        R: Reproducibility score   ∈ [0,1].
        E: Entropy / openness      ∈ [0,1].
        P: Productivity score      ∈ [0,1].
    """

    C: float = 0.7   # reasonable default: good but not perfect continuity
    R: float = 0.6   # medium reproducibility across sessions
    E: float = 0.8   # high openness — collaboration is exploratory
    P: float = 0.5   # medium productivity per session

    def __post_init__(self) -> None:
        for attr in ("C", "R", "E", "P"):
            val = getattr(self, attr)
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"CREP component {attr}={val} must be in [0,1]")

    @property
    def gamma(self) -> float:
        """Gamma_collab = geometric mean of C, R, E, P."""
        product = self.C * self.R * self.E * self.P
        if product <= 0.0:
            return 0.0
        return product ** 0.25

    def regime(self) -> str:
        """Classify collaboration regime by Gamma_collab.

        Collaboration operates at higher Gamma than physical systems because
        human sessions are intentionally exploratory (high E) and contextual (high C).
        Critical regime for collaboration: [0.35, 0.75].
        """
        g = self.gamma
        if g < 0.10:
            return "subcritical"
        if g < 0.35:
            return "pre-critical"
        if g < 0.75:
            return "critical"      # target regime — wider than physical CREP
        if g < 0.90:
            return "super-critical"
        return "saturated"

    def is_critical(self) -> bool:
        return self.regime() == "critical"

    def to_dict(self) -> dict[str, Any]:
        return {
            "C": self.C,
            "R": self.R,
            "E": self.E,
            "P": self.P,
            "gamma": self.gamma,
            "regime": self.regime(),
            "is_critical": self.is_critical(),
        }

    @classmethod
    def from_session_metrics(
        cls,
        context_overlap: float,
        anchor_hit_rate: float,
        topic_diversity: float,
        units_per_hour: float,
        max_units: float = 10.0,
    ) -> "CollaborationCREP":
        """Construct CREP from raw session observables.

        Args:
            context_overlap:  Fraction of previous context reused ∈ [0,1].
            anchor_hit_rate:  Fraction of anchors correctly recalled ∈ [0,1].
            topic_diversity:  Shannon entropy of topics / log(max_topics) ∈ [0,1].
            units_per_hour:   Meaning-units produced per hour (e.g. packages, concepts).
            max_units:        Normalisation factor for productivity.
        """
        P = min(1.0, units_per_hour / max(max_units, 1e-9))
        return cls(
            C=float(context_overlap),
            R=float(anchor_hit_rate),
            E=float(topic_diversity),
            P=float(P),
        )
