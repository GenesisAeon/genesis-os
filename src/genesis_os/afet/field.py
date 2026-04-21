"""AFET field module — local entropy balance and dual governance detection.

Implements the Allgemeine Feld-Entropie-Theorie as derived from
Feldtheorie's Entropy_in_Climate module.

Core equation (local entropy balance):
    ∂s/∂t + ∇·J_s = σ_s ≥ 0

CREP-coupled entropy production:
    σ_s(x,t) = σ_0 · (1 + κ · Γ(C,R,E,P))

β-reduction under local dissipation (Feldtheorie β-reduction):
    β_eff = β_global / (1 + σ_local / σ_critical)

Dual entropy governance (Feldtheorie v6):
    S∝A (surface, rigid):   β ≈ 11  — climate, holographic, area-law
    S∝V (volume, adaptive): β ≈ 4.5 — life, computation, volume-law

The S∝A → S∝V phase transition marks the origin of adaptive complexity
(emergence of life, self-organization).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np


# ---------------------------------------------------------------------------
# Constants (from Feldtheorie empirical analysis)
# ---------------------------------------------------------------------------

BETA_SURFACE: float = 11.0   # S∝A governance threshold (climate β)
BETA_VOLUME: float = 4.5     # S∝V governance threshold (informational β)
BETA_BOUNDARY: float = (BETA_SURFACE + BETA_VOLUME) / 2.0  # ≈ 7.75


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EntropyProductionField:
    """Snapshot of a local entropy production computation.

    Attributes:
        sigma_local: Local entropy production rate σ_s ≥ 0.
        sigma_crep: CREP-enhanced production rate σ_0·(1 + κ·Γ).
        beta_eff: Effective β after reduction by local dissipation.
        regime: Detected governance regime ("surface" or "volume").
        gamma: CREP coupling value used in this computation.
        kappa: CREP-entropy coupling constant used.
    """

    sigma_local: float
    sigma_crep: float
    beta_eff: float
    regime: Literal["surface", "volume"]
    gamma: float
    kappa: float


@dataclass(frozen=True)
class DualEntropyGovernance:
    """Result of dual entropy regime analysis.

    Attributes:
        regime: Current governance regime.
        beta_eff: Effective β value at transition point.
        transition_detected: True if S∝A→S∝V transition was found.
        transition_index: Time-series index of the transition (or -1).
        confidence: Detection confidence ∈ [0, 1].
    """

    regime: Literal["surface", "volume"]
    beta_eff: float
    transition_detected: bool
    transition_index: int
    confidence: float


# ---------------------------------------------------------------------------
# AFETField
# ---------------------------------------------------------------------------


@dataclass
class AFETField:
    """Allgemeine Feld-Entropie-Theorie (AFET) implementation.

    Implements local entropy balance with CREP coupling and β-reduction.

    Args:
        sigma_0: Baseline entropy production rate (default 1.0).
        sigma_critical: Critical dissipation for β-reduction (default 1.0).
        beta_surface: β threshold for S∝A regime (default 11.0).
        beta_volume: β threshold for S∝V regime (default 4.5).
    """

    sigma_0: float = 1.0
    sigma_critical: float = 1.0
    beta_surface: float = BETA_SURFACE
    beta_volume: float = BETA_VOLUME
    _production_history: list[float] = field(
        default_factory=list, init=False, repr=False
    )

    def compute_local_entropy_production(
        self,
        state: float,
        crep_gamma: float,
        kappa: float = 1.0,
    ) -> float:
        """Compute CREP-coupled local entropy production σ_s.

        .. math::
            \\sigma_s = \\sigma_0 \\cdot (1 + \\kappa \\cdot \\Gamma)

        Entropy production is always non-negative (second law).

        Args:
            state: Current system state (used to scale baseline σ_0).
            crep_gamma: CREP coupling Γ ∈ [0, 1].
            kappa: CREP-entropy coupling constant (default 1.0).

        Returns:
            σ_s ≥ 0.
        """
        sigma_s = self.sigma_0 * (1.0 + kappa * abs(crep_gamma))
        result = float(max(0.0, sigma_s * abs(state)))
        self._production_history.append(result)
        return result

    def compute_entropy_flux(
        self,
        state: np.ndarray,
        gradient: np.ndarray,
    ) -> np.ndarray:
        """Compute the entropy flux vector J_s = -λ · ∇s.

        Uses Fourier-like diffusive flux:
            J_s = -σ_0 · ∇s

        Args:
            state: State vector at each spatial point.
            gradient: Spatial gradient ∇s (same shape as state).

        Returns:
            Entropy flux vector (same shape as gradient).
        """
        return np.asarray(-self.sigma_0 * np.asarray(gradient), dtype=float)

    def detect_governance_regime(
        self, beta_eff: float
    ) -> Literal["surface", "volume"]:
        """Classify the entropy governance regime from effective β.

        Uses the midpoint boundary between β_surface and β_volume:
            β > boundary → "surface" (S∝A, rigid, holographic)
            β ≤ boundary → "volume" (S∝V, adaptive, life/computation)

        Args:
            beta_eff: Effective logistic steepness parameter.

        Returns:
            ``"surface"`` or ``"volume"``.
        """
        boundary = (self.beta_surface + self.beta_volume) / 2.0
        return "surface" if beta_eff > boundary else "volume"

    def beta_reduction_formula(
        self,
        beta_global: float,
        sigma_local: float,
        sigma_critical: float | None = None,
    ) -> float:
        """Apply the Feldtheorie β-reduction mechanism.

        Local dissipation reduces the effective steepness:

        .. math::
            \\beta_{\\text{eff}} = \\frac{\\beta_{\\text{global}}}{1 + \\sigma_{\\text{local}} / \\sigma_{\\text{critical}}}

        Args:
            beta_global: Global (domain-level) β steepness.
            sigma_local: Local entropy production rate σ_local.
            sigma_critical: Critical dissipation threshold (defaults to
                ``self.sigma_critical``).

        Returns:
            β_eff (always ≤ β_global).
        """
        sc = sigma_critical if sigma_critical is not None else self.sigma_critical
        denominator = 1.0 + abs(sigma_local) / max(abs(sc), 1e-12)
        return float(beta_global / denominator)

    def compute_full_field(
        self,
        state: float,
        crep_gamma: float,
        beta_global: float,
        kappa: float = 1.0,
    ) -> EntropyProductionField:
        """Compute the full AFET field snapshot.

        Combines entropy production, β-reduction, and regime detection.

        Args:
            state: Current system state.
            crep_gamma: CREP coupling Γ.
            beta_global: Global β steepness.
            kappa: CREP-entropy coupling constant.

        Returns:
            EntropyProductionField snapshot.
        """
        sigma_local = self.compute_local_entropy_production(state, crep_gamma, kappa)
        sigma_crep = self.sigma_0 * (1.0 + kappa * abs(crep_gamma))
        beta_eff = self.beta_reduction_formula(beta_global, sigma_local)
        regime = self.detect_governance_regime(beta_eff)
        return EntropyProductionField(
            sigma_local=sigma_local,
            sigma_crep=sigma_crep,
            beta_eff=beta_eff,
            regime=regime,
            gamma=crep_gamma,
            kappa=kappa,
        )

    def phase_transition_surface_to_volume(
        self,
        entropy_time_series: np.ndarray,
        window: int = 5,
    ) -> DualEntropyGovernance:
        """Detect the S∝A → S∝V phase transition in an entropy time series.

        Computes local β_eff from the variance/mean ratio (coefficient of
        variation proxy) over a rolling window. Detects the first crossing
        of the BETA_BOUNDARY from above (surface) to below (volume).

        Args:
            entropy_time_series: 1-D array of entropy values over time.
            window: Rolling window size for local β estimation.

        Returns:
            DualEntropyGovernance result.
        """
        ts = np.asarray(entropy_time_series, dtype=float)
        n = len(ts)
        if n < window:
            regime = self.detect_governance_regime(self.beta_surface)
            return DualEntropyGovernance(
                regime=regime,
                beta_eff=self.beta_surface,
                transition_detected=False,
                transition_index=-1,
                confidence=0.0,
            )

        boundary = (self.beta_surface + self.beta_volume) / 2.0

        # Estimate local β from rolling coefficient of variation
        beta_series: list[float] = []
        for i in range(window - 1, n):
            window_slice = ts[max(0, i - window + 1) : i + 1]
            mean_val = float(np.mean(np.abs(window_slice)))
            std_val = float(np.std(window_slice))
            if mean_val < 1e-10:
                beta_series.append(self.beta_volume)
                continue
            cv = std_val / mean_val
            # High CV → low β (volume regime); low CV → high β (surface regime)
            # Map: β_eff = β_surface * exp(-cv * 2)
            beta_local = self.beta_surface * float(np.exp(-cv * 2.0))
            beta_series.append(float(np.clip(beta_local, 0.0, self.beta_surface * 2)))

        beta_arr = np.array(beta_series)
        transition_idx = -1
        for i in range(1, len(beta_arr)):
            if beta_arr[i - 1] > boundary >= beta_arr[i]:
                transition_idx = i + (window - 1)
                break

        final_beta = float(beta_arr[-1]) if len(beta_arr) > 0 else self.beta_surface
        regime = self.detect_governance_regime(final_beta)
        transition_detected = transition_idx >= 0

        confidence = 0.0
        if transition_detected and len(beta_arr) > 1:
            delta = float(abs(beta_arr[max(0, transition_idx - (window - 1))] - boundary))
            confidence = float(np.clip(delta / self.beta_surface, 0.0, 1.0))

        return DualEntropyGovernance(
            regime=regime,
            beta_eff=final_beta,
            transition_detected=transition_detected,
            transition_index=transition_idx,
            confidence=confidence,
        )

    @property
    def production_history(self) -> list[float]:
        """History of computed local entropy production values."""
        return list(self._production_history)

    def reset(self) -> None:
        """Clear production history."""
        self._production_history.clear()
