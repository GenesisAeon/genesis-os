"""Constants for the semantic UTAC mapping (scope-resilience, Package 41)."""

from __future__ import annotations

# Universal structural constants (same as resilience-core)
SIGMA: float = 2.2
SIGMA_PHI: float = 1.0 / 16.0   # 0.0625
GAMMA_MAX: float = 0.920

# Critical semantic drift rate per conversation step
GAMMA_DOT_CRITICAL: float = 0.10

# Default sliding-window size for drift monitoring
DRIFT_WINDOW_DEFAULT: int = 5

# Risk thresholds for Ρ_sem
RHO_SAFE_THRESHOLD: float = 0.70
RHO_MODERATE_THRESHOLD: float = 0.40
RHO_HIGH_RISK_THRESHOLD: float = 0.10
