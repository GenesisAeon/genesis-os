"""Adapter for cosmic-moment: optional GenesisAeon ecosystem package."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState
try:
    import cosmic_moment as _mod  # type: ignore[import-not-found]
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _mod = None  # type: ignore[assignment]

def plugin_fn(state: GenesisState) -> dict[str, Any]:
    return {"cosmic_moment_available": _AVAILABLE}
