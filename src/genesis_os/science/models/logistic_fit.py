"""UTAC logistic σ(β(R-Θ)) fitter with ΔAIC validation.

Ports Feldtheorie models/membrane_solver.py.

Fits:   A(R) = 1 / (1 + exp(-β·(R - Θ)))

Null model comparison (ΔAIC ≥ 10 required for strong evidence):
    - Linear:      A(R) = a·R + b
    - Power law:   A(R) = a·R^b
    - Exponential: A(R) = a·exp(b·R)

Bootstrap CI: 1000 iterations, seed=1337.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UTACLogisticResult:
    """Result of a UTAC logistic fit.

    Attributes:
        beta: Fitted logistic steepness β.
        theta: Fitted inflection threshold Θ.
        L: Log-likelihood of the fitted model.
        beta_ci_95: 95% bootstrap confidence interval (lower, upper).
        delta_aic_linear: ΔAIC vs linear null model (positive = logistic better).
        delta_aic_power: ΔAIC vs power-law null model.
        delta_aic_exp: ΔAIC vs exponential null model.
        r_squared: R² of the logistic fit.
        n: Number of data points.
        success: True if fit converged successfully.
    """

    beta: float
    theta: float
    L: float
    beta_ci_95: tuple[float, float]
    delta_aic_linear: float
    delta_aic_power: float
    delta_aic_exp: float
    r_squared: float
    n: int
    success: bool


# ---------------------------------------------------------------------------
# Model functions
# ---------------------------------------------------------------------------


def _logistic(R: np.ndarray, beta: float, theta: float) -> np.ndarray:
    """Evaluate UTAC logistic activation σ(β(R-Θ))."""
    exponent = np.clip(-beta * (R - theta), -500.0, 500.0)
    return 1.0 / (1.0 + np.exp(exponent))


def _linear(R: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * R + b


def _power_law(R: np.ndarray, a: float, b: float) -> np.ndarray:
    R_safe = np.where(np.abs(R) < 1e-12, 1e-12, np.abs(R))
    return a * R_safe ** np.clip(b, -10.0, 10.0)


def _exponential(R: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * np.exp(np.clip(b * R, -500.0, 500.0))


def _compute_aic(residuals: np.ndarray, n_params: int) -> float:
    """Compute AIC = 2k - 2L (Gaussian likelihood)."""
    n = len(residuals)
    if n == 0:
        return 0.0
    sigma2 = max(float(np.mean(residuals**2)), 1e-12)
    ll = -n / 2.0 * (math.log(2 * math.pi * sigma2) + 1.0)
    return float(2 * n_params - 2 * ll)


def _fit_least_squares(
    R: np.ndarray, y: np.ndarray, model_fn: Any, n_params: int
) -> tuple[np.ndarray, float]:
    """Grid-search least-squares fit for a 2-parameter model.

    Returns best (params, aic).
    """
    best_sse = float("inf")
    best_params = np.zeros(n_params)

    for a in np.linspace(0.01, 3.0, 15):
        for b in np.linspace(-5.0, 5.0, 15):
            try:
                y_pred = model_fn(R, a, b)
                sse = float(np.mean((y - y_pred) ** 2))
                if sse < best_sse:
                    best_sse = sse
                    best_params = np.array([a, b])
            except Exception:
                continue

    residuals = y - model_fn(R, *best_params)
    aic = _compute_aic(residuals, n_params)
    return best_params, aic


def _fit_logistic_grid(R: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Grid search for logistic β and Θ parameters.

    Returns (beta, theta, aic).
    """
    best_sse = float("inf")
    best_beta = 1.0
    best_theta = 0.5

    r_min, r_max = float(R.min()), float(R.max())
    r_range = max(r_max - r_min, 1e-6)
    theta_grid = np.linspace(r_min + r_range * 0.1, r_max - r_range * 0.1, 20)
    beta_grid = np.linspace(0.5, 25.0, 30)

    for beta in beta_grid:
        for theta in theta_grid:
            y_pred = _logistic(R, beta, theta)
            sse = float(np.mean((y - y_pred) ** 2))
            if sse < best_sse:
                best_sse = sse
                best_beta = float(beta)
                best_theta = float(theta)

    residuals = y - _logistic(R, best_beta, best_theta)
    aic = _compute_aic(residuals, n_params=2)
    return best_beta, best_theta, aic


