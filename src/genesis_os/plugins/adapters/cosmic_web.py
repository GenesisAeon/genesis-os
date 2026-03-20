"""Adapter for cosmic-web: large-scale structure simulation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from cosmic_web import CosmicWebSimulator  # type: ignore[import-not-found]

    _SIM = CosmicWebSimulator()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _SIM = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Run a single cosmic-web coupling step."""
    if not _AVAILABLE or state.crep is None:
        return {"cosmic_web_available": _AVAILABLE}
    try:
        node_density = _SIM.step(state.crep.to_vector(), state.entropy)
        return {"cosmic_web_available": True, "node_density": float(node_density)}
    except Exception:
        return {"cosmic_web_available": True, "node_density": None}
