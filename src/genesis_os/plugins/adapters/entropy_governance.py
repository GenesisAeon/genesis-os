"""Adapter for entropy-governance: policy-based entropy control."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:  # pragma: no cover
    from entropy_governance import EntropyPolicy  # type: ignore[import-not-found]

    _POLICY = EntropyPolicy()
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _POLICY = None


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Apply entropy governance policy and return adjusted entropy."""
    if not _AVAILABLE:
        return {"entropy_governance_available": False}
    try:
        adjusted = _POLICY.apply(state.entropy, state.cycle)
        return {"entropy_governance_available": True, "governed_entropy": float(adjusted)}
    except Exception:
        return {"entropy_governance_available": True, "governed_entropy": None}
