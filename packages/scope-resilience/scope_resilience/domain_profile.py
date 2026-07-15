"""DomainProfile — domain-specific UTAC parameter container.

r is the only free parameter per domain; all other quantities are either
universal constants or measured values.  r_required = Ρ_target /
(tanh²(σ·Γ) · (1 − Γ/Γ_max)).
"""

from __future__ import annotations

import numpy as np

from scope_resilience.constants import GAMMA_MAX, SIGMA


class DomainProfile:
    """Encapsulates the domain fingerprint r and its calibration provenance.

    Args:
        domain:           Domain identifier string.
        gamma:            Representative Γ for the domain.
        r:                Return rate (the single free parameter).
        r_status:         "calibrated" | "estimated" | "open".
        r_source:         Human-readable provenance description.
        rho_atlas_target: Target Ρ the r value was derived from (optional).
    """

    def __init__(
        self,
        domain: str,
        gamma: float,
        r: float = 1.0,
        r_status: str = "open",
        r_source: str = "default",
        rho_atlas_target: float | None = None,
    ) -> None:
        self.domain = domain
        self.gamma = gamma
        self.r = r
        self.r_status = r_status
        self.r_source = r_source
        self.rho_atlas_target = rho_atlas_target

    @classmethod
    def from_atlas_target(
        cls,
        domain: str,
        gamma: float,
        rho_target: float,
        sigma: float = SIGMA,
        gamma_max: float = GAMMA_MAX,
    ) -> "DomainProfile":
        """Derive r analytically from an Atlas Ρ target.

        r_required = Ρ_target / (tanh²(σ·Γ) · (1 − Γ/Γ_max))

        Status is set to "estimated" (no real time-series fit yet).
        """
        tanh_sq = float(np.tanh(sigma * gamma) ** 2)
        crit = max(1e-10, 1.0 - gamma / gamma_max)
        r_required = rho_target / (tanh_sq * crit)
        return cls(
            domain=domain,
            gamma=gamma,
            r=r_required,
            r_status="estimated",
            r_source=f"analytical from Ρ_atlas={rho_target}",
            rho_atlas_target=rho_target,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "domain": self.domain,
            "gamma": self.gamma,
            "r": self.r,
            "r_status": self.r_status,
            "r_source": self.r_source,
            "rho_atlas_target": self.rho_atlas_target,
        }


# Known calibration profiles (analytical, all status="estimated").
# Promoted to "calibrated" once real time-series data is available from P49/TIP.
KNOWN_DOMAIN_PROFILES: dict[str, DomainProfile] = {
    "amoc":        DomainProfile.from_atlas_target("amoc",    0.251, 0.65),
    "arctic_era5": DomainProfile.from_atlas_target("arctic",  0.920, 0.05),
    "sandpile":    DomainProfile.from_atlas_target("sandpile", 0.296, 0.75),
    "quantum":     DomainProfile.from_atlas_target("quantum", 0.050, 0.90),
    # Semantic domains — pending P49/TIP calibration:
    "llm_physics": DomainProfile(
        "llm_physics", gamma=0.65, r=2.5,
        r_status="estimated", r_source="expert estimate, pending TIP",
    ),
    "llm_fringe": DomainProfile(
        "llm_fringe", gamma=0.20, r=0.9,
        r_status="estimated", r_source="expert estimate, pending TIP",
    ),
}
