"""Adapter for resilience-core (Package 40): system resilience Ρ."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:
    from resilience_core import ResilienceCore as _ResilienceCore

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _ResilienceCore = None  # type: ignore[assignment,misc]


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Compute system resilience Ρ from the current CREP Γ value."""
    if not _AVAILABLE or state.crep is None:
        return {"resilience_core_available": _AVAILABLE}

    try:
        gamma = float(state.crep.gamma)
        core = _ResilienceCore(domain="genesis_os")
        result = core.run_cycle(gamma=gamma)
        return {
            "resilience_core_available": True,
            "rho": result["rho"],
            "lambda_star": result["lambda_star"],
            "criticality_margin": result["criticality_margin"],
            "near_collapse": result["near_collapse"],
        }
    except Exception:
        return {"resilience_core_available": True, "rho": None}
