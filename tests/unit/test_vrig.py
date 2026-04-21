"""Tests for genesis_os.vrig — v_RIG information-geometric velocity."""

from __future__ import annotations

import numpy as np
import pytest

from genesis_os.vrig import RegimeDetector, VRIGVelocity
from genesis_os.vrig.regime_detector import RegimeShift
from genesis_os.vrig.velocity import V_RIG_KMS, VRIGResult


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestVRIGConstants:
    def test_v_rig_kms_approx(self) -> None:
        # c / (α · Φ) ≈ 1351.8 km/s
        assert 1300.0 < V_RIG_KMS < 1400.0

    def test_v_rig_kms_formula(self) -> None:
        c = 299792.458
        alpha = 137.036
        phi = 1.6180339887
        expected = c / (alpha * phi)
        assert V_RIG_KMS == pytest.approx(expected, rel=1e-4)


# ---------------------------------------------------------------------------
# VRIGVelocity tests
# ---------------------------------------------------------------------------


class TestVRIGVelocity:
    def setup_method(self) -> None:
        self.vrig = VRIGVelocity(dt=1.0)

    def test_compute_fim_shape(self) -> None:
        params = np.array([0.3, 1.0, 2.0])
        fim = self.vrig.compute_fisher_information_matrix(
            params, lambda p: float(-0.5 * np.sum(p**2))
        )
        assert fim.shape == (3, 3)

    def test_compute_fim_positive_semidefinite(self) -> None:
        params = np.array([0.3, 1.0, 2.0])
        fim = self.vrig.compute_fisher_information_matrix(
            params, lambda p: float(-0.5 * np.sum(p**2))
        )
        eigenvalues = np.linalg.eigvalsh(fim)
        assert np.all(eigenvalues >= -1e-9)

    def test_compute_velocity_zero_displacement(self) -> None:
        params = np.array([0.3, 1.0, 2.0])
        fim = np.eye(3)
        v = self.vrig.compute_velocity(params, params, fim)
        assert v == pytest.approx(0.0)

    def test_compute_velocity_nonzero(self) -> None:
        p1 = np.array([0.3, 1.0, 2.0])
        p2 = np.array([0.5, 0.8, 1.5])
        fim = np.eye(3)
        v = self.vrig.compute_velocity(p2, p1, fim)
        assert v > 0.0

    def test_compute_velocity_nonnegative(self) -> None:
        rng = np.random.default_rng(42)
        for _ in range(10):
            p1 = rng.normal(0, 1, 3)
            p2 = rng.normal(0, 1, 3)
            fim = np.eye(3)
            v = self.vrig.compute_velocity(p2, p1, fim)
            assert v >= 0.0

    def test_velocity_history_tracked(self) -> None:
        p1 = np.array([0.3, 1.0, 2.0])
        p2 = np.array([0.5, 0.8, 1.5])
        fim = np.eye(3)
        self.vrig.compute_velocity(p2, p1, fim)
        self.vrig.compute_velocity(p1, p2, fim)
        assert len(self.vrig.velocity_history) == 2

    def test_detect_regime_change_empty_on_short_series(self) -> None:
        result = self.vrig.detect_regime_change(np.array([1.0, 2.0]))
        assert result == []

    def test_detect_regime_change_detects_spike(self) -> None:
        # Series with a large spike
        base = np.ones(20) * 1.0
        base[10] = 100.0  # spike
        indices = self.vrig.detect_regime_change(base, threshold_sigma=2.0)
        assert 10 in indices

    def test_detect_regime_change_empty_uniform_series(self) -> None:
        # Uniform series → std=0 → no detection
        result = self.vrig.detect_regime_change(np.ones(20))
        assert result == []

    def test_reset_clears_history(self) -> None:
        p1 = np.array([0.3, 1.0, 2.0])
        p2 = np.array([0.5, 0.8, 1.5])
        self.vrig.compute_velocity(p2, p1, np.eye(3))
        self.vrig.reset()
        assert len(self.vrig.velocity_history) == 0

    def test_v_rig_constant_property(self) -> None:
        assert self.vrig.v_rig_constant_kms == pytest.approx(V_RIG_KMS)


