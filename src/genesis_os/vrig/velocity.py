"""v_RIG velocity on the Fisher-Rao information-geometric manifold.

The information-geometric velocity measures how fast parameters {r, K, σ}
move in parameter space, weighted by the Fisher information metric:

    v_RIG(t) = √(Δθ^T · FIM · Δθ) / Δt

where FIM is the Fisher information matrix estimated from the likelihood
function of the UTAC logistic ODE.

Scientific note: v_RIG ≈ 1351.8 km/s is a hypothesis based on:
    c / (α · Φ) ≈ 299792.458 / (137.036 · 1.6180) ≈ 1351.8 km/s
This is NOT a verified physical constant.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Final

import numpy as np

V_RIG_KMS: Final[float] = 299792.458 / (137.036 * 1.6180339887)  # ≈ 1351.8 km/s


@dataclass
class VRIGResult:
    """Result of a v_RIG velocity computation.

    Attributes:
        velocity: v_RIG(t) value.
        fim: Fisher information matrix (n_params × n_params).
        delta_theta: Parameter displacement vector.
        regime_change: True if velocity exceeds detection threshold.
        params_current: Current parameter vector.
        params_prev: Previous parameter vector.
    """

    velocity: float
    fim: np.ndarray
    delta_theta: np.ndarray
    regime_change: bool
    params_current: np.ndarray
    params_prev: np.ndarray


@dataclass
class VRIGVelocity:
    """Information-geometric velocity on the Fisher-Rao manifold.

    Computes the Fisher-Rao metric tensor and the resulting parameter-space
    velocity to detect rapid regime transitions.

    Args:
        dt: Time step between parameter estimates (default 1.0).
        fim_epsilon: Finite-difference step for FIM estimation (default 1e-4).
        n_params: Number of parameters (default 3 for [r, K, sigma]).
    """

    dt: float = 1.0
    fim_epsilon: float = 1e-4
    n_params: int = 3
    _velocity_history: list[float] = field(default_factory=list, init=False, repr=False)

    def compute_fisher_information_matrix(
        self,
        params: np.ndarray,
        log_likelihood_fn: Callable[[np.ndarray], float],
    ) -> np.ndarray:
        """Estimate the FIM via finite differences of the log-likelihood.

        FIM[i,j] = -E[∂²ℓ/∂θ_i∂θ_j] ≈ -∂²ℓ/∂θ_i∂θ_j  (sample approximation)

        Uses the outer product approximation:
            FIM ≈ g^T g  where g_i = ∂ℓ/∂θ_i (finite difference)

        Args:
            params: Current parameter vector (n_params,).
            log_likelihood_fn: Function mapping params → scalar log-likelihood.

        Returns:
            FIM matrix (n_params × n_params), positive semi-definite.
        """
        p = np.asarray(params, dtype=float)
        n = len(p)
        eps = self.fim_epsilon
        grad = np.zeros(n)

        ll_0 = float(log_likelihood_fn(p))
        for i in range(n):
            p_plus = p.copy()
            p_plus[i] += eps
            try:
                ll_plus = float(log_likelihood_fn(p_plus))
            except Exception:
                ll_plus = ll_0
            grad[i] = (ll_plus - ll_0) / eps

        # Outer product gives rank-1 PSD FIM estimate
        fim = np.outer(grad, grad)
        # Add small regularization for invertibility
        fim += np.eye(n) * 1e-8
        return fim

    def compute_velocity(
        self,
        params_t: np.ndarray,
        params_prev: np.ndarray,
        fim: np.ndarray,
    ) -> float:
        """Compute the information-geometric velocity.

        v_RIG(t) = √(Δθ^T · FIM · Δθ) / Δt

        Args:
            params_t: Current parameter vector.
            params_prev: Previous parameter vector.
            fim: Fisher information matrix.

        Returns:
            v_RIG(t) ≥ 0.
        """
        delta = np.asarray(params_t, dtype=float) - np.asarray(params_prev, dtype=float)
        fim_arr = np.asarray(fim, dtype=float)
        inner = float(delta @ fim_arr @ delta)
        v = math.sqrt(max(0.0, inner)) / max(self.dt, 1e-12)
        self._velocity_history.append(v)
        return v

    def detect_regime_change(
        self,
        velocity_series: np.ndarray,
        threshold_sigma: float = 3.0,
    ) -> list[int]:
        """Detect timestamps where v_RIG exceeds threshold_sigma·std above mean.

        Args:
            velocity_series: 1-D array of v_RIG values over time.
            threshold_sigma: Number of standard deviations above mean to flag.

        Returns:
            List of integer indices where regime change is detected.
        """
        arr = np.asarray(velocity_series, dtype=float)
        if len(arr) < 3:
            return []
        mean_v = float(np.mean(arr))
        std_v = float(np.std(arr))
        if std_v < 1e-12:
            return []
        threshold = mean_v + threshold_sigma * std_v
        return [int(i) for i in range(len(arr)) if arr[i] > threshold]

    @property
    def velocity_history(self) -> list[float]:
        """History of computed v_RIG values."""
        return list(self._velocity_history)

    @property
    def v_rig_constant_kms(self) -> float:
        """Hypothetical v_RIG reference constant in km/s.

        c / (α · Φ) ≈ 1351.8 km/s — research hypothesis only.
        """
        return V_RIG_KMS

    def reset(self) -> None:
        """Clear velocity history."""
        self._velocity_history.clear()