# ---------------------------------------------------------------------------
# Main fitting function
# ---------------------------------------------------------------------------


def fit_utac_logistic(
    R: np.ndarray,
    response: np.ndarray,
    null_models: list[str] | None = None,
    n_bootstrap: int = 1000,
    bootstrap_seed: int = 1337,
) -> UTACLogisticResult:
    """Fit the UTAC logistic A(R) = σ(β(R-Θ)) to data.

    Compares against null models using AIC. Bootstrap CI for β.

    ΔAIC ≥ 10 vs all nulls indicates strong evidence for logistic.

    Args:
        R: Resource / state variable array (independent variable).
        response: Observed response array (dependent variable, in [0,1]).
        null_models: List of null models to compare. Defaults to
            ``["linear", "power_law", "exponential"]``.
        n_bootstrap: Bootstrap iterations for CI (default 1000).
        bootstrap_seed: Random seed for reproducibility (default 1337).

    Returns:
        UTACLogisticResult with all fit statistics.
    """
    if null_models is None:
        null_models = ["linear", "power_law", "exponential"]

    R_arr = np.asarray(R, dtype=float).ravel()
    y_arr = np.asarray(response, dtype=float).ravel()
    n = min(len(R_arr), len(y_arr))

    if n < 4:
        return UTACLogisticResult(
            beta=1.0,
            theta=float(np.median(R_arr)) if n > 0 else 0.5,
            L=0.0,
            beta_ci_95=(0.0, 5.0),
            delta_aic_linear=0.0,
            delta_aic_power=0.0,
            delta_aic_exp=0.0,
            r_squared=0.0,
            n=n,
            success=False,
        )

    R_arr = R_arr[:n]
    y_arr = y_arr[:n]

    # Normalize response to [0, 1] if needed
    y_min, y_max = float(y_arr.min()), float(y_arr.max())
    y_norm = (y_arr - y_min) / (y_max - y_min) if y_max - y_min > 1e-12 else y_arr.copy()

    # Normalize R to [0, 1]
    r_min, r_max = float(R_arr.min()), float(R_arr.max())
    R_norm = (R_arr - r_min) / (r_max - r_min) if r_max - r_min > 1e-12 else R_arr.copy()

    # Fit logistic
    beta, theta, aic_logistic = _fit_logistic_grid(R_norm, y_norm)

    # Log-likelihood
    y_pred = _logistic(R_norm, beta, theta)
    residuals = y_norm - y_pred
    sigma2 = max(float(np.mean(residuals**2)), 1e-12)
    L = float(-n / 2.0 * math.log(2 * math.pi * sigma2) - np.sum(residuals**2) / (2 * sigma2))

    # R²
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((y_norm - np.mean(y_norm))**2))
    r_sq = float(1.0 - ss_res / max(ss_tot, 1e-12))

    # Null model AICs
    delta_aic: dict[str, float] = {}
    model_fns = {
        "linear": _linear,
        "power_law": _power_law,
        "exponential": _exponential,
    }
    for model_name in null_models:
        if model_name not in model_fns:
            delta_aic[model_name] = 0.0
            continue
        _, aic_null = _fit_least_squares(R_norm, y_norm, model_fns[model_name], n_params=2)
        delta_aic[model_name] = float(aic_null - aic_logistic)

    # Bootstrap CI for β
    rng = np.random.default_rng(bootstrap_seed)
    bootstrap_betas = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        R_bs = R_norm[idx]
        y_bs = y_norm[idx]
        try:
            b_beta, _, _ = _fit_logistic_grid(R_bs, y_bs)
            bootstrap_betas.append(b_beta)
        except Exception:
            bootstrap_betas.append(beta)

    betas_arr = np.array(bootstrap_betas)
    ci_low = float(np.percentile(betas_arr, 2.5))
    ci_high = float(np.percentile(betas_arr, 97.5))

    return UTACLogisticResult(
        beta=beta,
        theta=theta,
        L=L,
        beta_ci_95=(ci_low, ci_high),
        delta_aic_linear=delta_aic.get("linear", 0.0),
        delta_aic_power=delta_aic.get("power_law", 0.0),
        delta_aic_exp=delta_aic.get("exponential", 0.0),
        r_squared=max(0.0, r_sq),
        n=n,
        success=True,
    )
