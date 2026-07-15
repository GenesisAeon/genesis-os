"""ScopeResilience — Diamond Interface (6 methods) for scope-resilience.

Package 41 of the GenesisAeon ecosystem.
Extends genesis-scope with hallucination resilience mapping for LLM
semantic paths, using the UTAC framework adapted to semantic coherence.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from scope_resilience.constants import GAMMA_MAX, SIGMA
from scope_resilience.domain_profile import DomainProfile, KNOWN_DOMAIN_PROFILES
from scope_resilience.grounding import GroundingRecommender
from scope_resilience.hallucination_risk import HallucinationRisk
from scope_resilience.llms_txt import LLMSTxtExporter
from scope_resilience.path_monitor import PathDriftMonitor
from scope_resilience.semantic_crep import SemanticCREP
from scope_resilience.semantic_path import SemanticPath


class ScopeResilience:
    """Hallucination-resilience cartography for LLM semantic paths.

    Diamond Interface for Package 41 (scope-resilience).
    Implements all 6 methods: run_cycle, get_crep_state, get_utac_state,
    get_phase_events, to_zenodo_record, get_resilience_state.

    Also exposes get_semantic_path() and to_llms_txt() as high-level
    entry points for LLM initialisation workflows.

    Args:
        domain: Semantic domain name (e.g. "general", "physics_dense").
    """

    def __init__(self, domain: str = "general") -> None:
        self.domain = domain
        self._crep = SemanticCREP()
        self._risk = HallucinationRisk()
        self._grounder = GroundingRecommender()
        self._monitor = PathDriftMonitor()
        self._exporter = LLMSTxtExporter()
        self._current_path: SemanticPath | None = None
        self._domain_profile: DomainProfile | None = KNOWN_DOMAIN_PROFILES.get(domain)

    # ─── Diamond Interface ───────────────────────────────────────────────────

    def run_cycle(
        self,
        topic: str = "",
        sigillin_ids: list[str] | None = None,
        q4_transitions: list[tuple[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Compute hallucination resilience for a semantic path.

        Args:
            topic:          Topic or query string.
            sigillin_ids:   Ordered Sigillin snapshot IDs on the path.
            q4_transitions: Valid Gray-code transitions (src, dst).

        Returns:
            Dict with gamma_sem, rho_sem, risk_level, d_gamma_dt,
            needs_regrounding.
        """
        sigillin_ids = sigillin_ids or []
        q4_transitions = q4_transitions or []

        crep_comps = self._crep.compute(sigillin_ids, q4_transitions, self.domain)
        gamma_sem = self._crep.gamma_sem(crep_comps)
        d_gamma = self._monitor.update(gamma_sem)
        from scope_resilience.semantic_crep import get_domain_r

        rho_sem = self._risk.compute_rho(
            gamma_sem,
            domain_profile=self._domain_profile,
            r_sem=get_domain_r(self.domain) if self._domain_profile is None else None,
            d_gamma_dt=d_gamma,
        )
        risk_level, _ = self._risk.classify_risk(rho_sem)

        placeholder_path = SemanticPath(
            topic=topic,
            sigillin_ids=sigillin_ids,
            q4_transitions=q4_transitions,
            gamma_sem=gamma_sem,
            rho_sem=rho_sem,
            domain=self.domain,
            crep_components=crep_comps,
            risk_level=risk_level,
            grounding_recommendations=[],
        )
        recs = self._grounder.recommend(placeholder_path, risk_level)

        self._current_path = SemanticPath(
            topic=topic,
            sigillin_ids=sigillin_ids,
            q4_transitions=q4_transitions,
            gamma_sem=gamma_sem,
            rho_sem=rho_sem,
            domain=self.domain,
            crep_components=crep_comps,
            risk_level=risk_level,
            grounding_recommendations=recs,
        )

        return {
            "topic": topic,
            "gamma_sem": gamma_sem,
            "rho_sem": rho_sem,
            "risk_level": risk_level,
            "d_gamma_dt": d_gamma,
            "needs_regrounding": self._monitor.needs_regrounding(),
        }

    def get_crep_state(self) -> dict[str, float | None]:
        """Return semantic CREP components plus Gamma."""
        if not self._current_path:
            return {"C": None, "R": None, "E": None, "P": None, "Gamma": None}
        p = self._current_path
        return {**p.crep_components, "Gamma": p.gamma_sem}

    def get_utac_state(self) -> dict[str, float | None]:
        """UTAC state: Ρ_sem as H, coherence attractor as H_star."""
        if not self._current_path:
            return {"H": None, "H_star": None, "K_eff": None}
        rho = self._current_path.rho_sem
        gamma = self._current_path.gamma_sem
        return {
            "H": rho,
            "H_star": float(np.tanh(SIGMA * gamma)),
            "K_eff": 1.0,
        }

    def get_phase_events(self) -> list[dict[str, Any]]:
        """Return list of critical drift events from the current path."""
        if not self._current_path:
            return []
        if self._current_path.risk_level in ("high_risk", "critical"):
            return [
                {
                    "type": "hallucination_risk",
                    "topic": self._current_path.topic,
                    "rho_sem": self._current_path.rho_sem,
                    "risk_level": self._current_path.risk_level,
                }
            ]
        return []

    def to_zenodo_record(self) -> dict[str, Any]:
        """Zenodo metadata record for scope-resilience."""
        return {
            "title": (
                "scope-resilience: Hallucination resilience mapping "
                "for LLM semantic paths"
            ),
            "description": (
                "Extends genesis-scope with hallucination resilience "
                "quantification (Ρ_sem) for semantic paths. Maps UTAC "
                "system dynamics to LLM coherence maintenance, providing "
                "pre-flight risk assessment before LLM initialization on "
                "a semantic path."
            ),
            "creators": [
                {"name": "Römer, Johann", "affiliation": "MOR Research Collective"}
            ],
            "communities": [{"identifier": "genesisaeon"}],
        }

    def get_resilience_state(self) -> dict[str, Any]:
        """6th Diamond method — full semantic resilience state."""
        if not self._current_path:
            return {"rho_sem": None, "risk_level": "unknown", "implemented": True}
        p = self._current_path
        window = self._monitor.window
        d_gamma = (window[-1] - window[-2]) if len(window) >= 2 else 0.0  # noqa: PLR2004
        return {
            "rho_sem": p.rho_sem,
            "gamma_sem": p.gamma_sem,
            "risk_level": p.risk_level,
            "d_gamma_dt": d_gamma,
            "needs_regrounding": self._monitor.needs_regrounding(),
            "grounding_recs": p.grounding_recommendations,
            "implemented": True,
        }

    # ─── High-level LLM workflow helpers ────────────────────────────────────

    def get_semantic_path(
        self,
        topic: str,
        min_rho: float = 0.4,
        sigillin_ids: list[str] | None = None,
        q4_transitions: list[tuple[str, str]] | None = None,
    ) -> SemanticPath:
        """Return the best semantic path for LLM initialisation.

        Computes Ρ_sem for the path and returns it with a risk assessment.
        When Ρ_sem < min_rho the path is still returned but carries a
        risk_level of "high_risk" or "critical" as a signal to the caller.

        Args:
            topic:          Human-readable topic.
            min_rho:        Minimum acceptable resilience (default 0.4).
            sigillin_ids:   Optional explicit Sigillin anchor list.
            q4_transitions: Optional explicit Q4 transition list.

        Returns:
            SemanticPath instance with rho_sem and risk_level populated.
        """
        self.run_cycle(topic, sigillin_ids=sigillin_ids, q4_transitions=q4_transitions)
        return self._current_path  # type: ignore[return-value]

    def to_llms_txt(self, topic: str | None = None) -> str:
        """Export the current semantic path as an llms.txt string.

        If no path has been computed yet, runs a cycle for the given topic.
        """
        if not self._current_path:
            if topic:
                self.run_cycle(topic)
            else:
                return "# No semantic path computed yet."
        return self._exporter.export(self._current_path)  # type: ignore[arg-type]
