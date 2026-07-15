"""System resilience Ρ calculator.

Ρ(t) = |λ*(t)| · (1 − Γ(t)/Γ_max) · coupling_factor(domain)

Calibrated reference values (CREP Atlas):
  AMOC     (Γ=0.251): Ρ_ref ≈ 0.65
  Arctic   (Γ=0.920): Ρ_ref ≈ 0.05  (near collapse)
  Sandpile (Γ=0.296): Ρ_ref ≈ 0.75
  Quantum  (Γ=0.050): Ρ_ref ≈ 0.90
"""

from __future__ import annotations

from dataclasses import dataclass, field

from resilience_core.constants import COLLAPSE_THRESHOLD, GAMMA_MAX, SIGMA_PHI
from resilience_core.coupling import CouplingMatrix
from resilience_core.eigenrate import ResilienceEigenrate


@dataclass
class ResilienceState:
    """Complete resilience snapshot of a UTAC system at time t."""

    rho: float
    lambda_star: float
    criticality_margin: float
    coupling_load: float
    near_collapse: bool
    coupling_sources: dict[str, float] = field(default_factory=dict)


class RhoCalculator:
    """Compute Ρ from eigenrate and coupling matrix.

    Args:
        eigenrate: Pre-constructed ResilienceEigenrate instance.
        coupling:  Pre-constructed CouplingMatrix instance.
        gamma_max: Ceiling Γ (default ERA5 Arctic = 0.920).
    """

    def __init__(
        self,
        eigenrate: ResilienceEigenrate,
        coupling: CouplingMatrix,
        gamma_max: float = GAMMA_MAX,
    ) -> None:
        self.eigenrate = eigenrate
        self.coupling = coupling
        self.gamma_max = gamma_max

    def compute(self, gamma: float, domain: str) -> ResilienceState:
        """Compute the full ResilienceState for a domain at Γ = gamma."""
        lam = self.eigenrate.compute(gamma)
        crit_margin = max(0.0, 1.0 - gamma / self.gamma_max)
        coup_factor = self.coupling.coupling_factor(domain)
        rho = lam * crit_margin * coup_factor

        return ResilienceState(
            rho=rho,
            lambda_star=lam,
            criticality_margin=crit_margin,
            coupling_load=1.0 - coup_factor,
            near_collapse=rho < COLLAPSE_THRESHOLD,
            coupling_sources=self.coupling.sources_for(domain),
        )
