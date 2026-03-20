"""Adapter for entropy-table: tabular entropy state lookup."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from entropy_table import EntropyLookup  # type: ignore[import-not-found]

    _TABLE = EntropyLookup()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _TABLE = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Look up entropy table entry for current state."""
    if not _AVAILABLE:
        return {"entropy_table_available": False}
    try:
        entry = _TABLE.lookup(state.entropy, state.phase.value)
        return {"entropy_table_available": True, "entropy_table_entry": entry}
    except Exception:
        return {"entropy_table_available": True, "entropy_table_entry": None}
