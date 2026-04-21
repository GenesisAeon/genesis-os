"""Tests for genesis_os.science — β-fitting pipeline."""

from __future__ import annotations

import numpy as np
import pytest

from genesis_os.science import BetaPipeline, UTACLogisticResult, fit_utac_logistic
from genesis_os.science.analysis.beta_pipeline import PipelineResult, SystemFitResult
from genesis_os.science.data import generate_synthetic_datasets
from genesis_os.science.data.synthetic import generate_synthetic_datasets as gen_ds


# ---------------------------------------------------------------------------
# UTACLogisticResult tests
# ---------------------------------------------------------------------------


class TestFitUTACLogistic:
    def _make_logistic_data(
        self, beta: float = 7.0, theta: float = 0.5, n: int = 40, noise: float = 0.02
    ) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(42)
        R = np.linspace(0.0, 1.0, n)
        exponent = -beta * (R - theta)
        response = 1.0 / (1.0 + np.exp(np.clip(exponent, -500, 500)))
        return R, response + rng.normal(0, noise, n)

    def test_returns_result_object(self) -> None:
        R, y = self._make_logistic_data()
        result = fit_utac_logistic(R, y, n_bootstrap=10)
        assert isinstance(result, UTACLogisticResult)

    def test_beta_positive(self) -> None:
        R, y = self._make_logistic_data(beta=7.0)
        result = fit_utac_logistic(R, y, n_bootstrap=10)
        assert result.beta > 0.0

    def test_theta_in_unit_interval(self) -> None:
        R, y = self._make_logistic_data()
        result = fit_utac_logistic(R, y, n_bootstrap=10)
        assert 0.0 <= result.theta <= 1.0

    def test_r_squared_positive(self) -> None:
        R, y = self._make_logistic_data(noise=0.01)
        result = fit_utac_logistic(R, y, n_bootstrap=10)
        assert result.r_squared >= 0.0

    def test_ci_ordered(self) -> None:
        R, y = self._make_logistic_data()
        result = fit_utac_logistic(R, y, n_bootstrap=20)
        assert result.beta_ci_95[0] <= result.beta_ci_95[1]

    def test_n_correct(self) -> None:
        R, y = self._make_logistic_data(n=50)
        result = fit_utac_logistic(R, y, n_bootstrap=10)
        assert result.n == 50

    def test_success_on_valid_data(self) -> None:
        R, y = self._make_logistic_data(n=40)
        result = fit_utac_logistic(R, y, n_bootstrap=10)
        assert result.success is True

    def test_fail_on_too_few_points(self) -> None:
        R = np.array([0.1, 0.5])
        y = np.array([0.3, 0.7])
        result = fit_utac_logistic(R, y, n_bootstrap=5)
        assert result.success is False

    def test_delta_aic_computed(self) -> None:
        R, y = self._make_logistic_data(beta=8.0, noise=0.01)
        result = fit_utac_logistic(R, y, null_models=["linear", "power_law"], n_bootstrap=5)
        assert isinstance(result.delta_aic_linear, float)
        assert isinstance(result.delta_aic_power, float)

    def test_custom_null_models(self) -> None:
        R, y = self._make_logistic_data()
        result = fit_utac_logistic(R, y, null_models=["linear"], n_bootstrap=5)
        assert isinstance(result.delta_aic_linear, float)
        assert isinstance(result.delta_aic_exp, float)  # defaults to 0.0

    def test_climate_beta_range(self) -> None:
        R, y = self._make_logistic_data(beta=11.0, theta=0.5, noise=0.02)
        result = fit_utac_logistic(R, y, n_bootstrap=5)
        # Should recover beta in plausible range
        assert result.beta > 0.0

    def test_unknown_null_model_skipped(self) -> None:
        R, y = self._make_logistic_data()
        result = fit_utac_logistic(R, y, null_models=["linear", "unknown_model"], n_bootstrap=5)
        assert result.success is True


# ---------------------------------------------------------------------------
# BetaPipeline tests
# ---------------------------------------------------------------------------


