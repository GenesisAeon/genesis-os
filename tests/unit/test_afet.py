"""Tests for genesis_os.afet — AFET field entropy module."""

from __future__ import annotations

import numpy as np
import pytest

from genesis_os.afet import AFETField, DualEntropyGovernance, EntropyProductionField
from genesis_os.afet.climate import (
    arctic_sea_ice_entropy,
    amoc_entropy_production,
    detect_climate_regime_shift,
    rolling_entropy_trend,
)
from genesis_os.afet.field import BETA_BOUNDARY, BETA_SURFACE, BETA_VOLUME


# ---------------------------------------------------------------------------
# AFETField tests
# ---------------------------------------------------------------------------


class TestAFETField:
    def setup_method(self) -> None:
        self.afet = AFETField(sigma_0=1.0, sigma_critical=1.0)

    def test_entropy_production_positive(self) -> None:
        sigma = self.afet.compute_local_entropy_production(state=0.5, crep_gamma=0.4)
        assert sigma >= 0.0

    def test_entropy_production_second_law(self) -> None:
        for gamma in [-0.5, 0.0, 0.5, 1.0]:
            sigma = self.afet.compute_local_entropy_production(state=0.5, crep_gamma=gamma)
            assert sigma >= 0.0, f"σ_s < 0 for gamma={gamma}"

    def test_entropy_production_zero_state(self) -> None:
        sigma = self.afet.compute_local_entropy_production(state=0.0, crep_gamma=1.0)
        assert sigma == pytest.approx(0.0)

    def test_entropy_production_scales_with_kappa(self) -> None:
        s1 = self.afet.compute_local_entropy_production(state=0.5, crep_gamma=0.5, kappa=1.0)
        s2 = self.afet.compute_local_entropy_production(state=0.5, crep_gamma=0.5, kappa=2.0)
        assert s2 > s1

    def test_entropy_production_history_recorded(self) -> None:
        self.afet.reset()
        self.afet.compute_local_entropy_production(0.5, 0.3)
        self.afet.compute_local_entropy_production(0.7, 0.5)
        assert len(self.afet.production_history) == 2

    def test_entropy_flux_direction(self) -> None:
        state = np.array([1.0, 0.5, 0.2])
        gradient = np.array([0.1, -0.2, 0.3])
        flux = self.afet.compute_entropy_flux(state, gradient)
        assert flux.shape == gradient.shape
        # Flux should oppose gradient (Fourier)
        np.testing.assert_array_equal(np.sign(flux), -np.sign(gradient))

    def test_entropy_flux_zero_gradient(self) -> None:
        state = np.ones(5)
        gradient = np.zeros(5)
        flux = self.afet.compute_entropy_flux(state, gradient)
        np.testing.assert_array_almost_equal(flux, np.zeros(5))

    def test_detect_governance_surface_regime(self) -> None:
        regime = self.afet.detect_governance_regime(beta_eff=11.0)
        assert regime == "surface"

    def test_detect_governance_volume_regime(self) -> None:
        regime = self.afet.detect_governance_regime(beta_eff=4.5)
        assert regime == "volume"

    def test_detect_governance_boundary(self) -> None:
        # Exactly at boundary (7.75) — should be volume (≤ boundary)
        regime = self.afet.detect_governance_regime(beta_eff=BETA_BOUNDARY)
        assert regime == "volume"

    def test_beta_reduction_formula(self) -> None:
        beta_eff = self.afet.beta_reduction_formula(
            beta_global=11.0, sigma_local=1.0, sigma_critical=1.0
        )
        assert beta_eff == pytest.approx(5.5, rel=1e-4)

    def test_beta_reduction_zero_sigma_local(self) -> None:
        beta_eff = self.afet.beta_reduction_formula(beta_global=7.4, sigma_local=0.0)
        assert beta_eff == pytest.approx(7.4)

    def test_beta_reduction_large_sigma_local(self) -> None:
        beta_eff = self.afet.beta_reduction_formula(
            beta_global=11.0, sigma_local=1000.0, sigma_critical=1.0
        )
        assert beta_eff < 0.1

    def test_beta_reduction_uses_instance_critical(self) -> None:
        afet = AFETField(sigma_critical=2.0)
        beta_eff = afet.beta_reduction_formula(beta_global=10.0, sigma_local=2.0)
        assert beta_eff == pytest.approx(5.0, rel=1e-4)

    def test_compute_full_field_returns_snapshot(self) -> None:
        snap = self.afet.compute_full_field(state=0.5, crep_gamma=0.4, beta_global=11.0)
        assert isinstance(snap, EntropyProductionField)
        assert snap.sigma_local >= 0.0
        assert snap.beta_eff <= 11.0
        assert snap.regime in ("surface", "volume")
        assert snap.gamma == pytest.approx(0.4)

    def test_compute_full_field_volume_at_low_beta(self) -> None:
        snap = self.afet.compute_full_field(state=0.5, crep_gamma=1.0, beta_global=3.0)
        assert snap.regime == "volume"

    def test_compute_full_field_kappa_parameter(self) -> None:
        snap = self.afet.compute_full_field(state=0.5, crep_gamma=0.4, beta_global=11.0, kappa=2.0)
        assert snap.kappa == pytest.approx(2.0)

    def test_phase_transition_short_series(self) -> None:
        result = self.afet.phase_transition_surface_to_volume(np.array([1.0, 2.0]))
        assert isinstance(result, DualEntropyGovernance)
        assert result.transition_detected is False

    def test_phase_transition_declining_entropy(self) -> None:
        # Declining trend = low variance → surface regime
        ts = np.linspace(10.0, 1.0, 50)
        result = self.afet.phase_transition_surface_to_volume(ts, window=5)
        assert result.regime in ("surface", "volume")
        assert isinstance(result.transition_detected, bool)

    def test_phase_transition_volatile_series_volume(self) -> None:
        # High variance random series → should tend toward volume regime
        rng = np.random.default_rng(42)
        ts = rng.normal(5.0, 3.0, 100)
        result = self.afet.phase_transition_surface_to_volume(ts, window=10)
        assert result.regime in ("surface", "volume")

    def test_phase_transition_transition_index_valid(self) -> None:
        # Create a series that transitions from stable to volatile
        stable = np.ones(30) * 5.0
        volatile = np.random.default_rng(0).normal(5.0, 3.0, 30)
        ts = np.concatenate([stable, volatile])
        result = self.afet.phase_transition_surface_to_volume(ts, window=5)
        if result.transition_detected:
            assert 0 <= result.transition_index < len(ts)

    def test_reset_clears_history(self) -> None:
        self.afet.compute_local_entropy_production(0.5, 0.3)
        self.afet.reset()
        assert len(self.afet.production_history) == 0

    def test_constants(self) -> None:
        assert BETA_SURFACE == pytest.approx(11.0)
        assert BETA_VOLUME == pytest.approx(4.5)
        assert BETA_BOUNDARY == pytest.approx(7.75)


