"""Adapter for implosive-genesis: implosive field dynamics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from implosive_genesis import ImplosiveField  # type: ignore[import-not-found]

    _FIELD = ImplosiveField()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _FIELD = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Compute implosive field strength from phi and entropy."""
    if not _AVAILABLE:
        return {"implosive_genesis_available": False}
    try:
        strength = _FIELD.compute(state.phi, state.entropy)  # type: ignore[union-attr]
        return {"implosive_genesis_available": True, "implosive_strength": float(strength)}
    except Exception:
        return {"implosive_genesis_available": True, "implosive_strength": None}
