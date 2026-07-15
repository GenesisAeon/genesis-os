"""Inter-domain coupling matrix C_ij.

C_ij(t) = influence of domain j on dΓ_i/dt at time t.
Positive  → destabilising (increases Γ_i drift rate).
Negative  → stabilising   (dampens Γ_i drift rate).
"""

from __future__ import annotations

from resilience_core.constants import C_CRITICAL, GAMMA_MAX


class CouplingMatrix:
    """Manage coupling effects between GenesisAeon domains.

    Args:
        c_critical: Coupling collapse threshold (default 0.5).
    """

    def __init__(self, c_critical: float = C_CRITICAL) -> None:
        self.c_critical = c_critical
        self._couplings: dict[tuple[str, str], float] = {}

    def register_coupling(
        self,
        source_domain: str,
        target_domain: str,
        effect: float,
    ) -> None:
        """Register a coupling effect.  Positive = destabilising."""
        self._couplings[(source_domain, target_domain)] = effect

    def total_load(self, target_domain: str) -> float:
        """Sum |C_ij| over all sources j → target_domain."""
        return sum(
            abs(v)
            for (src, tgt), v in self._couplings.items()
            if tgt == target_domain
        )

    def coupling_factor(self, target_domain: str) -> float:
        """Return 1 − total_load/C_critical, clamped to [0, 1]."""
        return max(0.0, 1.0 - self.total_load(target_domain) / self.c_critical)

    def cascade_threshold(
        self,
        target_domain: str,
        gamma: float,
        gamma_max: float = GAMMA_MAX,
    ) -> bool:
        """True when cascade-collapse is imminent.

        Condition: coupling load > 50 % of C_critical AND Γ > 95 % of Γ_max.
        """
        load = self.total_load(target_domain)
        return load > self.c_critical * 0.5 and gamma > gamma_max * 0.95

    def sources_for(self, target_domain: str) -> dict[str, float]:
        """Return {source_domain: effect} for all sources of target_domain."""
        return {
            src: effect
            for (src, tgt), effect in self._couplings.items()
            if tgt == target_domain
        }
