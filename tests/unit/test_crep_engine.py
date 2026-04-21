"""Tests for genesis_os.core.crep_engine — enhanced CREP metrics."""

from __future__ import annotations

import math

import numpy as np
import pytest

from genesis_os.core.crep import CREPScore
from genesis_os.core.crep_engine import (
    CREP_THRESHOLDS,
    EmpiricalCREPEvaluator,
    compute_coherence,
    compute_emergence,
    compute_gamma,
    compute_poetics,
    compute_resonance,
    governance_level,
)


# ---------------------------------------------------------------------------
# Gamma (geometric mean)
# ---------------------------------------------------------------------------


class TestComputeGamma:
    def test_all_ones(self) -> None:
        assert compute_gamma(1.0, 1.0, 1.0, 1.0) == pytest.approx(1.0)

    def test_all_zeros(self) -> None:
        assert compute_gamma(0.0, 0.0, 0.0, 0.0) == pytest.approx(0.0)

    def test_one_zero_component(self) -> None:
        # If any component is 0, Γ = 0
        assert compute_gamma(1.0, 1.0, 0.0, 1.0) == pytest.approx(0.0)

    def test_equal_components(self) -> None:
        v = 0.5
        assert compute_gamma(v, v, v, v) == pytest.approx(v)

    def test_clamped_above_one(self) -> None:
        # Values > 1 should be clamped before computing
        result = compute_gamma(2.0, 2.0, 2.0, 2.0)
        assert result == pytest.approx(1.0)

    def test_clamped_below_zero(self) -> None:
        result = compute_gamma(-0.5, 0.5, 0.5, 0.5)
        assert result == pytest.approx(0.0)

    def test_typical_values(self) -> None:
        result = compute_gamma(0.8, 0.7, 0.6, 0.9)
        expected = (0.8 * 0.7 * 0.6 * 0.9) ** 0.25
        assert result == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# Coherence
# ---------------------------------------------------------------------------


class TestComputeCoherence:
    def test_returns_unit_interval(self) -> None:
        rng = np.random.default_rng(42)
        ts = rng.normal(0, 1, 100)
        C = compute_coherence(ts)
        assert 0.0 <= C <= 1.0

    def test_short_series_returns_half(self) -> None:
        C = compute_coherence(np.array([1.0]))
        assert C == pytest.approx(0.5)

    def test_periodic_signal_high_coherence(self) -> None:
        t = np.linspace(0, 10 * np.pi, 500)
        ts = np.sin(t)
        C = compute_coherence(ts)
        assert C > 0.5

    def test_no_crossings_returns_half(self) -> None:
        # Monotonic signal — no zero crossings
        ts = np.linspace(1, 10, 50)
        C = compute_coherence(ts)
        assert C == pytest.approx(0.5)

    def test_constant_signal(self) -> None:
        ts = np.ones(50)
        C = compute_coherence(ts)
        assert 0.0 <= C <= 1.0


# ---------------------------------------------------------------------------
# Resonance
# ---------------------------------------------------------------------------


class TestComputeResonance:
    def test_no_f_res_returns_one(self) -> None:
        t = np.linspace(0, 4 * np.pi, 100)
        ts = np.sin(t)
        R = compute_resonance(ts, f_res=None)
        assert R == pytest.approx(1.0)

    def test_short_series_returns_half(self) -> None:
        R = compute_resonance(np.array([1.0, 2.0]))
        assert R == pytest.approx(0.5)

    def test_returns_unit_interval(self) -> None:
        rng = np.random.default_rng(7)
        ts = rng.normal(0, 1, 200)
        R = compute_resonance(ts, f_res=0.1, delta_f=0.05)
        assert 0.0 <= R <= 1.0

    def test_f_res_at_peak_near_one(self) -> None:
        t = np.arange(200)
        ts = np.sin(2 * np.pi * 0.1 * t)  # f=0.1
        # Peak is at 0.1; set f_res=0.1 with small delta_f
        R = compute_resonance(ts, f_res=0.1, delta_f=0.05)
        assert R > 0.5

    def test_f_res_far_from_peak_low_resonance(self) -> None:
        t = np.arange(200)
        ts = np.sin(2 * np.pi * 0.05 * t)  # f=0.05
        R = compute_resonance(ts, f_res=0.45, delta_f=0.01)
        assert R < 0.5


# ---------------------------------------------------------------------------
# Emergence
# ---------------------------------------------------------------------------


class TestComputeEmergence:
    def test_returns_unit_interval(self) -> None:
        rng = np.random.default_rng(3)
        comps = rng.normal(0, 1, (4, 100))
        out = rng.normal(0, 1, 100)
        E = compute_emergence(comps, out)
        assert 0.0 <= E <= 1.0

    def test_short_time_series_returns_half(self) -> None:
        E = compute_emergence(np.array([[1.0]]), np.array([1.0]))
        assert E == pytest.approx(0.5)

    def test_constant_output_zero_emergence(self) -> None:
        comps = np.random.default_rng(0).normal(0, 1, (3, 50))
        out = np.ones(50)
        E = compute_emergence(comps, out)
        assert E == pytest.approx(0.0, abs=1e-6)

    def test_transposed_input(self) -> None:
        rng = np.random.default_rng(5)
        comps = rng.normal(0, 1, (100, 4))  # (T, n_components)
        out = rng.normal(0, 1, 100)
        E = compute_emergence(comps, out)
        assert 0.0 <= E <= 1.0


