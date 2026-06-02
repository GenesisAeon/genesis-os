"""Adapter for cosmic-moment: optional GenesisAeon ecosystem package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    import cosmic_moment as _mod
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _mod = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    return {"cosmic_moment_available": _AVAILABLE}
