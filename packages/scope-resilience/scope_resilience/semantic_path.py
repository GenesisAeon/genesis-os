"""SemanticPath — primary data structure for scope-resilience."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SemanticPath:
    """A semantic path through the GenesisAeon knowledge space.

    Consists of a sequence of Sigillin state anchors connected via valid
    Q4 transitions, with CREP coherence as the quality metric.

    Attributes:
        topic:                   Human-readable topic label.
        sigillin_ids:            Ordered Sigillin snapshot IDs on the path.
        q4_transitions:          Valid Gray-code transitions (src, dst).
        gamma_sem:               CREP Γ of the path.
        rho_sem:                 Hallucination resilience of the path.
        domain:                  Semantic domain (e.g. "oceanography").
        crep_components:         Raw C, R, E, P values.
        risk_level:              "safe" / "moderate" / "high_risk" / "critical".
        grounding_recommendations: Actionable grounding steps.
    """

    topic: str
    sigillin_ids: list[str] = field(default_factory=list)
    q4_transitions: list[tuple[str, str]] = field(default_factory=list)
    gamma_sem: float = 0.0
    rho_sem: float = 0.0
    domain: str = "general"
    crep_components: dict[str, float] = field(default_factory=dict)
    risk_level: str = "unknown"
    grounding_recommendations: list[str] = field(default_factory=list)
