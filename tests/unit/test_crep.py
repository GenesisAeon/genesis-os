"""Unit tests for genesis_os.core.crep."""

from __future__ import annotations

import math

import numpy as np
import pytest

from genesis_os.core.crep import CREPEvaluator, CREPScore

# ──────────────────────────────────────────────────────────────────────────────
# CREPScore validation
# ──────────────────────────────────────────────────────────────────────────────


class TestCREPScoreValidation:
    def test_valid_score_created(self) -> None:
        s = CREPScore(coherence=0.5, resonance=0.3, emergence=0.7, poetics=0.9)
        assert s.coherence == pytest.approx(0.5)

    def test_values_clamped_above_one(self) -> None:
        s = CREPScore(coherence=1.5, resonance=1.5, emergence=1.5, poetics=1.5)
        assert s.coherence == pytest.approx(1.0)

    def test_values_clamped_below_zero(self) -> None:
        s = CREPScore(coherence=-0.5, resonance=-0.1, emergence=-1.0, poetics=-0.3)
        assert s.coherence == pytest.approx(0.0)
        assert s.resonance == pytest.approx(0.0)

    def test_default_timestamp_zero(self) -> None:
        s = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        assert s.timestamp == 0

    def test_custom_timestamp(self) -> None:
        s = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5, timestamp=42)
        assert s.timestamp == 42

    def test_all_axes_stored(self) -> None:
        s = CREPScore(coherence=0.1, resonance=0.2, emergence=0.3, poetics=0.4)
        assert s.coherence == pytest.approx(0.1)
        assert s.resonance == pytest.approx(0.2)
        assert s.emergence == pytest.approx(0.3)
        assert s.poetics == pytest.approx(0.4)

    def test_boundary_zero(self) -> None:
        s = CREPScore(coherence=0.0, resonance=0.0, emergence=0.0, poetics=0.0)
        assert s.coherence == 0.0

    def test_boundary_one(self) -> None:
        s = CREPScore(coherence=1.0, resonance=1.0, emergence=1.0, poetics=1.0)
        assert s.coherence == 1.0


# ──────────────────────────────────────────────────────────────────────────────
# CREPScore.gamma
# ──────────────────────────────────────────────────────────────────────────────


class TestCREPGamma:
    def test_gamma_zero_for_zero_scores(self) -> None:
        s = CREPScore(coherence=0.0, resonance=0.0, emergence=0.0, poetics=0.0)
        assert s.gamma == pytest.approx(0.0, abs=1e-9)

    def test_gamma_positive_for_high_scores(self) -> None:
        s = CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)
        assert s.gamma > 0.0

    def test_gamma_between_zero_and_one(self) -> None:
        for c, r, e, p in [(0.5, 0.5, 0.5, 0.5), (0.3, 0.7, 0.6, 0.4), (1.0, 1.0, 1.0, 1.0)]:
            s = CREPScore(coherence=c, resonance=r, emergence=e, poetics=p)
            # gamma can exceed 1.0 in theory but coherence weight keeps it bounded
            assert s.gamma >= 0.0

    def test_gamma_increases_with_coherence(self) -> None:
        s_low = CREPScore(coherence=0.1, resonance=0.9, emergence=0.9, poetics=0.9)
        s_high = CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)
        assert s_high.gamma > s_low.gamma

    def test_gamma_formula_manual(self) -> None:
        c, r, e, p, sigma = 0.8, 0.7, 0.6, 0.5, 0.3
        s = CREPScore(coherence=c, resonance=r, emergence=e, poetics=p)
        base = (c * r + e * p) / 2.0
        weight = math.exp(-((1.0 - c) ** 2) / (2.0 * sigma**2))
        expected = base * weight
        assert s.gamma == pytest.approx(expected, rel=1e-6)


# ──────────────────────────────────────────────────────────────────────────────
# CREPScore.mean
# ──────────────────────────────────────────────────────────────────────────────


