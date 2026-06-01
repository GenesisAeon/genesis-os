"""GenesisScope — Diamond interface for the genesis-scope package.

The scope is the cartographer of the shared Human-AI space.
It coordinates DriftModel, CollaborationCREP, SemanticAnchor,
and SessionTracker into a single coherent system.

Diamond interface (required by genesis-os propagation script):
    run_cycle()        → dict
    get_crep_state()   → dict  (must contain 'gamma' key)
    get_utac_state()   → dict
    get_phase_events() → list
    to_zenodo_record() → dict
"""

from __future__ import annotations

from typing import Any

import numpy as np

from genesis_scope.constants import (
    KAPPA_DEFAULT,
    LAMBDA_DEFAULT,
    GAMMA_COLLAB_MIN,
    GAMMA_COLLAB_MAX,
    V_RIG_KM_S,
)
from genesis_scope.crep_collaboration import CollaborationCREP
from genesis_scope.drift_model import DriftModel
from genesis_scope.semantic_anchor import SemanticAnchor, GENESIS_ANCHORS
from genesis_scope.session_tracker import SessionTracker


class GenesisScope:
    """Semantic coordinate system for Human-AI collaboration.

    Integrates all genesis-scope components and exposes the
    Diamond interface required by genesis-os package registry.

    Args:
        n_sessions:  Number of historical sessions to bootstrap from
                     (default 38, representing P17–P38 of GenesisAeon).
        kappa:       Drift rate parameter.
        lambda_:     Anchor damping coefficient.
    """

    def __init__(
        self,
        n_sessions: int = 38,
        kappa: float = KAPPA_DEFAULT,
        lambda_: float = LAMBDA_DEFAULT,
    ) -> None:
        self.n_sessions = n_sessions

        # Drift model with default GenesisAeon anchors
        self._drift = DriftModel(kappa=kappa, lambda_=lambda_)
        for anchor in GENESIS_ANCHORS:
            self._drift.add_anchor(anchor)

        # Collaboration CREP — default session metrics
        self._crep = CollaborationCREP(C=0.72, R=0.65, E=0.80, P=0.55)

        # Session tracker bootstrapped from package history
        package_ids = list(range(17, 17 + n_sessions))
        self._tracker = SessionTracker()
        self._tracker = SessionTracker.from_package_history(package_ids)

        # Phase events = sessions where drift exceeded v_RIG
        self._phase_events: list[dict[str, Any]] = []

    # ─── Diamond Interface ───────────────────────────────────────────────────

    def run_cycle(self, n_sessions: int | None = None) -> dict[str, Any]:
        """Run one scope cycle: simulate drift, evaluate CREP, detect events.

        Args:
            n_sessions: Override number of sessions to simulate.

        Returns:
            Summary dict with drift trajectory, CREP state, and phase events.
        """
        n = n_sessions or self.n_sessions
        trajectory = self._drift.simulate(n_sessions=n)

        # Detect phase events (drift spikes above fixed_point * 2)
        self._phase_events = []
        threshold = self._drift.fixed_point() * 2.0
        for i, d in enumerate(trajectory):
            if d > threshold and threshold > 0:
                self._phase_events.append({
                    "session": i,
                    "drift": float(d),
                    "type": "drift_spike",
                })

        return {
            "drift_trajectory": trajectory.tolist(),
            "drift_fixed_point": self._drift.fixed_point(),
            "is_stable": self._drift.is_stable(),
            "n_phase_events": len(self._phase_events),
            "crep": self._crep.to_dict(),
            "tracker": self._tracker.summary(),
        }

    def get_crep_state(self) -> dict[str, Any]:
        """Return CREP state dict with mandatory 'gamma' key."""
        state = self._crep.to_dict()
        # Ensure 'gamma' is present at top level (Diamond requirement)
        state["gamma"] = self._crep.gamma
        state["gamma_regime_expected"] = f"[{GAMMA_COLLAB_MIN}, {GAMMA_COLLAB_MAX}]"
        return state

    def get_utac_state(self) -> dict[str, Any]:
        """Return UTAC-analogue state: drift ODE maps to H(t) dynamics."""
        drift_summary = self._drift.summary()
        return {
            # In scope, drift D maps to UTAC's H (population/density)
            "H": self._drift.fixed_point(),
            "K": self._drift.d0,               # carrying capacity = initial drift
            "r": self._drift.kappa,             # growth rate = drift rate
            "sigma": self._drift.lambda_,       # coupling = anchor damping
            "Gamma": self._crep.gamma,
            "drift_stable": drift_summary["is_stable"],
        }

    def get_phase_events(self) -> list[dict[str, Any]]:
        """Return list of detected drift-spike phase events."""
        return list(self._phase_events)

    def to_zenodo_record(self) -> dict[str, Any]:
        return {
            "package": "genesis-scope",
            "version": "1.0.0",
            "package_id": 39,
            "doi": "10.5281/zenodo.17472834",
            "domain": "meta-collaboration",
            "description": (
                "Semantic coordinate system for Human-AI collaboration. "
                "Externalises shared geometry as executable code."
            ),
            "authors": ["Johann Römer", "MOR Research Collective"],
            "gamma_collab": self._crep.gamma,
            "drift_fixed_point": self._drift.fixed_point(),
            "n_anchors": len(GENESIS_ANCHORS),
            "connections": [
                "vrig-cosmological (P31): v_RIG as drift-speed threshold",
                "sa-sv-duality (P36): S_A/S_V as session entropy",
                "sigillin: Sigillin == SemanticAnchor",
                "HexaAgent (P40): agent roles in scope-space",
                "beta-clustering-utac (P32): Phi^(1/3) scales coordinate ratios",
            ],
        }

    # ─── Extended Interface ──────────────────────────────────────────────────

    def coherence_score(self) -> float:
        """Gamma_collab ∈ [0, 1] — current collaboration coherence."""
        return self._crep.gamma

    def drift_status(self) -> str:
        """'stable' | 'drifting' | 'anchored' | 'insufficient_data'."""
        return self._tracker.status()

    def anchor_count(self) -> int:
        """Number of active semantic anchors."""
        return len(self._drift._anchors)

    def add_anchor(self, name: str, state_bits: float = 64.0, anchor_bits: float = 8.0) -> None:
        """Register a new semantic anchor (Sigillin) dynamically."""
        anchor = SemanticAnchor(name=name, state_bits=state_bits, anchor_bits=anchor_bits)
        self._drift.add_anchor(anchor)

    def update_crep(self, C: float, R: float, E: float, P: float) -> None:
        """Update collaboration CREP from observed session metrics."""
        self._crep = CollaborationCREP(C=C, R=R, E=E, P=P)

    def scope_report(self) -> dict[str, Any]:
        """Full human-readable scope report."""
        cycle = self.run_cycle()
        return {
            "coherence_score": self.coherence_score(),
            "drift_status": self.drift_status(),
            "anchor_count": self.anchor_count(),
            "gamma_regime": self._crep.regime(),
            "v_rig_warning": self._tracker.is_drifting(),
            "v_rig_km_s": V_RIG_KM_S,
            "is_critical": self._crep.is_critical(),
            "sessions_tracked": len(self._tracker.trajectory()),
            "cycle": cycle,
        }