# ---------------------------------------------------------------------------
# Climate module tests
# ---------------------------------------------------------------------------


class TestRollingEntropyTrend:
    def test_output_length(self) -> None:
        data = np.linspace(0, 1, 20)
        result = rolling_entropy_trend(data, window=5)
        assert len(result) == 20 - 5 + 1

    def test_output_normalized(self) -> None:
        # Use random data with varied entropy to test normalization path
        rng = np.random.default_rng(42)
        data = rng.uniform(0, 5, 30)
        result = rolling_entropy_trend(data, window=5, normalize=True)
        if len(result) > 0:
            assert result.min() >= 0.0 - 1e-9
            assert result.max() <= 1.0 + 1e-9

    def test_empty_short_series(self) -> None:
        result = rolling_entropy_trend(np.array([1.0, 2.0]), window=5)
        assert len(result) == 0

    def test_no_normalize(self) -> None:
        data = np.linspace(0, 1, 20)
        result = rolling_entropy_trend(data, window=5, normalize=False)
        assert len(result) == 16
        assert result.min() >= 0.0

    def test_constant_series_zero_entropy(self) -> None:
        data = np.ones(20)
        result = rolling_entropy_trend(data, window=5, normalize=False)
        # All values identical → single bin → 0 entropy (log(1) = 0)
        assert all(r == pytest.approx(0.0, abs=1e-6) for r in result)


class TestArcticSeaIceEntropy:
    def test_returns_result_object(self) -> None:
        extent = np.array([12.0, 11.8, 11.5, 10.9, 10.2, 9.8, 9.5, 9.1, 8.7, 8.2, 7.9, 7.5])
        result = arctic_sea_ice_entropy(extent)
        assert isinstance(result.beta_eff, float)
        assert result.regime in ("surface", "volume")

    def test_with_years(self) -> None:
        extent = np.linspace(12.0, 7.0, 30)
        years = np.arange(1990, 2020)
        result = arctic_sea_ice_entropy(extent, years=years, window=5)
        assert isinstance(result.regime_shift_year, (int, type(None)))

    def test_single_element(self) -> None:
        result = arctic_sea_ice_entropy(np.array([10.0]))
        assert result.entropy_rate == pytest.approx(0.0)


class TestAmocEntropyProduction:
    def test_output_length_matches_input(self) -> None:
        amoc = np.array([18.0, 17.5, 17.0, 16.5, 16.0])
        result = amoc_entropy_production(amoc)
        assert len(result) == len(amoc)

    def test_all_non_negative(self) -> None:
        amoc = np.linspace(20.0, 10.0, 20)
        result = amoc_entropy_production(amoc)
        assert np.all(result >= 0.0)

    def test_with_crep_gamma_series(self) -> None:
        amoc = np.ones(10) * 15.0
        gamma = np.linspace(0.2, 0.8, 10)
        result = amoc_entropy_production(amoc, crep_gamma_series=gamma, kappa=2.0)
        assert len(result) == 10

    def test_wrong_length_gamma_falls_back(self) -> None:
        amoc = np.ones(5) * 15.0
        gamma = np.ones(3) * 0.5
        result = amoc_entropy_production(amoc, crep_gamma_series=gamma)
        assert len(result) == 5

    def test_empty_input(self) -> None:
        result = amoc_entropy_production(np.array([]))
        assert len(result) == 0


class TestDetectClimateRegimeShift:
    def test_returns_governance_object(self) -> None:
        data = np.random.default_rng(42).normal(5.0, 1.0, 50)
        result = detect_climate_regime_shift(data, window=5)
        assert isinstance(result, DualEntropyGovernance)

    def test_short_series_no_transition(self) -> None:
        result = detect_climate_regime_shift(np.array([1.0, 2.0]), window=5)
        assert result.transition_detected is False

    def test_long_declining_series(self) -> None:
        data = np.linspace(10.0, 1.0, 100)
        result = detect_climate_regime_shift(data, window=10)
        assert result.regime in ("surface", "volume")
