"""Adapter for universums-sim: optional GenesisAeon ecosystem package."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState
try:
    import universums_sim as _mod  # type: ignore[import-not-found]
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _mod = None  # type: ignore[assignment]

def plugin_fn(state: GenesisState) -> dict[str, Any]:
    return {"universums_sim_available": _AVAILABLE}