# ---------------------------------------------------------------------------
# Poetics (permutation entropy)
# ---------------------------------------------------------------------------


class TestComputePoetics:
    def test_returns_unit_interval(self) -> None:
        rng = np.random.default_rng(42)
        ts = rng.normal(0, 1, 200)
        P = compute_poetics(ts, order=3)
        assert 0.0 <= P <= 1.0

    def test_random_signal_high_entropy(self) -> None:
        rng = np.random.default_rng(42)
        ts = rng.normal(0, 1, 500)
        P = compute_poetics(ts, order=3)
        assert P > 0.7

    def test_monotonic_signal_low_entropy(self) -> None:
        ts = np.arange(50, dtype=float)
        P = compute_poetics(ts, order=3)
        # Monotone → single pattern → H_perm = 0 → P = 0
        assert P == pytest.approx(0.0, abs=1e-6)

    def test_short_series_returns_half(self) -> None:
        P = compute_poetics(np.array([1.0, 2.0]), order=3)
        assert P == pytest.approx(0.5)

    def test_order_2(self) -> None:
        rng = np.random.default_rng(11)
        ts = rng.normal(0, 1, 100)
        P = compute_poetics(ts, order=2)
        assert 0.0 <= P <= 1.0

    def test_order_clamped_at_2(self) -> None:
        rng = np.random.default_rng(11)
        ts = rng.normal(0, 1, 100)
        P_order1 = compute_poetics(ts, order=1)  # clamped to 2
        P_order2 = compute_poetics(ts, order=2)
        assert P_order1 == pytest.approx(P_order2)


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------


class TestGovernanceLevel:
    def test_safe(self) -> None:
        assert governance_level(0.3) == "safe"

    def test_informational(self) -> None:
        assert governance_level(0.65) == "informational"

    def test_warning(self) -> None:
        assert governance_level(0.75) == "warning"

    def test_reviewer(self) -> None:
        assert governance_level(0.85) == "reviewer"

    def test_critical(self) -> None:
        assert governance_level(0.95) == "critical"

    def test_exactly_at_threshold(self) -> None:
        assert governance_level(0.9) == "critical"
        assert governance_level(0.8) == "reviewer"
        assert governance_level(0.7) == "warning"
        assert governance_level(0.6) == "informational"

    def test_thresholds_constant(self) -> None:
        assert CREP_THRESHOLDS["informational"] == pytest.approx(0.6)
        assert CREP_THRESHOLDS["warning"] == pytest.approx(0.7)
        assert CREP_THRESHOLDS["reviewer"] == pytest.approx(0.8)
        assert CREP_THRESHOLDS["critical"] == pytest.approx(0.9)


# ---------------------------------------------------------------------------
# EmpiricalCREPEvaluator
# ---------------------------------------------------------------------------


class TestEmpiricalCREPEvaluator:
    def setup_method(self) -> None:
        self.evaluator = EmpiricalCREPEvaluator(permutation_order=3)

    def test_evaluate_from_signals_returns_crep_score(self) -> None:
        rng = np.random.default_rng(42)
        sig = rng.normal(0, 1, 100)
        score = self.evaluator.evaluate_from_signals(sig)
        assert isinstance(score, CREPScore)

    def test_evaluate_all_components_unit_interval(self) -> None:
        rng = np.random.default_rng(42)
        sig = rng.normal(0, 1, 100)
        score = self.evaluator.evaluate_from_signals(sig)
        assert 0.0 <= score.coherence <= 1.0
        assert 0.0 <= score.resonance <= 1.0
        assert 0.0 <= score.emergence <= 1.0
        assert 0.0 <= score.poetics <= 1.0

    def test_evaluate_with_components(self) -> None:
        rng = np.random.default_rng(7)
        sig = rng.normal(0, 1, 100)
        comps = rng.normal(0, 1, (3, 100))
        score = self.evaluator.evaluate_from_signals(sig, components=comps, timestamp=5)
        assert score.timestamp == 5
        assert 0.0 <= score.emergence <= 1.0

    def test_compute_gamma_from_signal(self) -> None:
        rng = np.random.default_rng(1)
        sig = rng.normal(0, 1, 100)
        gamma = self.evaluator.compute_gamma_from_signal(sig)
        assert 0.0 <= gamma <= 1.0

    def test_assess_governance_dict_keys(self) -> None:
        result = self.evaluator.assess_governance(0.85)
        assert "level" in result
        assert "gamma" in result
        assert "action" in result
        assert result["level"] == "reviewer"

    def test_assess_governance_safe(self) -> None:
        result = self.evaluator.assess_governance(0.2)
        assert result["level"] == "safe"
        assert "no action" in str(result["action"])

    def test_assess_governance_critical(self) -> None:
        result = self.evaluator.assess_governance(0.95)
        assert result["level"] == "critical"
        assert "halt" in str(result["action"])
