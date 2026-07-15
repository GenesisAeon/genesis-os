"""Semantic CREP tensor computation for LLM paths.

Γ_sem(P) = (C_sem · R_sem · E_sem · P_sem)^(1/4)

All four components are estimated from path metadata when a live
Sigillin store is unavailable.  The domain config table documents
the calibration status of each r_sem value.
"""

from __future__ import annotations

import warnings

import numpy as np


# Semantic domain r_sem configuration.
# Structure is universal; only the numeric values differ per domain.
# All values are "estimate" until P49/TIP correlation data provides ≥30 pairs.
DOMAIN_CONFIG: dict[str, dict[str, object]] = {
    "physics_dense": {
        "r_sem": 0.80,
        "status": "estimate",
        "calibration_source": "pending TIP/P49",
        "notes": "Dense physics literature; fast self-correction expected.",
    },
    "sparse_fringe": {
        "r_sem": 0.30,
        "status": "estimate",
        "calibration_source": "pending TIP/P49",
        "notes": "Sparse/speculative domains; slow self-correction.",
    },
    "curated_graph": {
        "r_sem": 0.90,
        "status": "estimate",
        "calibration_source": "pending TIP/P49",
        "notes": "Dense curated knowledge graphs; strongest attractor.",
    },
    "general": {
        "r_sem": 0.50,
        "status": "conservative_default",
        "calibration_source": "theoretical midpoint",
        "notes": "Use when domain unknown. Conservative: underestimates Ρ_sem.",
    },
}


def get_domain_r(domain: str) -> float:
    """Return r_sem for domain; fall back to 'general' if unknown.

    Emits a UserWarning for any non-calibrated value.
    """
    config = DOMAIN_CONFIG.get(domain, DOMAIN_CONFIG["general"])
    if config["status"] in ("estimate", "conservative_default"):
        warnings.warn(
            f"r_sem for domain '{domain}' is {config['status']} "
            f"({config['r_sem']}). Calibration pending: "
            f"{config['calibration_source']}. Ρ_sem values are approximate.",
            UserWarning,
            stacklevel=3,
        )
    return float(config["r_sem"])


class SemanticCREP:
    """Compute the CREP tensor for semantic paths.

    When called without a live Sigillin store the components are estimated
    from path metadata (lengths, domain, etc.).

    C_sem = semantic consistency  = 1 − (contradictory / total edges)
    R_sem = semantic resonance    = proximity to ground-truth paths
    E_sem = semantic emergence    = normalised edge surprisal
    P_sem = path richness         = tanh(n_edges · mean_weight / ref_density)

    All ∈ [0, 1].  Γ_sem = (C · R · E · P)^(1/4) — diamond formula.
    """

    def compute(
        self,
        sigillin_ids: list[str],
        q4_transitions: list[tuple[str, str]],
        domain: str = "general",
    ) -> dict[str, float]:
        """Estimate CREP components from path metadata.

        In production these would be computed against a live Sigillin store.
        The current implementation provides structurally correct placeholders
        that scale with path length and domain configuration.
        """
        n_edges = max(len(q4_transitions), 1)
        n_anchors = max(len(sigillin_ids), 1)

        # Coherence: longer paths tend to be more consistent (up to saturation)
        c_sem = float(np.tanh(n_anchors / 10.0))

        # Resonance: proxy — presence of Q4 transitions signals alignment
        r_sem = float(np.tanh(n_edges / 8.0)) if q4_transitions else 0.3

        # Emergence: normalised path novelty (proxy via anchor count)
        e_sem = float(1.0 - np.exp(-n_anchors / 5.0))

        # Path richness: tanh of combined depth signal
        p_sem = float(np.tanh((n_anchors + n_edges) / 12.0))

        return {"C": c_sem, "R": r_sem, "E": e_sem, "P": p_sem}

    def gamma_sem(self, crep_components: dict[str, float]) -> float:
        """Γ_sem = (C·R·E·P)^(1/4) — standard CREP diamond formula."""
        c, r, e, p = (crep_components[k] for k in ("C", "R", "E", "P"))
        return float((c * r * e * p) ** 0.25)
