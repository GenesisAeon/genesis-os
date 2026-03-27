"""Adapter for utac-core: external UTAC implementation."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from utac_core import UTACEngine  # type: ignore[import-not-found]

    _ENGINE = UTACEngine()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _ENGINE = None


def compute_tension_metric(temp_anomaly: float, ice_volume: float) -> float:
    """Compute UTAC tension metric from ERA5 climate observables.

    Maps temperature anomaly and Arctic ice volume to a scalar tension value
    consistent with the UTAC-Logistic framework. Higher temperature anomalies
    and lower ice volumes yield higher tension.

    .. math::
        C = \\exp\\!\\left(-\\frac{T^2}{2\\sigma^2}\\right), \\quad
        \\Gamma = C \\cdot \\exp\\!\\left(-\\frac{(1-C)^2}{2\\sigma^2}\\right), \\quad
        \\mathcal{T} = (1 - C + \\Gamma)\\,\\bigl(1 + \\tfrac{1}{1 + V}\\bigr)

    Args:
        temp_anomaly: Global mean temperature anomaly in °C.
        ice_volume: Arctic sea ice volume in 10³ km³ (PIOMAS-style).

    Returns:
        Tension metric T ≥ 0.
    """
    sigma = 1.5
    coherence = math.exp(-(temp_anomaly / sigma) ** 2 / 2.0)
    gamma = coherence * math.exp(-((1.0 - coherence) ** 2) / (2.0 * sigma**2))
    # Tension = lost coupling (1 - gamma) amplified by ice-volume stress.
    # As temp_anomaly rises, gamma falls and tension grows; lower ice → higher stress.
    ice_stress = 1.0 / (1.0 + max(0.0, ice_volume))
    return float((1.0 - gamma) * (1.0 + ice_stress))


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Override internal UTAC with external utac-core step."""
    if not _AVAILABLE or state.crep is None:
        return {"utac_core_available": _AVAILABLE}
    try:
        result = _ENGINE.step(state.entropy, state.crep.gamma)
        return {"utac_core_available": True, "utac_entropy": float(result)}
    except Exception:
        return {"utac_core_available": True, "utac_entropy": None}
