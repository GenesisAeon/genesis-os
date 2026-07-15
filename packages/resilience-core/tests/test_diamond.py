"""Diamond interface contract tests for ResilienceCore."""

from __future__ import annotations

import pytest

from resilience_core.system import ResilienceCore


@pytest.fixture()
def core() -> ResilienceCore:
    return ResilienceCore(domain="test", r=1.0)


def test_crep_state_before_run_cycle_returns_none_gamma(core: ResilienceCore) -> None:
    state = core.get_crep_state()
    assert state["Gamma"] is None


def test_run_cycle_returns_required_keys(core: ResilienceCore) -> None:
    result = core.run_cycle(gamma=0.251)
    for key in ("rho", "lambda_star", "criticality_margin", "coupling_load",
                "near_collapse", "recovery_time"):
        assert key in result


def test_gamma_not_none_after_run_cycle(core: ResilienceCore) -> None:
    core.run_cycle(gamma=0.251)
    crep = core.get_crep_state()
    assert crep["Gamma"] is not None


def test_crep_gamma_in_unit_interval(core: ResilienceCore) -> None:
    core.run_cycle(gamma=0.251)
    crep = core.get_crep_state()
    assert 0.0 <= crep["Gamma"] <= 1.0


def test_utac_state_has_required_keys(core: ResilienceCore) -> None:
    core.run_cycle(gamma=0.251)
    utac = core.get_utac_state()
    for key in ("H", "H_star", "K_eff"):
        assert key in utac


def test_phase_events_list(core: ResilienceCore) -> None:
    core.run_cycle(gamma=0.251)
    events = core.get_phase_events()
    assert isinstance(events, list)


def test_zenodo_record_required_keys(core: ResilienceCore) -> None:
    zr = core.to_zenodo_record()
    for key in ("title", "description", "creators"):
        assert key in zr


def test_resilience_state_has_rho(core: ResilienceCore) -> None:
    core.run_cycle(gamma=0.251)
    res = core.get_resilience_state()
    assert "rho" in res
    assert isinstance(res["rho"], float)


def test_cascade_via_coupling_updates(core: ResilienceCore) -> None:
    result = core.run_cycle(
        gamma=0.900,
        coupling_updates={("external_a", "test"): 0.3, ("external_b", "test"): 0.3},
    )
    res = core.get_resilience_state()
    assert res["cascade_risk"] is True
