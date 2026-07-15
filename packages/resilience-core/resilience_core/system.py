"""ResilienceCore — Diamond Interface (6 methods) for resilience-core.

Package 40 of the GenesisAeon ecosystem.
Implements the domain-agnostic system resilience metric Ρ derived from
UTAC fixed-point analysis and inter-domain coupling effects.
"""

from __future__ import annotations

from typing import Any

from resilience_core.cascade import detect_cascade
from resilience_core.constants import COLLAPSE_THRESHOLD, GAMMA_MAX, SIGMA_PHI
from resilience_core.coupling import CouplingMatrix
from resilience_core.eigenrate import ResilienceEigenrate
from resilience_core.frame_principle import frame_principle_limit
from resilience_core.rho_calculator import ResilienceState, RhoCalculator


class ResilienceCore:
    """Diamond Interface for resilience-core (Package 40).

    Computes Ρ(t) = |λ*(t)| · (1−Γ/Γ_max) · coupling_factor(domain).

    Implements all 6 Diamond methods:
      run_cycle(), get_crep_state(), get_utac_state(),
      get_phase_events(), to_zenodo_record(), get_resilience_state()

    Args:
        domain: Domain name (used as key in the coupling matrix).
        r:      Domain-specific return rate.
        sigma:  CREP coupling constant (universal default 2.2).
    """

    def __init__(
        self,
        domain: str = "generic",
        r: float = 1.0,
        sigma: float = 2.2,
    ) -> None:
        self.domain = domain
        self.eigenrate = ResilienceEigenrate(r=r, sigma=sigma)
        self.coupling = CouplingMatrix()
        self.calculator = RhoCalculator(self.eigenrate, self.coupling)
        self._current_gamma: float | None = None
        self._history: list[ResilienceState] = []

    # ─── Diamond Interface ───────────────────────────────────────────────────

    def run_cycle(
        self,
        gamma: float = 0.251,
        coupling_updates: dict[tuple[str, str], float] | None = None,
    ) -> dict[str, Any]:
        """Run one resilience cycle.

        Args:
            gamma:            Γ value for this cycle (typically from the
                              domain package's get_crep_state()).
            coupling_updates: Optional {(source, target): effect} dict for
                              dynamic coupling registration.

        Returns:
            Dict with rho, lambda_star, criticality_margin, coupling_load,
            near_collapse, and recovery_time.
        """
        if coupling_updates:
            for (src, tgt), effect in coupling_updates.items():
                self.coupling.register_coupling(src, tgt, effect)

        self._current_gamma = gamma
        state = self.calculator.compute(gamma, self.domain)
        self._history.append(state)

        return {
            "rho": state.rho,
            "lambda_star": state.lambda_star,
            "criticality_margin": state.criticality_margin,
            "coupling_load": state.coupling_load,
            "near_collapse": state.near_collapse,
            "recovery_time": self.eigenrate.recovery_time(gamma),
        }

    def get_crep_state(self) -> dict[str, float | None]:
        """CREP representation of the resilience domain.

        Maps resilience quantities onto CREP axes:
          C = criticality margin (buffer to Γ_max)
          R = 1 − coupling_load (coupling stability)
          E = normalised eigenrate (intrinsic return speed)
          P = not-near-collapse flag (0 or 1)
          Gamma = Ρ itself (resilience as CREP output)
        """
        gamma = self._current_gamma
        if gamma is None:
            return {"C": None, "R": None, "E": None, "P": None, "Gamma": None}
        state = self.calculator.compute(gamma, self.domain)
        return {
            "C": state.criticality_margin,
            "R": 1.0 - state.coupling_load,
            "E": state.lambda_star,
            "P": float(not state.near_collapse),
            "Gamma": state.rho,
        }

    def get_utac_state(self) -> dict[str, float]:
        """UTAC state: current Ρ as H, target Ρ as H_star."""
        gamma = self._current_gamma or 0.0
        rho = self.calculator.compute(gamma, self.domain).rho
        return {
            "H": rho,
            "H_star": COLLAPSE_THRESHOLD * 2.0,
            "K_eff": 1.0,
        }

    def get_phase_events(self) -> list[dict[str, Any]]:
        """Return all near-collapse events recorded since instantiation."""
        return [
            {
                "type": "near_collapse",
                "rho": s.rho,
                "coupling_load": s.coupling_load,
            }
            for s in self._history
            if s.near_collapse
        ]

    def to_zenodo_record(self) -> dict[str, Any]:
        """Zenodo metadata record for this resilience-core instance."""
        return {
            "title": (
                f"resilience-core: UTAC-derived system resilience (Ρ) "
                f"for domain '{self.domain}'"
            ),
            "description": (
                "Computes the GenesisAeon system resilience metric Ρ from "
                "UTAC eigenrate analysis and inter-domain coupling effects. "
                "Ρ quantifies a system's buffer capacity against destabilising "
                "perturbations, from physical tipping points to semantic drift."
            ),
            "creators": [
                {"name": "Römer, Johann", "affiliation": "MOR Research Collective"}
            ],
            "communities": [{"identifier": "genesisaeon"}],
            "related_identifiers": [
                {
                    "identifier": "10.5281/zenodo.19645351",
                    "relation": "isPartOf",
                    "scheme": "doi",
                }
            ],
        }

    def get_resilience_state(self) -> dict[str, Any]:
        """6th Diamond method — full resilience state.

        Standard interface for all GenesisAeon packages that import
        resilience-core as an optional dependency.
        """
        gamma = self._current_gamma or 0.0
        state = self.calculator.compute(gamma, self.domain)
        fp = frame_principle_limit(gamma, state.coupling_load)
        cascade = detect_cascade(self.domain, gamma, self.coupling)
        return {
            "rho": state.rho,
            "lambda_star": state.lambda_star,
            "recovery_time": self.eigenrate.recovery_time(gamma),
            "criticality_margin": state.criticality_margin,
            "coupling_load": state.coupling_load,
            "near_collapse": state.near_collapse,
            "frame_principle_warn": fp["frame_principle_warn"],
            "coupling_sources": state.coupling_sources,
            "cascade_risk": cascade["cascade_risk"],
        }
