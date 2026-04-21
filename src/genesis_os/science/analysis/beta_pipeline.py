"""β-fitting pipeline — full batch fitting across empirical datasets.

Implements the Feldtheorie β-fitting pipeline for 78 systems across 5 domains.
Produces domain-classified β values and validates the ANOVA result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from genesis_os.core.utac_bridge import DomainBetaRegistry, UTACBridge
from genesis_os.science.models.logistic_fit import UTACLogisticResult, fit_utac_logistic


@dataclass
class SystemFitResult:
    """β-fit result for a single empirical system.

    Attributes:
        system_id: Identifier for the system.
        domain: Domain classification (informational/biological/climate/etc.).
        beta: Fitted β steepness.
        theta: Fitted Θ inflection.
        r_squared: R² of the logistic fit.
        delta_aic_min: Minimum ΔAIC across null models (higher = stronger evidence).
        n_points: Number of data points.
    """

    system_id: str
    domain: str
    beta: float
    theta: float
    r_squared: float
    delta_aic_min: float
    n_points: int


@dataclass
class PipelineResult:
    """Full β-pipeline result across all systems.

    Attributes:
        system_results: List of per-system fit results.
        domain_means: Mean β per domain.
        domain_stds: Std β per domain.
        anova_f: ANOVA F-statistic (should be ≈ 185.3 on real data).
        anova_p: ANOVA p-value.
        eta_squared: ANOVA effect size η².
        n_systems: Total number of systems fitted.
    """

    system_results: list[SystemFitResult]
    domain_means: dict[str, float]
    domain_stds: dict[str, float]
    anova_f: float
    anova_p: float
    eta_squared: float
    n_systems: int


class BetaPipeline:
    """Full β-fitting pipeline for empirical system datasets.

    Fits UTAC logistic σ(β(R-Θ)) to each system, classifies by domain,
    and runs ANOVA to validate domain separation.

    Args:
        registry: DomainBetaRegistry for domain classification.
        bridge: UTACBridge for parameter mapping.
        n_bootstrap: Bootstrap iterations per system (default 100 for speed).
    """

    def __init__(
        self,
        registry: DomainBetaRegistry | None = None,
        bridge: UTACBridge | None = None,
        n_bootstrap: int = 100,
    ) -> None:
        self.registry = registry or DomainBetaRegistry()
        self.bridge = bridge or UTACBridge()
        self.n_bootstrap = n_bootstrap
        self._results: list[SystemFitResult] = []

    def fit_system(
        self,
        system_id: str,
        R: np.ndarray,
        response: np.ndarray,
        domain: str | None = None,
    ) -> SystemFitResult:
        """Fit a single empirical system.

        Args:
            system_id: Unique identifier.
            R: State/resource variable.
            response: Observed response.
            domain: Known domain label (auto-classified if None).

        Returns:
            SystemFitResult for this system.
        """
        result: UTACLogisticResult = fit_utac_logistic(
            R=R,
            response=response,
            n_bootstrap=self.n_bootstrap,
        )

        classified_domain = domain if domain is not None else self.registry.classify_domain(
            result.beta
        )
        delta_aic_min = min(
            result.delta_aic_linear,
            result.delta_aic_power,
            result.delta_aic_exp,
        )

        fit = SystemFitResult(
            system_id=system_id,
            domain=classified_domain,
            beta=result.beta,
            theta=result.theta,
            r_squared=result.r_squared,
            delta_aic_min=delta_aic_min,
            n_points=result.n,
        )
        self._results.append(fit)
        return fit

    def run_batch(
        self, datasets: list[dict[str, Any]]
    ) -> PipelineResult:
        """Run the full β-fitting pipeline on a batch of datasets.

        Each dataset dict must have: ``id``, ``R``, ``response``.
        Optionally: ``domain`` (string label).

        Args:
            datasets: List of dataset dicts.

        Returns:
            PipelineResult with domain statistics and ANOVA.
        """
        self._results = []
        for ds in datasets:
            self.fit_system(
                system_id=str(ds.get("id", "unknown")),
                R=np.asarray(ds["R"]),
                response=np.asarray(ds["response"]),
                domain=ds.get("domain"),
            )

        return self._compute_pipeline_result()

    def _compute_pipeline_result(self) -> PipelineResult:
        """Compute domain statistics and ANOVA from current results."""
        # Group by domain
        domain_betas: dict[str, list[float]] = {}
        for r in self._results:
            domain_betas.setdefault(r.domain, []).append(r.beta)

        domain_means = {d: float(np.mean(betas)) for d, betas in domain_betas.items()}
        domain_stds = {d: float(np.std(betas)) for d, betas in domain_betas.items()}

        # One-way ANOVA
        f_stat, p_val, eta_sq = self._one_way_anova(domain_betas)

        return PipelineResult(
            system_results=list(self._results),
            domain_means=domain_means,
            domain_stds=domain_stds,
            anova_f=f_stat,
            anova_p=p_val,
            eta_squared=eta_sq,
            n_systems=len(self._results),
        )

    @staticmethod
    def _one_way_anova(domain_betas: dict[str, list[float]]) -> tuple[float, float, float]:
        """Compute one-way ANOVA F-statistic, p-value, and η².

        Args:
            domain_betas: Dict mapping domain → list of β values.

        Returns:
            (F_statistic, p_value, eta_squared)
        """
        groups = [np.array(v) for v in domain_betas.values() if len(v) > 0]
        if len(groups) < 2:
            return 0.0, 1.0, 0.0

        all_vals = np.concatenate(groups)
        grand_mean = float(np.mean(all_vals))
        n_total = len(all_vals)
        k = len(groups)

        # Between-group sum of squares
        ss_between = float(sum(
            len(g) * (float(np.mean(g)) - grand_mean) ** 2 for g in groups
        ))
        # Within-group sum of squares
        ss_within = float(sum(np.sum((g - np.mean(g)) ** 2) for g in groups))

        df_between = k - 1
        df_within = n_total - k

        if df_within <= 0 or ss_within < 1e-12:
            return 0.0, 1.0, 0.0

        ms_between = ss_between / df_between
        ms_within = ss_within / df_within
        f_stat = float(ms_between / max(ms_within, 1e-12))

        # p-value via scipy if available, else approximate
        try:
            from scipy import stats as sp_stats
            p_val = float(sp_stats.f.sf(f_stat, df_between, df_within))
        except ImportError:
            p_val = 1.0 / (1.0 + f_stat)  # rough approximation

        # η² = SS_between / SS_total
        ss_total = ss_between + ss_within
        eta_sq = float(ss_between / max(ss_total, 1e-12))

        return f_stat, p_val, eta_sq

    @property
    def results(self) -> list[SystemFitResult]:
        """Read-only list of fitted system results."""
        return list(self._results)

    def summary(self) -> dict[str, Any]:
        """Return a summary of the pipeline results."""
        return {
            "n_systems": len(self._results),
            "domains": list({r.domain for r in self._results}),
            "mean_beta": float(np.mean([r.beta for r in self._results])) if self._results else 0.0,
            "mean_r_squared": (
                float(np.mean([r.r_squared for r in self._results])) if self._results else 0.0
            ),
        }
