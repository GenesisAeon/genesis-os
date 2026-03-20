"""Adapter for utac-core: external UTAC implementation."""

from __future__ import annotations

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


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Override internal UTAC with external utac-core step."""
    if not _AVAILABLE or state.crep is None:
        return {"utac_core_available": _AVAILABLE}
    try:
        result = _ENGINE.step(state.entropy, state.crep.gamma)  # type: ignore[union-attr]
        return {"utac_core_available": True, "utac_entropy": float(result)}
    except Exception:
        return {"utac_core_available": True, "utac_entropy": None}
