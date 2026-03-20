"""Adapter for aeon-ai v0.2.0: PhaseDetector + SelfReflector."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from aeon_ai import PhaseDetector, SelfReflector  # type: ignore[import-not-found]

    _DETECTOR = PhaseDetector()
    _REFLECTOR = SelfReflector()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _DETECTOR = None
    _REFLECTOR = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Inject aeon-ai phase detection and self-reflection data.

    Args:
        state: Current GenesisState.

    Returns:
        Dict with keys ``aeon_phase``, ``aeon_reflection``.
    """
    if not _AVAILABLE:
        return {"aeon_available": False}

    result: dict[str, Any] = {"aeon_available": True}
    try:
        crep_vec = state.crep.to_vector() if state.crep else None
        if crep_vec is not None:
            result["aeon_phase"] = _DETECTOR.detect(crep_vec)  # type: ignore[union-attr]
            result["aeon_reflection"] = _REFLECTOR.reflect(state.phi, crep_vec)  # type: ignore[union-attr]
    except Exception:
        pass
    return result
