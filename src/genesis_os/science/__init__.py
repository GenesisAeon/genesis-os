"""genesis-os science pipeline — empirical β-fitting across 78 systems.

Ports Feldtheorie's validated empirical infrastructure:
    - 78 empirical systems across 5 domains
    - UTAC logistic σ(β(R-Θ)) fitting with ΔAIC validation
    - β-domain clustering: ANOVA F(4,73)=185.3, p<1e-20, η²=0.91
    - Meta-regression and domain classification

Primary modules:
    models.logistic_fit   — σ(β(R-Θ)) fitter with bootstrap CI
    models.meta_regression — β meta-regression across domains
    analysis.beta_pipeline — full β-fitting pipeline
    analysis.domain_classifier — nearest-centroid domain classifier
    reproduce_beta         — CLI reproduction script
"""

from genesis_os.science.analysis.beta_pipeline import BetaPipeline
from genesis_os.science.models.logistic_fit import UTACLogisticResult, fit_utac_logistic

__all__ = ["BetaPipeline", "UTACLogisticResult", "fit_utac_logistic"]
