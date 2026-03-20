"""Adapter for mirror-machine: recursive self-mirroring resonance."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from mirror_machine import MirrorEngine  # type: ignore[import-not-found]

    _MIRROR = MirrorEngine()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _MIRROR = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Compute mirror resonance factor."""
    if not _AVAILABLE or state.crep is None:
        return {"mirror_available": _AVAILABLE}
    try:
        factor = _MIRROR.reflect(state.crep.resonance, state.phi)  # type: ignore[union-attr]
        return {"mirror_available": True, "mirror_resonance": float(factor)}
    except Exception:
        return {"mirror_available": True, "mirror_resonance": None}
