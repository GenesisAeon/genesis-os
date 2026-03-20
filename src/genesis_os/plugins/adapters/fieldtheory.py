"""Adapter for fieldtheory: field-theoretic potential computation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from fieldtheory import FieldPotential  # type: ignore[import-not-found]

    _POTENTIAL = FieldPotential()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _POTENTIAL = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Compute field potential from entropy and phi."""
    if not _AVAILABLE:
        return {"fieldtheory_available": False}
    try:
        potential = _POTENTIAL.compute(state.entropy, state.phi)
        return {"fieldtheory_available": True, "field_potential": float(potential)}
    except Exception:
        return {"fieldtheory_available": True, "field_potential": None}
