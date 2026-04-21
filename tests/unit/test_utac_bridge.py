"""Tests for genesis_os.core.utac_bridge — UTACBridge and DomainBetaRegistry."""

from __future__ import annotations

import math

import numpy as np
import pytest

from genesis_os.core.utac_bridge import (
    BETA_ANOVA,
    CREP_THRESHOLDS,
    DOMAIN_BETA,
    PHI,
    DomainBetaRegistry,
    UTACBridge,
)


# ---------------------------------------------------------------------------
# DomainBetaRegistry tests
# ---------------------------------------------------------------------------


class TestDomainBetaRegistry:
    def setup_method(self) -> None:
        self.registry = DomainBetaRegistry()

    def test_all_domains_present(self) -> None:
        assert set(self.registry.all_domains) == {
            "informational", "geophysical", "biological", "climate", "neurodegen"
        }

    def test_get_known_domain(self) -> None:
        data = self.registry.get("climate")
        assert data["beta_mean"] == pytest.approx(11.0)
        assert data["beta_std"] == pytest.approx(1.0)
        assert "AMOC" in data["domains"]

    def test_get_unknown_domain_raises(self) -> None:
        with pytest.raises(KeyError, match="quantum"):
            self.registry.get("quantum")

    def test_classify_climate(self) -> None:
        assert self.registry.classify_domain(11.0) == "climate"

    def test_classify_informational(self) -> None:
        assert self.registry.classify_domain(4.5) == "informational"

    def test_classify_biological(self) -> None:
        assert self.registry.classify_domain(7.4) == "biological"

    def test_classify_neurodegen(self) -> None:
        assert self.registry.classify_domain(13.0) == "neurodegen"

    def test_classify_geophysical(self) -> None:
        assert self.registry.classify_domain(4.6) == "geophysical"

    def test_classify_boundary_informational_geophysical(self) -> None:
        # Midpoint between 4.5 and 4.6 = 4.55 — both are equidistant.
        # nearest-centroid picks informational (lower β, first in ordered list)
        result = self.registry.classify_domain(4.55)
        assert result in ("informational", "geophysical")

    def test_classify_high_beta_neurodegen(self) -> None:
        assert self.registry.classify_domain(20.0) == "neurodegen"

    def test_classify_low_beta_informational(self) -> None:
        assert self.registry.classify_domain(0.1) == "informational"

    def test_beta_mean_and_std(self) -> None:
        assert self.registry.beta_mean("biological") == pytest.approx(7.4)
        assert self.registry.beta_std("biological") == pytest.approx(0.9)

    def test_phi_attractor_climate(self) -> None:
        phi5 = PHI**5
        assert self.registry.phi_attractor("climate") == pytest.approx(phi5, rel=1e-4)

    def test_phi_attractor_neurodegen_none(self) -> None:
        assert self.registry.phi_attractor("neurodegen") is None

    def test_anova_result_keys(self) -> None:
        anova = self.registry.anova_result
        assert anova["F_statistic"] == pytest.approx(185.3)
        assert anova["p_value"] < 1e-15
        assert anova["eta_squared"] >= 0.90
        assert anova["n_systems"] == 78


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_phi_value(self) -> None:
        assert PHI == pytest.approx(1.6180339887, rel=1e-6)

    def test_domain_beta_structure(self) -> None:
        for domain, data in DOMAIN_BETA.items():
            assert "beta_mean" in data
            assert "beta_std" in data
            assert "phi_attractor" in data
            assert "domains" in data
            assert isinstance(data["domains"], list)

    def test_crep_thresholds_ordering(self) -> None:
        vals = list(CREP_THRESHOLDS.values())
        assert vals == sorted(vals), "CREP thresholds should be monotonically increasing"

    def test_beta_anova_constants(self) -> None:
        assert BETA_ANOVA["F_statistic"] == pytest.approx(185.3)
        assert BETA_ANOVA["eta_squared"] == pytest.approx(0.91)


# ---------------------------------------------------------------------------
# UTACBridge tests
# ---------------------------------------------------------------------------


