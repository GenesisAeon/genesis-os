"""Tests für genesis_os.mirror — Phase D."""

from __future__ import annotations

import pytest

from genesis_os.core.crep import CREPScore
from genesis_os.mirror.dual_detector import DualDetector, DualDetectorResult
from genesis_os.mirror.tension_metric import (
    CRITICAL_TENSION_THRESHOLD,
    REGENERATIVE_DAMPING_FACTOR,
    albedo_loss,
    compute_tension_metric,
    regenerative_noise_damping,
)


class TestTensionMetric:
    def test_tension_basic(self) -> None:
        t = compute_tension_metric(gamma_klima=0.7, q_ki=100.0, v_ice=1000.0)
        assert t == pytest.approx(0.7 * 100.0 / (1000.0 + 1e-6), rel=1e-5)

    def test_tension_zero_ice(self) -> None:
        t = compute_tension_metric(gamma_klima=0.7, q_ki=100.0, v_ice=0.0, epsilon=1e-6)
        assert t > 1e5

    def test_tension_scales_with_q_ki(self) -> None:
        t1 = compute_tension_metric(0.5, 50.0, 1000.0)
        t2 = compute_tension_metric(0.5, 100.0, 1000.0)
        assert t2 == pytest.approx(2.0 * t1, rel=1e-5)

    def test_tension_zero_gamma(self) -> None:
        t = compute_tension_metric(gamma_klima=0.0, q_ki=100.0, v_ice=1000.0)
        assert t == pytest.approx(0.0)


class TestAlbedoLoss:
    def test_albedo_loss_zero_ice(self) -> None:
        loss = albedo_loss(albedo_factor=1.0, v_ice=0.0, epsilon=1e-6)
        assert loss > 1e5

    def test_albedo_loss_large_ice(self) -> None:
        loss = albedo_loss(albedo_factor=1.0, v_ice=1e9)
        assert loss < 1e-8

    def test_albedo_loss_scales_with_factor(self) -> None:
        l1 = albedo_loss(1.0, 1000.0)
        l2 = albedo_loss(2.0, 1000.0)
        assert l2 == pytest.approx(2.0 * l1, rel=1e-5)


class TestRegenerativeDamping:
    def test_damping_inactive(self) -> None:
        eta = 0.25
        assert regenerative_noise_damping(eta, regenerative=False) == pytest.approx(eta)

    def test_damping_active(self) -> None:
        eta = 0.25
        damped = regenerative_noise_damping(eta, regenerative=True)
        assert damped == pytest.approx(eta / REGENERATIVE_DAMPING_FACTOR, rel=1e-5)

    def test_87_2_value(self) -> None:
        """87.2 — empirischer neuromorphic noise damping Faktor aus unified-mandala v0.3.1."""
        assert REGENERATIVE_DAMPING_FACTOR == pytest.approx(87.2, abs=0.01)

    def test_regenerative_reduces_noise(self) -> None:
        eta = 1.0
        damped = regenerative_noise_damping(eta, regenerative=True)
        assert damped < eta


class TestDualDetector:
    def _crep(self, gamma_val: float = 0.7) -> CREPScore:
        v = gamma_val**4
        return CREPScore(coherence=v**0.25, resonance=v**0.25, emergence=v**0.25, poetics=v**0.25)

    def test_stable_system(self) -> None:
        crep = CREPScore(coherence=0.8, resonance=0.8, emergence=0.8, poetics=0.8)
        detector = DualDetector(n_sde_runs=50, seed=42)
        H = 0.5
        result = detector.detect(H, crep, tension=0.0)
        assert isinstance(result, DualDetectorResult)
        assert result.stochastic_collapse_risk < 0.3

    def test_collapse_risk_near_zero(self) -> None:
        crep = CREPScore(coherence=0.05, resonance=0.05, emergence=0.05, poetics=0.05)
        detector = DualDetector(n_sde_runs=50, seed=0)
        result = detector.detect(H=0.01, crep=crep, tension=0.0)
        assert result.stochastic_collapse_risk > 0.3

    def test_tension_triggers_mirror(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        detector = DualDetector(n_sde_runs=20, seed=1)
        result = detector.detect(H=0.5, crep=crep, tension=10.0)
        assert result.mirror_triggered is True
        assert result.recommendation == "halt"

    def test_no_mirror_below_threshold(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        detector = DualDetector(n_sde_runs=20, seed=2)
        result = detector.detect(H=0.5, crep=crep, tension=1.0)
        assert result.mirror_triggered is False

    def test_regenerative_mode(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        det_normal = DualDetector(n_sde_runs=30, seed=5, regenerative=False)
        det_regen = DualDetector(n_sde_runs=30, seed=5, regenerative=True)
        assert det_regen.eta < det_normal.eta

    def test_recommendation_enum(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        detector = DualDetector(n_sde_runs=10, seed=7)
        result = detector.detect(H=0.5, crep=crep, tension=0.0)
        assert result.recommendation in ("continue", "monitor", "halt")

    def test_critical_threshold_constant(self) -> None:
        assert CRITICAL_TENSION_THRESHOLD == pytest.approx(5.0)
