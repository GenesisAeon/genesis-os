"""Adapter for scope-resilience (Package 41): semantic hallucination resilience."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genesis_os.core.orchestrator import GenesisState

try:
    from scope_resilience import ScopeResilience as _ScopeResilience

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _ScopeResilience = None  # type: ignore[assignment,misc]


def plugin_fn(state: GenesisState) -> dict[str, Any]:
    """Assess hallucination resilience Ρ_sem for the active semantic context."""
    if not _AVAILABLE:
        return {"scope_resilience_available": False}

    try:
        sr = _ScopeResilience(domain="general")
        topic = getattr(state, "topic", "") or ""
        result = sr.run_cycle(topic)
        return {
            "scope_resilience_available": True,
            "rho_sem": result["rho_sem"],
            "gamma_sem": result["gamma_sem"],
            "risk_level": result["risk_level"],
            "needs_regrounding": result["needs_regrounding"],
        }
    except Exception:
        return {"scope_resilience_available": True, "rho_sem": None}