class TestBetaPipeline:
    def setup_method(self) -> None:
        self.pipeline = BetaPipeline(n_bootstrap=10)

    def _make_logistic_data(self, beta: float, n: int = 30) -> tuple[np.ndarray, np.ndarray]:
        R = np.linspace(0.0, 1.0, n)
        response = 1.0 / (1.0 + np.exp(-beta * (R - 0.5)))
        return R, response

    def test_fit_system_returns_result(self) -> None:
        R, y = self._make_logistic_data(7.0)
        result = self.pipeline.fit_system("bio_01", R, y)
        assert isinstance(result, SystemFitResult)

    def test_fit_system_domain_classification(self) -> None:
        R, y = self._make_logistic_data(11.0)
        result = self.pipeline.fit_system("climate_01", R, y)
        assert result.system_id == "climate_01"
        assert isinstance(result.domain, str)

    def test_fit_system_with_explicit_domain(self) -> None:
        R, y = self._make_logistic_data(4.5)
        result = self.pipeline.fit_system("info_01", R, y, domain="informational")
        assert result.domain == "informational"

    def test_run_batch_returns_pipeline_result(self) -> None:
        datasets = [
            {"id": "sys_0", "R": np.linspace(0, 1, 20), "response": np.linspace(0.1, 0.9, 20)},
            {"id": "sys_1", "R": np.linspace(0, 1, 20), "response": np.linspace(0.2, 0.8, 20)},
        ]
        result = self.pipeline.run_batch(datasets)
        assert isinstance(result, PipelineResult)
        assert result.n_systems == 2

    def test_run_batch_domain_means(self) -> None:
        datasets = [
            {"id": f"s{i}", "R": np.linspace(0, 1, 25), "response": np.linspace(0.1, 0.9, 25)}
            for i in range(4)
        ]
        result = self.pipeline.run_batch(datasets)
        assert len(result.domain_means) >= 1

    def test_anova_fields_present(self) -> None:
        datasets = [
            {"id": f"s{i}", "R": np.linspace(0, 1, 25), "response": np.linspace(0.1, 0.9, 25)}
            for i in range(3)
        ]
        result = self.pipeline.run_batch(datasets)
        assert isinstance(result.anova_f, float)
        assert isinstance(result.anova_p, float)
        assert 0.0 <= result.eta_squared <= 1.0

    def test_results_property(self) -> None:
        R, y = self._make_logistic_data(5.0)
        self.pipeline.fit_system("test", R, y)
        assert len(self.pipeline.results) == 1

    def test_summary_keys(self) -> None:
        summary = self.pipeline.summary()
        assert "n_systems" in summary

    def test_pipeline_on_synthetic_data(self) -> None:
        datasets = generate_synthetic_datasets(n_per_domain=2, n_points=25, seed=99)
        pipeline = BetaPipeline(n_bootstrap=5)
        result = pipeline.run_batch(datasets)
        assert result.n_systems == 2 * 5  # 2 per domain × 5 domains


# ---------------------------------------------------------------------------
# Synthetic dataset generator tests
# ---------------------------------------------------------------------------


class TestSyntheticDatasets:
    def test_returns_correct_count(self) -> None:
        datasets = gen_ds(n_per_domain=3, n_points=20, seed=7)
        assert len(datasets) == 3 * 5  # 5 domains

    def test_dataset_structure(self) -> None:
        datasets = gen_ds(n_per_domain=2, n_points=15, seed=42)
        for ds in datasets:
            assert "id" in ds
            assert "domain" in ds
            assert "R" in ds
            assert "response" in ds
            assert len(ds["R"]) == 15
            assert len(ds["response"]) == 15

    def test_response_in_unit_interval(self) -> None:
        datasets = gen_ds(n_per_domain=2, n_points=20, seed=0)
        for ds in datasets:
            assert np.all(ds["response"] >= 0.0)
            assert np.all(ds["response"] <= 1.0)

    def test_domains_covered(self) -> None:
        datasets = gen_ds(n_per_domain=1, n_points=20, seed=1)
        domains = {ds["domain"] for ds in datasets}
        assert "informational" in domains
        assert "climate" in domains
        assert "biological" in domains

    def test_beta_true_positive(self) -> None:
        datasets = gen_ds(n_per_domain=3, n_points=20, seed=5)
        for ds in datasets:
            assert ds["beta_true"] > 0.0

    def test_theta_true_in_range(self) -> None:
        datasets = gen_ds(n_per_domain=3, n_points=20, seed=5)
        for ds in datasets:
            assert 0.3 <= ds["theta_true"] <= 0.7


# ---------------------------------------------------------------------------
# ANOVA internal method
# ---------------------------------------------------------------------------


class TestBetaPipelineANOVA:
    def test_two_domain_anova(self) -> None:
        domain_betas = {
            "climate": [10.5, 11.0, 11.5, 10.8, 11.2],
            "informational": [4.0, 4.5, 5.0, 4.3, 4.7],
        }
        f, p, eta = BetaPipeline._one_way_anova(domain_betas)
        assert f > 0.0
        assert 0.0 <= p <= 1.0
        assert 0.0 <= eta <= 1.0

    def test_single_domain_returns_zero(self) -> None:
        domain_betas = {"climate": [10.5, 11.0, 11.5]}
        f, p, eta = BetaPipeline._one_way_anova(domain_betas)
        assert f == pytest.approx(0.0)
        assert p == pytest.approx(1.0)

    def test_five_domain_anova(self) -> None:
        domain_betas = {
            "informational": [4.0, 4.5, 5.0, 4.3, 4.7],
            "geophysical": [4.1, 4.6, 4.8, 4.4, 4.9],
            "biological": [7.0, 7.4, 7.8, 7.2, 7.6],
            "climate": [10.5, 11.0, 11.5, 10.8, 11.2],
            "neurodegen": [12.5, 13.0, 13.5, 12.8, 13.2],
        }
        f, p, eta = BetaPipeline._one_way_anova(domain_betas)
        assert f > 10.0  # Should be very high F for well-separated groups
        assert p < 0.05
        assert eta > 0.5
