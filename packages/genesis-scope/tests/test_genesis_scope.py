"""Tests for genesis-scope Diamond interface and core components."""

from __future__ import annotations

import math
import pytest

from genesis_scope.constants import PHI, PHI_CBRT, KAPPA_DEFAULT, LAMBDA_DEFAULT
from genesis_scope.semantic_anchor import SemanticAnchor, GENESIS_ANCHORS
from genesis_scope.drift_model import DriftModel
from genesis_scope.crep_collaboration import CollaborationCREP
from genesis_scope.session_tracker import SessionTracker, SessionPoint
from genesis_scope.system import GenesisScope


# ─── Constants ───────────────────────────────────────────────────────────────

def test_phi_cbrt():
    assert abs(PHI_CBRT - 1.17480) < 1e-3


def test_phi_value():
    assert abs(PHI - 1.61803) < 1e-4


# ─── SemanticAnchor ──────────────────────────────────────────────────────────

def test_anchor_recall_entropy():
    anchor = SemanticAnchor("CREP", state_bits=128.0, anchor_bits=12.0)
    assert anchor.recall_entropy() == pytest.approx(116.0, abs=0.1)


def test_anchor_compression_ratio():
    anchor = SemanticAnchor("test", state_bits=100.0, anchor_bits=10.0)
    assert anchor.compression_ratio() == pytest.approx(10.0, abs=0.01)


def test_genesis_anchors_non_empty():
    assert len(GENESIS_ANCHORS) >= 4


def test_anchor_drift_reduction_positive():
    anchor = SemanticAnchor("x", state_bits=64.0, anchor_bits=8.0)
    assert anchor.drift_reduction(0.3, 0.8) > 0


# ─── DriftModel ──────────────────────────────────────────────────────────────

def test_drift_no_anchors_unstable():
    model = DriftModel(kappa=0.3, lambda_=0.8)
    # Without anchors, anchor_strength = 0, model is unstable
    assert not model.is_stable()


def test_drift_with_anchors_stable():
    model = DriftModel(kappa=0.3, lambda_=0.8)
    for anchor in GENESIS_ANCHORS:
        model.add_anchor(anchor)
    assert model.is_stable()


def test_drift_trajectory_length():
    model = DriftModel()
    for a in GENESIS_ANCHORS:
        model.add_anchor(a)
    traj = model.simulate(n_sessions=38)
    assert len(traj) == 38


def test_drift_trajectory_non_negative():
    model = DriftModel()
    traj = model.simulate(n_sessions=20)
    assert all(d >= 0 for d in traj)


# ─── CollaborationCREP ───────────────────────────────────────────────────────

def test_crep_gamma_geometric_mean():
    crep = CollaborationCREP(C=0.5, R=0.5, E=0.5, P=0.5)
    assert crep.gamma == pytest.approx(0.5, abs=1e-9)


def test_crep_gamma_zero_when_any_zero():
    crep = CollaborationCREP(C=0.0, R=1.0, E=1.0, P=1.0)
    assert crep.gamma == 0.0


def test_crep_regime_critical():
    crep = CollaborationCREP(C=0.72, R=0.65, E=0.80, P=0.55)
    assert crep.regime() == "critical"


def test_crep_invalid_raises():
    with pytest.raises(ValueError):
        CollaborationCREP(C=1.5, R=0.5, E=0.5, P=0.5)


def test_crep_from_session_metrics():
    crep = CollaborationCREP.from_session_metrics(
        context_overlap=0.7,
        anchor_hit_rate=0.6,
        topic_diversity=0.8,
        units_per_hour=5.0,
        max_units=10.0,
    )
    assert 0.0 < crep.gamma < 1.0


# ─── SessionTracker ──────────────────────────────────────────────────────────

def test_session_tracker_bootstrap():
    tracker = SessionTracker.from_package_history(list(range(17, 40)))
    assert len(tracker.trajectory()) == 23


def test_session_velocity_zero_single():
    tracker = SessionTracker()
    tracker.record(SessionPoint("P17", tau_a=100, tau_h=2.0, sigma=0.3, gamma_collab=0.4))
    assert tracker.velocity() == 0.0


def test_session_status_insufficient():
    tracker = SessionTracker()
    assert tracker.status() == "insufficient_data"


def test_session_gamma_trajectory_shape():
    tracker = SessionTracker.from_package_history(list(range(17, 30)))
    gammas = tracker.gamma_trajectory()
    assert len(gammas) == 13


# ─── GenesisScope Diamond Interface ─────────────────────────────────────────

@pytest.fixture
def scope():
    return GenesisScope(n_sessions=23)


def test_diamond_run_cycle(scope):
    result = scope.run_cycle()
    assert "drift_trajectory" in result
    assert "crep" in result
    assert "tracker" in result


def test_diamond_get_crep_state_has_gamma(scope):
    state = scope.get_crep_state()
    assert "gamma" in state
    assert 0.0 <= state["gamma"] <= 1.0


def test_diamond_get_utac_state(scope):
    state = scope.get_utac_state()
    assert "H" in state
    assert "Gamma" in state


def test_diamond_get_phase_events(scope):
    scope.run_cycle()
    events = scope.get_phase_events()
    assert isinstance(events, list)


def test_diamond_to_zenodo_record(scope):
    record = scope.to_zenodo_record()
    assert record["package"] == "genesis-scope"
    assert record["package_id"] == 39
    assert "doi" in record


def test_coherence_in_critical_regime(scope):
    g = scope.coherence_score()
    # Default params in critical collaboration regime [0.30, 0.80]
    assert 0.30 <= g <= 0.80


def test_anchor_count(scope):
    assert scope.anchor_count() >= len(GENESIS_ANCHORS)


def test_add_anchor_increases_count(scope):
    before = scope.anchor_count()
    scope.add_anchor("new_anchor", state_bits=50.0, anchor_bits=6.0)
    assert scope.anchor_count() == before + 1


def test_scope_report_keys(scope):
    report = scope.scope_report()
    for key in ("coherence_score", "drift_status", "anchor_count", "gamma_regime"):
        assert key in report