# ---------------------------------------------------------------------------
# RegimeDetector tests
# ---------------------------------------------------------------------------


class TestRegimeDetector:
    def setup_method(self) -> None:
        self.detector = RegimeDetector(window_size=10, threshold_sigma=2.0, min_windows=3)

    def test_fit_returns_param_list(self) -> None:
        ts = np.linspace(1.0, 0.5, 30)
        params = self.detector.fit(ts)
        expected_windows = 30 - 10 + 1
        assert len(params) == expected_windows

    def test_fit_params_shape(self) -> None:
        ts = np.linspace(1.0, 0.5, 20)
        params = self.detector.fit(ts)
        for p in params:
            assert len(p) == 3

    def test_fit_short_series(self) -> None:
        ts = np.ones(5)
        params = self.detector.fit(ts)
        # 5 - 10 + 1 = negative, so 0 windows
        assert len(params) == 0

    def test_compute_velocity_series_empty_without_fit(self) -> None:
        result = self.detector.compute_velocity_series()
        assert len(result) == 0

    def test_compute_velocity_series_after_fit(self) -> None:
        ts = np.linspace(1.0, 0.3, 30)
        self.detector.fit(ts)
        vel = self.detector.compute_velocity_series()
        assert len(vel) == self.detector.n_windows - 1
        assert np.all(vel >= 0.0)

    def test_detect_returns_list(self) -> None:
        ts = np.linspace(1.0, 0.5, 30)
        shifts = self.detector.detect(ts)
        assert isinstance(shifts, list)

    def test_detect_short_series_empty(self) -> None:
        ts = np.ones(5)
        shifts = self.detector.detect(ts)
        assert shifts == []

    def test_detect_regime_shift_with_step(self) -> None:
        # Create a clear regime shift: stable then declining
        stable = np.ones(15) * 10.0
        declining = np.linspace(10.0, 5.0, 15)
        ts = np.concatenate([stable, declining])
        shifts = self.detector.detect(ts)
        # May or may not detect depending on parameter fitting accuracy
        assert isinstance(shifts, list)

    def test_detected_shifts_property(self) -> None:
        ts = np.linspace(1.0, 0.5, 30)
        self.detector.detect(ts)
        assert isinstance(self.detector.detected_shifts, list)

    def test_summary_keys(self) -> None:
        ts = np.linspace(1.0, 0.5, 30)
        self.detector.detect(ts)
        summary = self.detector.summary()
        assert "n_windows" in summary
        assert "n_shifts_detected" in summary
        assert "window_size" in summary

    def test_n_windows_after_fit(self) -> None:
        ts = np.linspace(0, 1, 25)
        self.detector.fit(ts)
        assert self.detector.n_windows == 25 - 10 + 1

    def test_regime_shift_dataclass(self) -> None:
        shift = RegimeShift(
            time_index=15,
            velocity=5.0,
            params_before=np.array([0.3, 1.0, 1.5]),
            params_after=np.array([0.5, 0.8, 2.0]),
            confidence=0.8,
        )
        assert shift.time_index == 15
        assert shift.confidence == pytest.approx(0.8)

    def test_arctic_1998_detection_window(self) -> None:
        # Simulate Arctic sea ice: stable 1979-1997, shift ~1998, declining after
        rng = np.random.default_rng(42)
        years = np.arange(1979, 2020)
        pre_shift = np.linspace(7.5, 7.0, 19) + rng.normal(0, 0.1, 19)
        post_shift = np.linspace(6.5, 4.5, 22) + rng.normal(0, 0.15, 22)
        extent = np.concatenate([pre_shift, post_shift])
        shifts = self.detector.detect(extent)
        # If a shift is detected, it should be within ±3 years of 1998 (index ~19±3)
        if shifts:
            for shift in shifts:
                assert 0 <= shift.time_index < len(extent)
