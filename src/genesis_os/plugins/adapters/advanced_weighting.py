"""Adapter for advanced-weighting-systems."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from advanced_weighting_systems import WeightingEngine  # type: ignore[import-not-found]

    _ENGINE = WeightingEngine()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _ENGINE = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Apply advanced weighting to the CREP vector."""
    if not _AVAILABLE or state.crep is None:
        return {"weighting_available": _AVAILABLE}
    try:
        weights = _ENGINE.compute(state.crep.to_vector())
        return {"weighting_available": True, "crep_weights": weights.tolist()}
    except Exception:
        return {"weighting_available": True, "crep_weights": None}
