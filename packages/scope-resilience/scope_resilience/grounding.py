"""Grounding recommender — actionable steps when Ρ_sem is low.

Grounding = injecting verified Sigillin anchors into the LLM context to
raise H_sem and dampen dΓ_sem/dt.
"""

from __future__ import annotations

from scope_resilience.semantic_path import SemanticPath

# Domains known to be highly resilient (used as cross-domain grounding sources)
_RESILIENT_DOMAINS: list[str] = ["quantum-genesis", "sandpile-utac"]


class GroundingRecommender:
    """Produce grounding recommendations based on risk level."""

    def recommend(self, path: SemanticPath, risk_level: str) -> list[str]:
        """Return a list of actionable grounding recommendations."""
        if risk_level == "safe":
            return ["No grounding required."]
        if risk_level == "moderate":
            return [
                f"Inject top Sigillin anchors: {path.sigillin_ids[:3]}",
                "Set Q4 state to most coherent node on path.",
                "Monitor dΓ/dt during conversation.",
            ]
        if risk_level == "high_risk":
            return [
                "Seek alternative path with higher Γ_sem.",
                f"Cross-domain grounding from: "
                f"{self._resilient_cross_domains(path.domain)}",
                "Consider reducing task complexity for this domain.",
            ]
        # critical
        return [
            "WARNING: DO NOT INITIALIZE LLM on this path.",
            "Semantic domain is near phase boundary.",
            f"Suggested alternatives: {self._alternative_paths(path)}",
        ]

    def _resilient_cross_domains(self, domain: str) -> list[str]:
        return [d for d in _RESILIENT_DOMAINS if d != domain]

    def _alternative_paths(self, path: SemanticPath) -> list[str]:
        return [
            f"alt_path_{path.topic}_v2",
            f"alt_path_{path.topic}_v3",
        ]
