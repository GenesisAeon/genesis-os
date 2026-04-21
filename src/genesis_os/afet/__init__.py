"""AFET — Allgemeine Feld-Entropie-Theorie.

Implements local entropy balance with CREP coupling:
    ∂s/∂t + ∇·J_s = σ_s ≥ 0

Dual entropy governance regimes (Feldtheorie v6):
    S∝A (surface/holographic): β ≈ 11  — rigid, climate-scale
    S∝V (volume/life/computation): β ≈ 4.5  — adaptive, informational
"""

from genesis_os.afet.field import AFETField, DualEntropyGovernance, EntropyProductionField

__all__ = ["AFETField", "DualEntropyGovernance", "EntropyProductionField"]
