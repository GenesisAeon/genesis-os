"""Cascade-collapse detection across multiple weakly-coupled domains."""

from __future__ import annotations

from resilience_core.constants import C_CRITICAL, GAMMA_MAX
from resilience_core.coupling import CouplingMatrix


def detect_cascade(
    target_domain: str,
    gamma: float,
    coupling: CouplingMatrix,
    gamma_max: float = GAMMA_MAX,
    c_critical: float = C_CRITICAL,
) -> dict[str, object]:
    """Return cascade-risk assessment for target_domain.

    A cascade is imminent when:
    - The system is near its critical Γ threshold (Γ > 0.875 · Γ_max), AND
    - Multiple destabilising couplings are active simultaneously.

    Args:
        target_domain: Domain being evaluated.
        gamma:         Current Γ for that domain.
        coupling:      CouplingMatrix populated with active couplings.
        gamma_max:     Saturated-system ceiling (default 0.920).
        c_critical:    Collapse threshold for total coupling load.

    Returns:
        Dict with risk flag, load fraction, and active sources.
    """
    load = coupling.total_load(target_domain)
    sources = coupling.sources_for(target_domain)
    n_destabilising = sum(1 for v in sources.values() if v > 0)

    near_gamma_limit = gamma > gamma_max * 0.95  # noqa: PLR2004
    overloaded = load > c_critical * 0.5  # noqa: PLR2004
    cascade_risk = near_gamma_limit and overloaded and n_destabilising > 0

    return {
        "cascade_risk": cascade_risk,
        "load_fraction": load / c_critical,
        "near_gamma_limit": near_gamma_limit,
        "n_destabilising_couplings": n_destabilising,
        "active_sources": sources,
    }