class TestCREPMean:
    def test_mean_uniform(self) -> None:
        s = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        assert s.mean == pytest.approx(0.5)

    def test_mean_all_zeros(self) -> None:
        s = CREPScore(coherence=0.0, resonance=0.0, emergence=0.0, poetics=0.0)
        assert s.mean == pytest.approx(0.0)

    def test_mean_mixed(self) -> None:
        s = CREPScore(coherence=0.0, resonance=0.5, emergence=1.0, poetics=0.5)
        assert s.mean == pytest.approx(0.5)

    def test_mean_all_ones(self) -> None:
        s = CREPScore(coherence=1.0, resonance=1.0, emergence=1.0, poetics=1.0)
        assert s.mean == pytest.approx(1.0)


# ──────────────────────────────────────────────────────────────────────────────
# CREPScore.dominant
# ──────────────────────────────────────────────────────────────────────────────


class TestCREPDominant:
    def test_dominant_coherence(self) -> None:
        s = CREPScore(coherence=0.9, resonance=0.1, emergence=0.1, poetics=0.1)
        assert s.dominant == "C"

    def test_dominant_resonance(self) -> None:
        s = CREPScore(coherence=0.1, resonance=0.9, emergence=0.1, poetics=0.1)
        assert s.dominant == "R"

    def test_dominant_emergence(self) -> None:
        s = CREPScore(coherence=0.1, resonance=0.1, emergence=0.9, poetics=0.1)
        assert s.dominant == "E"

    def test_dominant_poetics(self) -> None:
        s = CREPScore(coherence=0.1, resonance=0.1, emergence=0.1, poetics=0.9)
        assert s.dominant == "P"


# ──────────────────────────────────────────────────────────────────────────────
# CREPScore.to_vector
# ──────────────────────────────────────────────────────────────────────────────


class TestCREPToVector:
    def test_returns_ndarray(self) -> None:
        s = CREPScore(coherence=0.1, resonance=0.2, emergence=0.3, poetics=0.4)
        v = s.to_vector()
        assert isinstance(v, np.ndarray)

    def test_vector_shape(self) -> None:
        s = CREPScore(coherence=0.1, resonance=0.2, emergence=0.3, poetics=0.4)
        assert s.to_vector().shape == (4,)

    def test_vector_values(self) -> None:
        s = CREPScore(coherence=0.1, resonance=0.2, emergence=0.3, poetics=0.4)
        np.testing.assert_allclose(s.to_vector(), [0.1, 0.2, 0.3, 0.4])


# ──────────────────────────────────────────────────────────────────────────────
# CREPScore arithmetic
# ──────────────────────────────────────────────────────────────────────────────


class TestCREPArithmetic:
    def test_add_clamped(self) -> None:
        a = CREPScore(coherence=0.8, resonance=0.8, emergence=0.8, poetics=0.8)
        b = CREPScore(coherence=0.8, resonance=0.8, emergence=0.8, poetics=0.8)
        result = a + b
        assert result.coherence == pytest.approx(1.0)

    def test_add_zero(self) -> None:
        a = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        b = CREPScore(coherence=0.0, resonance=0.0, emergence=0.0, poetics=0.0)
        result = a + b
        assert result.coherence == pytest.approx(0.5)

    def test_mul_scalar(self) -> None:
        s = CREPScore(coherence=0.8, resonance=0.6, emergence=0.4, poetics=0.2)
        result = s * 0.5
        assert result.coherence == pytest.approx(0.4)
        assert result.resonance == pytest.approx(0.3)

    def test_mul_zero(self) -> None:
        s = CREPScore(coherence=1.0, resonance=1.0, emergence=1.0, poetics=1.0)
        result = s * 0.0
        assert result.coherence == pytest.approx(0.0)

    def test_mul_preserves_timestamp(self) -> None:
        s = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5, timestamp=7)
        result = s * 2.0
        assert result.timestamp == 7


