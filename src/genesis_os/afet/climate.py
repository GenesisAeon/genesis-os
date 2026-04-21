"""AFET climate module — entropy integration with ERA5-style climate data.

Ports relevant logic from Feldtheorie's Entropy_in_Climate module,
adapted to work cleanly with the genesis-os ERA5 pipeline.

Key functions:
    - rolling_entropy_trend: Compute rolling entropy trends from climate arrays
    - arctic_sea_ice_entropy: Entropy proxy for Arctic sea ice extent
    - amoc_entropy_production: AMOC-related entropy production estimate
    - detect_climate_regime_shift: Detect β-level regime shifts in climate data
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from genesis_os.afet.field import AFETField, DualEntropyGovernance


@dataclass(frozen=True)
class ClimateEntropyResult:
    """Result of a climate entropy computation.

    Attributes:
        entropy_rate: Mean entropy production rate.
        beta_eff: Effective β for the climate system.
        regime: Detected entropy governance regime.
        regime_shift_year: Estimated year of regime shift (or None).
        rolling_entropy: Array of rolling entropy values.
    """

    entropy_rate: float
    beta_eff: float
    regime: str
    regime_shift_year: int | None
    rolling_entropy: np.ndarray


def rolling_entropy_trend(
    data: np.ndarray,
    window: int = 10,
    normalize: bool = True,
) -> np.ndarray:
    """Compute rolling Shannon-like entropy from a univariate climate time series.

    Uses a sliding window to estimate local entropy as:
        H_local = -Σ p_i · log(p_i)  (binned histogram within window)

    Args:
        data: 1-D array of climate variable values.
        window: Rolling window size (in time steps).
        normalize: If True, normalize output to [0, 1].

    Returns:
        Array of rolling entropy values (length = len(data) - window + 1).
    """
    arr = np.asarray(data, dtype=float)
    n = len(arr)
    if n < window:
        return np.array([], dtype=float)

    entropies = []
    for i in range(n - window + 1):
        seg = arr[i : i + window]
        hist, _ = np.histogram(seg, bins=min(window, 5), density=False)
        hist = hist.astype(float)
        total = hist.sum()
        if total == 0:
            entropies.append(0.0)
            continue
        p = hist[hist > 0] / total
        h = float(-np.sum(p * np.log(p + 1e-12)))
        entropies.append(h)

    result = np.array(entropies, dtype=float)
    if normalize and result.size > 0:
        rng = float(result.max() - result.min())
        if rng > 1e-12:
            result = (result - result.min()) / rng
    return result


def arctic_sea_ice_entropy(
    extent_km2: np.ndarray,
    years: np.ndarray | None = None,
    window: int = 5,
) -> ClimateEntropyResult:
    """Compute entropy proxy from Arctic sea ice extent time series.

    Sea ice extent serves as a proxy for Arctic climate state. Declining
    extent corresponds to increasing entropy (disorder / phase transition).

    Args:
        extent_km2: Annual Arctic sea ice extent (10^6 km²) time series.
        years: Corresponding year array (optional, for regime-shift reporting).
        window: Rolling window for entropy computation.

    Returns:
        ClimateEntropyResult with regime classification and shift detection.
    """
    arr = np.asarray(extent_km2, dtype=float)
    afet = AFETField(sigma_0=1.0, sigma_critical=1.0)

    rolling = rolling_entropy_trend(arr, window=window, normalize=True)
    governance = afet.phase_transition_surface_to_volume(rolling, window=window)

    mean_rate = float(np.mean(np.abs(np.diff(arr)))) if len(arr) > 1 else 0.0

    regime_shift_year: int | None = None
    if governance.transition_detected and years is not None:
        idx = governance.transition_index
        if 0 <= idx < len(years):
            regime_shift_year = int(years[idx])

    return ClimateEntropyResult(
        entropy_rate=mean_rate,
        beta_eff=governance.beta_eff,
        regime=governance.regime,
        regime_shift_year=regime_shift_year,
        rolling_entropy=rolling,
    )


def amoc_entropy_production(
    amoc_strength_sv: np.ndarray,
    crep_gamma_series: np.ndarray | None = None,
    kappa: float = 1.0,
) -> np.ndarray:
    """Estimate AMOC-related entropy production over time.

    AMOC (Atlantic Meridional Overturning Circulation) strength in Sv (sverdrup).
    Lower AMOC strength corresponds to higher entropy production in the climate system.

    Args:
        amoc_strength_sv: Time series of AMOC strength in Sv.
        crep_gamma_series: Optional CREP coupling series (same length). Uses 0.5 if None.
        kappa: CREP-entropy coupling constant.

    Returns:
        Array of entropy production values (same length as amoc_strength_sv).
    """
    amoc = np.asarray(amoc_strength_sv, dtype=float)
    n = len(amoc)
    if n == 0:
        return np.array([], dtype=float)

    gammas = (
        np.asarray(crep_gamma_series, dtype=float)
        if crep_gamma_series is not None
        else np.full(n, 0.5)
    )
    if len(gammas) != n:
        gammas = np.full(n, 0.5)

    afet = AFETField(sigma_0=1.0, sigma_critical=1.0)
    sigma_max = float(np.max(np.abs(amoc))) if np.max(np.abs(amoc)) > 0 else 1.0
    production = np.zeros(n, dtype=float)
    for i in range(n):
        normalized_state = float(amoc[i]) / sigma_max
        production[i] = afet.compute_local_entropy_production(
            state=normalized_state, crep_gamma=float(gammas[i]), kappa=kappa
        )
    return production


def detect_climate_regime_shift(
    climate_series: np.ndarray,
    window: int = 10,
    beta_threshold: float = 7.75,
) -> DualEntropyGovernance:
    """Detect regime shifts in a climate time series via AFET analysis.

    Wraps the AFET field transition detector for direct climate data use.

    Args:
        climate_series: 1-D array of climate variable values.
        window: Rolling window for local β estimation.
        beta_threshold: Custom β boundary for regime classification.

    Returns:
        DualEntropyGovernance with transition detection results.
    """
    afet = AFETField(
        sigma_0=1.0,
        sigma_critical=1.0,
        beta_surface=beta_threshold * 1.4,
        beta_volume=beta_threshold * 0.6,
    )
    rolling = rolling_entropy_trend(
        np.asarray(climate_series, dtype=float), window=window, normalize=True
    )
    if len(rolling) == 0:
        return DualEntropyGovernance(
            regime="surface",
            beta_eff=beta_threshold * 1.4,
            transition_detected=False,
            transition_index=-1,
            confidence=0.0,
        )
    return afet.phase_transition_surface_to_volume(rolling, window=window)
