"""Adapter for sonification plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    import sonification  # type: ignore[import-not-found]

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Signal sonification availability."""
    return {"sonification_available": _AVAILABLE}