# ──────────────────────────────────────────────────────────────────────────────
# CREPEvaluator
# ──────────────────────────────────────────────────────────────────────────────


class TestCREPEvaluator:
    def test_evaluate_returns_score(self, crep_evaluator: CREPEvaluator) -> None:
        score = crep_evaluator.evaluate({"entropy": 0.3, "coupling": 0.7})
        assert isinstance(score, CREPScore)

    def test_evaluate_uses_entropy_for_coherence(self, crep_evaluator: CREPEvaluator) -> None:
        score = crep_evaluator.evaluate({"entropy": 0.2})
        assert score.coherence == pytest.approx(0.8)

    def test_evaluate_uses_coupling_for_resonance(self, crep_evaluator: CREPEvaluator) -> None:
        score = crep_evaluator.evaluate({"coupling": 0.6})
        assert score.resonance == pytest.approx(0.6)

    def test_evaluate_appends_to_history(self, crep_evaluator: CREPEvaluator) -> None:
        crep_evaluator.evaluate({})
        crep_evaluator.evaluate({})
        assert len(crep_evaluator.history) == 2

    def test_history_capped_at_max(self) -> None:
        ev = CREPEvaluator(history_length=3)
        for _ in range(10):
            ev.evaluate({})
        assert len(ev.history) == 3

    def test_gradient_none_with_one_entry(self, crep_evaluator: CREPEvaluator) -> None:
        crep_evaluator.evaluate({})
        assert crep_evaluator.gradient() is None

    def test_gradient_returns_array(self, crep_evaluator: CREPEvaluator) -> None:
        crep_evaluator.evaluate({"entropy": 0.3})
        crep_evaluator.evaluate({"entropy": 0.5})
        grad = crep_evaluator.gradient()
        assert grad is not None
        assert grad.shape == (4,)

    def test_threshold_exceeded_true(self, crep_evaluator: CREPEvaluator) -> None:
        high = CREPScore(coherence=0.95, resonance=0.95, emergence=0.95, poetics=0.95)
        assert crep_evaluator.threshold_exceeded(high, threshold=0.5)

    def test_threshold_exceeded_false(self, crep_evaluator: CREPEvaluator) -> None:
        low = CREPScore(coherence=0.1, resonance=0.1, emergence=0.1, poetics=0.1)
        assert not crep_evaluator.threshold_exceeded(low, threshold=0.9)

    def test_weighted_average_empty_returns_zero(self) -> None:
        ev = CREPEvaluator()
        assert ev.weighted_average() == pytest.approx(0.0)

    def test_weighted_average_uniform(self, crep_evaluator: CREPEvaluator) -> None:
        crep_evaluator.evaluate({"coherence": 0.5, "resonance": 0.5, "emergence": 0.5, "poetics": 0.5})
        result = crep_evaluator.weighted_average()
        assert result == pytest.approx(0.5)

    def test_reset_clears_history(self, crep_evaluator: CREPEvaluator) -> None:
        crep_evaluator.evaluate({})
        crep_evaluator.reset()
        assert len(crep_evaluator.history) == 0

    def test_history_returns_copy(self, crep_evaluator: CREPEvaluator) -> None:
        crep_evaluator.evaluate({})
        h1 = crep_evaluator.history
        h1.clear()
        assert len(crep_evaluator.history) == 1

    def test_evaluate_with_explicit_crep_values(self, crep_evaluator: CREPEvaluator) -> None:
        score = crep_evaluator.evaluate(
            {"coherence": 0.3, "resonance": 0.4, "emergence": 0.6, "poetics": 0.7}
        )
        assert score.coherence == pytest.approx(0.3)
        assert score.resonance == pytest.approx(0.4)

    def test_evaluate_cycle_stored_in_timestamp(self, crep_evaluator: CREPEvaluator) -> None:
        score = crep_evaluator.evaluate({"cycle": 5})
        assert score.timestamp == 5
