"""Tests for ResilienceEigenrate."""

from __future__ import annotations

import math

import pytest

from resilience_core.eigenrate import ResilienceEigenrate


def test_lambda_star_zero_gamma() -> None:
    e = ResilienceEigenrate(r=1.0)
    assert e.compute(0.0) == pytest.approx(0.0, abs=1e-9)


def test_lambda_star_amoc() -> None:
    """AMOC: r=1.0, Γ=0.251 → |λ*| = tanh²(2.2·0.251) ≈ 0.252."""
    e = ResilienceEigenrate(r=1.0)
    lam = e.compute(0.251)
    assert 0.20 <= lam <= 0.32


def test_lambda_star_arctic() -> None:
    """Arctic: Γ=0.920 → high |λ*| (but crit_margin≈0 kills Ρ)."""
    e = ResilienceEigenrate(r=1.0)
    lam = e.compute(0.920)
    assert lam > 0.9


def test_recovery_time_finite() -> None:
    e = ResilienceEigenrate(r=1.0)
    assert math.isfinite(e.recovery_time(0.251))


def test_recovery_time_zero_gamma_is_inf() -> None:
    e = ResilienceEigenrate(r=1.0)
    assert math.isinf(e.recovery_time(0.0))


def test_nan_gamma_returns_zero() -> None:
    e = ResilienceEigenrate(r=1.0)
    assert e.compute(float("nan")) == 0.0
