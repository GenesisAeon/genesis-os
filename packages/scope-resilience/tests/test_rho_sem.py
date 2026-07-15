"""Tests for HallucinationRisk Ρ_sem computation."""

from __future__ import annotations

import warnings

import pytest

from scope_resilience.hallucination_risk import HallucinationRisk
from scope_resilience.domain_profile import DomainProfile


@pytest.fixture()
def risk() -> HallucinationRisk:
    return HallucinationRisk()


def test_rho_sem_zero_gamma(risk: HallucinationRisk) -> None:
    assert risk.compute_rho(0.0) == pytest.approx(0.0, abs=1e-9)


def test_rho_sem_moderate_gamma(risk: HallucinationRisk) -> None:
    rho = risk.compute_rho(0.5, r_sem=1.0)
    assert 0.0 < rho < 1.0


def test_rho_sem_uses_domain_profile(risk: HallucinationRisk) -> None:
    profile_high = DomainProfile("high", gamma=0.5, r=2.0, r_status="calibrated")
    profile_low = DomainProfile("low", gamma=0.5, r=0.5, r_status="calibrated")
    rho_high = risk.compute_rho(0.5, domain_profile=profile_high)
    rho_low = risk.compute_rho(0.5, domain_profile=profile_low)
    assert rho_high > rho_low


def test_drift_reduces_rho(risk: HallucinationRisk) -> None:
    rho_static = risk.compute_rho(0.5, r_sem=1.0, d_gamma_dt=0.0)
    rho_drifting = risk.compute_rho(0.5, r_sem=1.0, d_gamma_dt=0.09)
    assert rho_drifting < rho_static


def test_drift_above_critical_zeroes_rho(risk: HallucinationRisk) -> None:
    rho = risk.compute_rho(0.5, r_sem=1.0, d_gamma_dt=0.15)
    assert rho == pytest.approx(0.0, abs=1e-9)


def test_classify_safe(risk: HallucinationRisk) -> None:
    level, _ = risk.classify_risk(0.80)
    assert level == "safe"


def test_classify_moderate(risk: HallucinationRisk) -> None:
    level, _ = risk.classify_risk(0.55)
    assert level == "moderate"


def test_classify_high_risk(risk: HallucinationRisk) -> None:
    level, _ = risk.classify_risk(0.25)
    assert level == "high_risk"


def test_classify_critical(risk: HallucinationRisk) -> None:
    level, _ = risk.classify_risk(0.05)
    assert level == "critical"
