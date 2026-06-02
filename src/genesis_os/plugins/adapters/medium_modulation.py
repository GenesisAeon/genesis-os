"""Adapter for medium-modulation: optional GenesisAeon ecosystem package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    import medium_modulation as _mod  # type: ignore[import-not-found]
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _mod = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    return {"medium_modulation_available": _AVAILABLE}
