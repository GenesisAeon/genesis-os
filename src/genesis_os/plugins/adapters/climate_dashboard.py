"""Adapter for climate-dashboard: environmental entropy coupling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from climate_dashboard import ClimateEntropy  # type: ignore[import-not-found]

    _CLIMATE = ClimateEntropy()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _CLIMATE = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Inject climate entropy data into the system state."""
    if not _AVAILABLE:
        return {"climate_dashboard_available": False}
    try:
        climate_h = _CLIMATE.entropy(state.cycle)  # type: ignore[union-attr]
        return {"climate_dashboard_available": True, "climate_entropy": float(climate_h)}
    except Exception:
        return {"climate_dashboard_available": True, "climate_entropy": None}
