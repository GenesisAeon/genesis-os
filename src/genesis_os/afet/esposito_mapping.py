"""Esposito-Van den Broeck → CREP-Mapping.

Esposito-Zerlegung der Entropieproduktion:
    σ_total = σ_maint + σ_reorg

    σ_maint: Erhaltungsentropie — Aufrechterhaltung des Systemzustands
    σ_reorg: Reorganisationsentropie — Entstehung neuer Strukturen

CREP-Mapping (physikalisch motiviert):
    σ_maint ↔ C (Coherence): Erhaltung kohärenter Muster
    σ_reorg ↔ E (Emergence): Reorganisation zu neuen Strukturen

    Normierung: C_esposito = σ_maint / σ_total
                E_esposito = σ_reorg / σ_total
"""

from __future__ import annotations

from dataclasses import dataclass

from genesis_os.core.crep import CREPScore

_EPSILON: float = 1e-12


@dataclass
class EspositoDecomposition:
    """Zerlegung der Entropieproduktion nach Esposito-Van den Broeck.

    Attributes:
        sigma_maint: Erhaltungsentropie [J/(K·s)].
        sigma_reorg: Reorganisationsentropie [J/(K·s)].
        sigma_total: Gesamtentropieproduktion.
    """

    sigma_maint: float
    sigma_reorg: float

    @property
    def sigma_total(self) -> float:
        """Gesamtentropieproduktion."""
        return self.sigma_maint + self.sigma_reorg

    @property
    def c_esposito(self) -> float:
        """Kohärenz-Proxy aus Erhaltungsentropie: σ_maint / σ_total."""
        return self.sigma_maint / max(self.sigma_total, _EPSILON)

    @property
    def e_esposito(self) -> float:
        """Emergenz-Proxy aus Reorganisationsentropie: σ_reorg / σ_total."""
        return self.sigma_reorg / max(self.sigma_total, _EPSILON)


def map_to_crep(
    decomp: EspositoDecomposition,
    crep: CREPScore,
    blend_weight: float = 0.3,
) -> dict[str, float]:
    """Mischt Esposito-Metriken als CREP-Korrekturfaktoren ein.

    Args:
        decomp: Esposito-Zerlegung der Entropieproduktion.
        crep: Bestehender CREP-Score.
        blend_weight: Gewicht des Esposito-Anteils (default 0.3).

    Returns:
        Dict mit ``C_esposito``, ``E_esposito``, ``C_corrected``, ``E_corrected``.
    """
    w = float(max(0.0, min(1.0, blend_weight)))
    return {
        "C_esposito": decomp.c_esposito,
        "E_esposito": decomp.e_esposito,
        "C_corrected": (1.0 - w) * crep.coherence + w * decomp.c_esposito,
        "E_corrected": (1.0 - w) * crep.emergence + w * decomp.e_esposito,
        "sigma_maint": decomp.sigma_maint,
        "sigma_reorg": decomp.sigma_reorg,
        "sigma_total": decomp.sigma_total,
    }