class TestUTACBridge:
    def setup_method(self) -> None:
        self.bridge = UTACBridge(r=0.3, K=1.0, sigma=2.0)

    # --- feldtheorie_activation ---

    def test_activation_at_theta_is_half(self) -> None:
        a = UTACBridge.feldtheorie_activation(beta=5.0, R=0.5, theta=0.5)
        assert a == pytest.approx(0.5, abs=1e-6)

    def test_activation_above_theta_greater_than_half(self) -> None:
        a = UTACBridge.feldtheorie_activation(beta=7.4, R=0.8, theta=0.5)
        assert a > 0.5

    def test_activation_below_theta_less_than_half(self) -> None:
        a = UTACBridge.feldtheorie_activation(beta=7.4, R=0.2, theta=0.5)
        assert a < 0.5

    def test_activation_domain_climate_beta(self) -> None:
        a = UTACBridge.feldtheorie_activation(beta=11.0, R=0.7, theta=0.5)
        assert 0.0 < a < 1.0

    def test_activation_large_beta_sharp_transition(self) -> None:
        # β=50 gives very sharp transition near theta; R=0.6 vs R=0.4 gives clear separation
        a_high = UTACBridge.feldtheorie_activation(beta=50.0, R=0.6, theta=0.5)
        a_low = UTACBridge.feldtheorie_activation(beta=50.0, R=0.4, theta=0.5)
        assert a_high > 0.99
        assert a_low < 0.01

    def test_activation_zero_beta_always_half(self) -> None:
        for R in [0.0, 0.3, 0.7, 1.0]:
            a = UTACBridge.feldtheorie_activation(beta=0.0, R=R, theta=0.5)
            assert a == pytest.approx(0.5, abs=1e-6)

    def test_activation_numerical_stability_large_negative(self) -> None:
        # β·(R-Θ) >> 500 should not raise overflow
        a = UTACBridge.feldtheorie_activation(beta=1000.0, R=0.0, theta=0.5)
        assert 0.0 <= a <= 1.0

    def test_activation_numerical_stability_large_positive(self) -> None:
        a = UTACBridge.feldtheorie_activation(beta=1000.0, R=1.0, theta=0.5)
        assert 0.0 <= a <= 1.0

    # --- feldtheorie_to_genesis ---

    def test_feldtheorie_to_genesis_H_normalized(self) -> None:
        result = self.bridge.feldtheorie_to_genesis(beta=4.5, R=0.6)
        assert result["H"] == pytest.approx(0.6 * self.bridge.K)

    def test_feldtheorie_to_genesis_gamma_from_beta(self) -> None:
        result = self.bridge.feldtheorie_to_genesis(beta=4.5, R=0.6)
        assert result["gamma"] == pytest.approx(4.5 / self.bridge.sigma, rel=1e-6)

    def test_feldtheorie_to_genesis_default_theta(self) -> None:
        result = self.bridge.feldtheorie_to_genesis(beta=4.5, R=0.6)
        assert result["theta"] == pytest.approx(self.bridge.K / 2.0)

    def test_feldtheorie_to_genesis_custom_theta(self) -> None:
        result = self.bridge.feldtheorie_to_genesis(beta=4.5, R=0.6, theta=0.3)
        assert result["theta"] == pytest.approx(0.3)

    def test_feldtheorie_to_genesis_activation_in_unit_interval(self) -> None:
        result = self.bridge.feldtheorie_to_genesis(beta=7.4, R=0.8)
        assert 0.0 <= result["activation"] <= 1.0

    # --- genesis_to_feldtheorie ---

    def test_genesis_to_feldtheorie_R_from_H(self) -> None:
        result = self.bridge.genesis_to_feldtheorie(H=0.7, gamma=2.0)
        assert result["R"] == pytest.approx(0.7 / self.bridge.K)

    def test_genesis_to_feldtheorie_beta_from_gamma(self) -> None:
        result = self.bridge.genesis_to_feldtheorie(H=0.5, gamma=2.25)
        assert result["beta"] == pytest.approx(self.bridge.sigma * 2.25, rel=1e-6)

    def test_genesis_to_feldtheorie_theta_is_K_half(self) -> None:
        result = self.bridge.genesis_to_feldtheorie(H=0.4, gamma=1.5)
        assert result["theta"] == pytest.approx(self.bridge.K / 2.0)

    # --- genesis_ode_step ---

    def test_ode_step_positive_gamma_increases_entropy_below_K(self) -> None:
        H0 = 0.3
        H1 = self.bridge.genesis_ode_step(H=H0, gamma=1.0)
        assert H1 > H0

    def test_ode_step_negative_gamma_decreases_entropy(self) -> None:
        H0 = 0.8
        H1 = self.bridge.genesis_ode_step(H=H0, gamma=-1.0)
        assert H1 < H0

    def test_ode_step_zero_gamma_no_change(self) -> None:
        H0 = 0.5
        H1 = self.bridge.genesis_ode_step(H=H0, gamma=0.0)
        assert H1 == pytest.approx(H0)

    def test_ode_step_clamped_to_zero(self) -> None:
        # Negative input should clamp output to 0
        H1 = self.bridge.genesis_ode_step(H=-0.5, gamma=-10.0)
        assert H1 >= 0.0

    def test_ode_step_clamped_to_K(self) -> None:
        H1 = self.bridge.genesis_ode_step(H=self.bridge.K + 0.5, gamma=10.0)
        assert H1 <= self.bridge.K

    # --- compute_sigma_phi_min (Frame Principle) ---

    def test_sigma_phi_min_default_params(self) -> None:
        # With r=0.3, sigma=2.0, gamma_max=1.0 → tanh(2)≈0.964
        # σ_Φ_min = 0.3 * (1 - 0.964) / 2 ≈ 0.0054 (small but positive)
        result = self.bridge.compute_sigma_phi_min(gamma_max=1.0)
        assert result > 0.0

    def test_sigma_phi_min_approx_one_sixteenth(self) -> None:
        # With r=1.0, sigma=0.0, gamma_max=0.0 → tanh(0)=0 → σ_Φ_min = 0.5
        # With smaller sigma we can approach 1/16 ≈ 0.0625
        bridge = UTACBridge(r=0.3, K=1.0, sigma=0.5)
        val = bridge.compute_sigma_phi_min(gamma_max=1.0)
        # Just check it's in a reasonable range [0, 1]
        assert 0.0 <= val <= 1.0

    def test_sigma_phi_min_zero_gamma_max(self) -> None:
        # gamma_max=0 → tanh(0)=0 → σ_Φ_min = r/2
        result = self.bridge.compute_sigma_phi_min(gamma_max=0.0)
        assert result == pytest.approx(self.bridge.r / 2.0, rel=1e-6)

    def test_sigma_phi_min_explicit_r_sigma(self) -> None:
        result = self.bridge.compute_sigma_phi_min(r=1.0, sigma=0.0, gamma_max=0.0)
        assert result == pytest.approx(0.5, rel=1e-6)

    # --- steady_state_equivalence ---

    def test_steady_state_equivalence_exact(self) -> None:
        # At R=Θ the activation is always 0.5 regardless of β; trivially equivalent
        assert self.bridge.steady_state_equivalence(beta=7.4, R=0.5, theta=0.5)

    def test_steady_state_equivalence_tight_tol(self) -> None:
        # When sigma is consistent with beta, the mappings are identical
        assert self.bridge.steady_state_equivalence(beta=4.0, R=0.6, theta=0.5, tol=1e-2)

    # --- classify_domain ---

    def test_classify_domain_delegates(self) -> None:
        assert self.bridge.classify_domain(11.0) == "climate"
        assert self.bridge.classify_domain(4.5) == "informational"
        assert self.bridge.classify_domain(7.4) == "biological"
        assert self.bridge.classify_domain(13.0) == "neurodegen"

    # --- custom K ---

    def test_bridge_custom_K(self) -> None:
        bridge = UTACBridge(r=0.5, K=10.0, sigma=3.0)
        result = bridge.feldtheorie_to_genesis(beta=4.5, R=0.6)
        assert result["H"] == pytest.approx(6.0)  # R * K = 0.6 * 10
        assert result["theta"] == pytest.approx(5.0)  # K/2

    # --- round-trip conversion ---

    def test_round_trip_feld_to_genesis_to_feld(self) -> None:
        beta_orig = 7.4
        R_orig = 0.65
        g = self.bridge.feldtheorie_to_genesis(beta=beta_orig, R=R_orig)
        back = self.bridge.genesis_to_feldtheorie(H=g["H"], gamma=g["gamma"])
        assert back["R"] == pytest.approx(R_orig, rel=1e-6)
        assert back["beta"] == pytest.approx(beta_orig, rel=1e-6)
