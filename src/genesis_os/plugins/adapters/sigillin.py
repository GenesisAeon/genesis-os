"""Adapter for sigillin: symbolic trigger and sigil generation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from sigillin import SigilGenerator  # type: ignore[import-not-found]

    _SIGIL = SigilGenerator()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _SIGIL = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Generate a sigil token for the current phase."""
    if not _AVAILABLE:
        return {"sigillin_available": False}
    try:
        token = _SIGIL.generate(state.phase.value, state.cycle)
        return {"sigillin_available": True, "sigil_token": str(token)}
    except Exception:
        return {"sigillin_available": True, "sigil_token": None}
