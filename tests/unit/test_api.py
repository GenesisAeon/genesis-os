"""Tests for genesis_os.api — GenesisRouter endpoints."""

from __future__ import annotations

import numpy as np
import pytest

from genesis_os.api import GenesisRouter
from genesis_os.api.cycle import CYCLE_PHASES


# ---------------------------------------------------------------------------
# CYCLE_PHASES constant
# ---------------------------------------------------------------------------


class TestCyclePhases:
    def test_has_expected_phases(self) -> None:
        for phase in ("core", "afet", "crep", "utac_ode", "vrig",
                      "mirror", "aeon", "science", "cosmicweb", "api", "sigillin"):
            assert phase in CYCLE_PHASES

    def test_length_11(self) -> None:
        assert len(CYCLE_PHASES) == 11

    def test_all_strings(self) -> None:
        assert all(isinstance(p, str) for p in CYCLE_PHASES)


# ---------------------------------------------------------------------------
# GenesisRouter tests
# ---------------------------------------------------------------------------


class TestGenesisRouter:
    def setup_method(self) -> None:
        self.router = GenesisRouter()

    # --- utac_fit ---

    def test_utac_fit_returns_dict(self) -> None:
        R = list(np.linspace(0, 1, 25))
        y = [1 / (1 + np.exp(-5 * (r - 0.5))) for r in R]
        result = self.router.utac_fit(R, y, n_bootstrap=5)
        assert isinstance(result, dict)

    def test_utac_fit_has_required_keys(self) -> None:
        R = list(np.linspace(0, 1, 25))
        y = [1 / (1 + np.exp(-5 * (r - 0.5))) for r in R]
        result = self.router.utac_fit(R, y, n_bootstrap=5)
        for key in ("beta", "theta", "r_squared", "domain", "success", "n"):
            assert key in result

    def test_utac_fit_beta_positive(self) -> None:
        R = list(np.linspace(0, 1, 25))
        y = [1 / (1 + np.exp(-7 * (r - 0.5))) for r in R]
        result = self.router.utac_fit(R, y, n_bootstrap=5)
        assert result["beta"] > 0.0

    def test_utac_fit_domain_classified(self) -> None:
        R = list(np.linspace(0, 1, 25))
        y = [1 / (1 + np.exp(-7 * (r - 0.5))) for r in R]
        result = self.router.utac_fit(R, y, n_bootstrap=5)
        assert result["domain"] in (
            "informational", "geophysical", "biological", "climate", "neurodegen"
        )

    def test_utac_fit_too_short_fails(self) -> None:
        result = self.router.utac_fit([0.1, 0.5], [0.3, 0.7], n_bootstrap=5)
        assert result["success"] is False

    def test_utac_fit_ci_ordered(self) -> None:
        R = list(np.linspace(0, 1, 30))
        y = [1 / (1 + np.exp(-6 * (r - 0.5))) for r in R]
        result = self.router.utac_fit(R, y, n_bootstrap=10)
        assert result["beta_ci_95"][0] <= result["beta_ci_95"][1]

    # --- utac_domain ---

    def test_utac_domain_known(self) -> None:
        result = self.router.utac_domain("climate")
        assert result["beta_mean"] == pytest.approx(11.0)
        assert "AMOC" in result["domains"]

    def test_utac_domain_unknown_returns_error(self) -> None:
        result = self.router.utac_domain("quantum_gravity")
        assert "error" in result
        assert "available" in result

    def test_utac_domain_all_five(self) -> None:
        for domain in ("informational", "geophysical", "biological", "climate", "neurodegen"):
            result = self.router.utac_domain(domain)
            assert "beta_mean" in result
            assert "error" not in result

    # --- crep_compute ---

    def test_crep_compute_returns_dict(self) -> None:
        signal = list(np.random.default_rng(42).normal(0, 1, 100))
        result = self.router.crep_compute(signal)
        assert isinstance(result, dict)

    def test_crep_compute_has_required_keys(self) -> None:
        signal = list(np.random.default_rng(42).normal(0, 1, 100))
        result = self.router.crep_compute(signal)
        for key in ("C", "R", "E", "P", "gamma", "governance_level"):
            assert key in result

    def test_crep_compute_unit_interval_components(self) -> None:
        signal = list(np.random.default_rng(7).normal(0, 1, 100))
        result = self.router.crep_compute(signal)
        for key in ("C", "R", "E", "P", "gamma"):
            assert 0.0 <= result[key] <= 1.0

    def test_crep_compute_governance_level_string(self) -> None:
        signal = list(np.random.default_rng(3).normal(0, 1, 100))
        result = self.router.crep_compute(signal)
        assert result["governance_level"] in (
            "safe", "informational", "warning", "reviewer", "critical"
        )

    def test_crep_compute_n_points(self) -> None:
        signal = list(np.ones(50))
        result = self.router.crep_compute(signal)
        assert result["n_points"] == 50

    # --- vrig_velocity ---

    def test_vrig_velocity_returns_dict(self) -> None:
        result = self.router.vrig_velocity(
            params_current=[0.5, 0.9, 1.8],
            params_prev=[0.3, 1.0, 2.0],
        )
        assert isinstance(result, dict)

    def test_vrig_velocity_has_keys(self) -> None:
        result = self.router.vrig_velocity(
            params_current=[0.5, 0.9, 1.8],
            params_prev=[0.3, 1.0, 2.0],
        )
        for key in ("velocity", "regime_change", "v_rig_constant_kms"):
            assert key in result

    def test_vrig_velocity_nonnegative(self) -> None:
        result = self.router.vrig_velocity(
            params_current=[0.5, 0.9, 1.8],
            params_prev=[0.3, 1.0, 2.0],
        )
        assert result["velocity"] >= 0.0

    def test_vrig_velocity_zero_displacement(self) -> None:
        result = self.router.vrig_velocity(
            params_current=[0.3, 1.0, 2.0],
            params_prev=[0.3, 1.0, 2.0],
        )
        assert result["velocity"] == pytest.approx(0.0)

    def test_vrig_constant_approx(self) -> None:
        result = self.router.vrig_velocity([0.3, 1.0, 2.0], [0.3, 1.0, 2.0])
        assert 1300.0 < result["v_rig_constant_kms"] < 1400.0

    # --- mirror_update ---

    def test_mirror_update_returns_confirmation(self) -> None:
        result = self.router.mirror_update({"entropy": 0.6, "phase": "activation"})
        assert result["status"] == "updated"
        assert "entropy" in result["updated_keys"]

    def test_mirror_update_increments_cycle(self) -> None:
        self.router.mirror_update({"x": 1})
        self.router.mirror_update({"y": 2})
        assert self.router._cycle_count == 2

    def test_mirror_update_accumulates_state(self) -> None:
        self.router.mirror_update({"a": 1})
        self.router.mirror_update({"b": 2})
        assert "a" in self.router._mirror_state
        assert "b" in self.router._mirror_state

    # --- genesis_cycle_status ---

    def test_genesis_cycle_status_returns_dict(self) -> None:
        result = self.router.genesis_cycle_status()
        assert isinstance(result, dict)

    def test_genesis_cycle_status_has_phases(self) -> None:
        result = self.router.genesis_cycle_status()
        assert "phases" in result
        assert result["n_phases"] == 11

    def test_genesis_cycle_status_registry_domains(self) -> None:
        result = self.router.genesis_cycle_status()
        assert "registry_domains" in result
        assert len(result["registry_domains"]) == 5

    def test_genesis_cycle_status_cycle_count(self) -> None:
        self.router.mirror_update({"ping": True})
        status = self.router.genesis_cycle_status()
        assert status["cycle_count"] == 1
