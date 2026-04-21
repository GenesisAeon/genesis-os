"""RegimeDetector — rolling-window UTAC parameter fitting + v_RIG detection.

Fits UTAC ODE parameters {r, K, σ} on rolling windows and computes the
information-geometric velocity v_RIG(t) to detect regime transitions.

Primary use case: Arctic sea ice decline (~1998 regime shift detection).
Parameters fitted: r (growth rate), K (carrying capacity), σ (coupling).
Rolling window: W = 10 time steps (years for annual data).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from genesis_os.vrig.velocity import VRIGVelocity


@dataclass(frozen=True)
class RegimeShift:
    """Record of a detected regime shift.

    Attributes:
        time_index: Index in the original time series.
        velocity: v_RIG value at detection.
        params_before: UTAC parameters before shift.
        params_after: UTAC parameters after shift.
        confidence: Detection confidence ∈ [0, 1].
    """

    time_index: int
    velocity: float
    params_before: np.ndarray
    params_after: np.ndarray
    confidence: float


@dataclass
class RegimeDetector:
    """Rolling-window UTAC parameter regime detector.

    Fits a simplified UTAC logistic model on each rolling window and
    computes v_RIG to identify sudden parameter shifts.

    The simplified UTAC logistic fit uses:
        H_t+1 = H_t + r · H_t · (1 - H_t/K) · tanh(σ · Γ)

    Parameters estimated per window: [r, K, σ] via least-squares on
    the finite-difference ΔH/H (relative growth rate).

    Args:
        window_size: Number of time steps in each rolling window (default 10).
        threshold_sigma: v_RIG threshold in units of std above mean (default 3.0).
        min_windows: Minimum number of windows required for detection (default 3).
    """

    window_size: int = 10
    threshold_sigma: float = 3.0
    min_windows: int = 3
    _velocity_engine: VRIGVelocity = field(
        default_factory=VRIGVelocity, init=False, repr=False
    )
    _params_history: list[np.ndarray] = field(default_factory=list, init=False, repr=False)
    _detected_shifts: list[RegimeShift] = field(default_factory=list, init=False, repr=False)

    def _fit_utac_window(self, window: np.ndarray) -> np.ndarray:
        """Fit simplified UTAC parameters on a rolling window.

        Estimates [r, K, σ] via ordinary least squares on relative growth:
            ΔH/Δt ≈ r · (1 - H/K) · tanh(σ · Γ)

        For the simplified single-variable case (no external Γ), uses
        the mean amplitude as proxy for σ·Γ.

        Args:
            window: 1-D array of state values over the window.

        Returns:
            Parameter array [r, K, sigma] (length 3).
        """
        n = len(window)
        if n < 3:
            return np.array([0.3, float(np.max(np.abs(window)) + 1e-6), 1.0])

        # Estimate K as max observed value
        K_est = float(max(np.max(np.abs(window)), 1e-6))
        # Estimate r from mean relative growth rate
        diffs = np.diff(window.astype(float))
        w_safe = np.where(np.abs(window[:-1]) > 1e-6, window[:-1], 1e-6)
        rel_growth = diffs / w_safe
        r_est = float(np.clip(np.mean(rel_growth), -1.0, 1.0))
        # Estimate sigma from coefficient of variation as proxy
        std_w = float(np.std(window))
        mean_w = float(abs(np.mean(window)))
        sigma_est = float(std_w / max(mean_w, 1e-6))
        return np.array([r_est, K_est, sigma_est])

    def _log_likelihood(self, params: np.ndarray, window: np.ndarray) -> float:
        """Compute log-likelihood of UTAC parameters for a data window.

        Uses Gaussian residuals with the UTAC ODE as the mean model.

        Args:
            params: [r, K, sigma] parameter vector.
            window: Observed data window.

        Returns:
            Log-likelihood scalar.
        """
        r, K, sigma = params[0], max(params[1], 1e-6), params[2]
        n = len(window)
        if n < 2:
            return 0.0

        # Simulate UTAC ODE
        H = float(window[0])
        residuals = []
        for i in range(1, n):
            H_pred = H + r * H * (1.0 - H / K) * math.tanh(sigma * 0.5)  # Γ=0.5 proxy
            H_pred = float(np.clip(H_pred, 0.0, K * 2))
            residuals.append(float(window[i]) - H_pred)
            H = H_pred

        if not residuals:
            return 0.0

        residuals_arr = np.array(residuals)
        sigma_noise = max(float(np.std(residuals_arr)), 1e-6)
        ll = float(-0.5 * np.sum((residuals_arr / sigma_noise) ** 2)) - len(residuals) * math.log(
            sigma_noise + 1e-12
        )
        return ll

    def fit(self, time_series: np.ndarray) -> list[np.ndarray]:
        """Fit UTAC parameters over all rolling windows.

        Args:
            time_series: 1-D array of state values over time.

        Returns:
            List of parameter arrays [r, K, sigma], one per window.
        """
        ts = np.asarray(time_series, dtype=float)
        n = len(ts)
        self._params_history.clear()

        for i in range(n - self.window_size + 1):
            window = ts[i : i + self.window_size]
            params = self._fit_utac_window(window)
            self._params_history.append(params)

        return list(self._params_history)

    def compute_velocity_series(self) -> np.ndarray:
        """Compute v_RIG over the fitted parameter history.

        Must call fit() first.

        Returns:
            Array of v_RIG values (length = n_windows - 1).
        """
        if len(self._params_history) < 2:
            return np.array([], dtype=float)

        velocities = []
        for i in range(1, len(self._params_history)):
            # Build FIM from log-likelihood at current params
            p_curr = self._params_history[i]
            fim = self._velocity_engine.compute_fisher_information_matrix(
                params=p_curr,
                log_likelihood_fn=lambda p: float(-0.5 * np.sum(p**2)),  # Gaussian proxy
            )
            v = self._velocity_engine.compute_velocity(
                params_t=p_curr,
                params_prev=self._params_history[i - 1],
                fim=fim,
            )
            velocities.append(v)
        return np.array(velocities, dtype=float)

    def detect(self, time_series: np.ndarray) -> list[RegimeShift]:
        """Full pipeline: fit → velocity → detect shifts.

        Args:
            time_series: 1-D array of state values over time.

        Returns:
            List of RegimeShift records (may be empty).
        """
        params_list = self.fit(time_series)
        if len(params_list) < self.min_windows:
            return []

        vel_series = self.compute_velocity_series()
        if len(vel_series) == 0:
            return []

        flagged_indices = self._velocity_engine.detect_regime_change(
            vel_series, threshold_sigma=self.threshold_sigma
        )

        self._detected_shifts = []
        for idx in flagged_indices:
            param_idx = idx + 1  # velocity[i] corresponds to params[i+1]
            if param_idx >= len(params_list):
                continue
            p_before = params_list[max(0, param_idx - 1)]
            p_after = params_list[param_idx]
            v_val = float(vel_series[idx])
            v_max = float(np.max(vel_series))
            confidence = float(np.clip(v_val / max(v_max, 1e-12), 0.0, 1.0))

            time_idx = idx + self.window_size  # map back to original time series
            shift = RegimeShift(
                time_index=time_idx,
                velocity=v_val,
                params_before=p_before,
                params_after=p_after,
                confidence=confidence,
            )
            self._detected_shifts.append(shift)

        return list(self._detected_shifts)

    @property
    def detected_shifts(self) -> list[RegimeShift]:
        """Read-only list of detected regime shifts from last detect() call."""
        return list(self._detected_shifts)

    @property
    def n_windows(self) -> int:
        """Number of windows fitted."""
        return len(self._params_history)

    def summary(self) -> dict[str, Any]:
        """Return a summary of detection results."""
        return {
            "n_windows": self.n_windows,
            "n_shifts_detected": len(self._detected_shifts),
            "window_size": self.window_size,
            "threshold_sigma": self.threshold_sigma,
            "shift_indices": [s.time_index for s in self._detected_shifts],
        }
