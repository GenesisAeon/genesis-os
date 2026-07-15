"""Diamond interface contract tests for ScopeResilience."""

from __future__ import annotations

import pytest

from scope_resilience.system import ScopeResilience


@pytest.fixture()
def sr() -> ScopeResilience:
    return ScopeResilience(domain="general")


def test_crep_state_before_run_cycle_returns_none_gamma(sr: ScopeResilience) -> None:
    state = sr.get_crep_state()
    assert state["Gamma"] is None


def test_run_cycle_returns_required_keys(sr: ScopeResilience) -> None:
    result = sr.run_cycle("AMOC tipping point")
    for key in ("gamma_sem", "rho_sem", "risk_level", "d_gamma_dt", "needs_regrounding"):
        assert key in result


def test_gamma_not_none_after_run_cycle(sr: ScopeResilience) -> None:
    sr.run_cycle("test topic")
    crep = sr.get_crep_state()
    assert crep["Gamma"] is not None


def test_crep_gamma_in_unit_interval(sr: ScopeResilience) -> None:
    sr.run_cycle("test topic", sigillin_ids=["s1", "s2"])
    crep = sr.get_crep_state()
    assert 0.0 <= crep["Gamma"] <= 1.0


def test_utac_state_has_required_keys(sr: ScopeResilience) -> None:
    sr.run_cycle("test")
    utac = sr.get_utac_state()
    for key in ("H", "H_star", "K_eff"):
        assert key in utac


def test_phase_events_list(sr: ScopeResilience) -> None:
    sr.run_cycle("test")
    events = sr.get_phase_events()
    assert isinstance(events, list)


def test_zenodo_record_required_keys(sr: ScopeResilience) -> None:
    zr = sr.to_zenodo_record()
    for key in ("title", "description", "creators"):
        assert key in zr


def test_resilience_state_implemented(sr: ScopeResilience) -> None:
    sr.run_cycle("test")
    res = sr.get_resilience_state()
    assert res.get("implemented") is True
    assert "rho_sem" in res


def test_get_semantic_path_returns_path(sr: ScopeResilience) -> None:
    from scope_resilience.semantic_path import SemanticPath
    path = sr.get_semantic_path("quantum decoherence")
    assert isinstance(path, SemanticPath)
    assert path.topic == "quantum decoherence"


def test_to_llms_txt_contains_topic(sr: ScopeResilience) -> None:
    txt = sr.to_llms_txt("AMOC")
    assert "AMOC" in txt
    assert "Resilience" in txt


def test_drift_detection_across_steps(sr: ScopeResilience) -> None:
    # Run multiple cycles; monitor should track drift
    sr.run_cycle("step1", sigillin_ids=["a"])
    result = sr.run_cycle("step2", sigillin_ids=["a", "b", "c", "d", "e", "f", "g"])
    assert isinstance(result["d_gamma_dt"], float)
