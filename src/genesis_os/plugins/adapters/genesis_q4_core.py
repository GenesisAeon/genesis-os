"""Adapter for genesis-q4-core: optional GenesisAeon ecosystem package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    import genesis_q4_core as _mod
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _mod = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    return {"genesis_q4_core_available": _AVAILABLE}
