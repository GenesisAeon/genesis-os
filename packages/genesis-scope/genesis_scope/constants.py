"""Physical and mathematical constants for genesis-scope."""

from __future__ import annotations

import math

# Golden ratio — universal scaling constant across GenesisAeon
PHI: float = (1.0 + math.sqrt(5.0)) / 2.0
PHI_CBRT: float = PHI ** (1.0 / 3.0)  # ≈ 1.17480

# v_RIG: characteristic velocity in semantic parameter space (P31)
# Used as the drift-speed warning threshold in SessionTracker.
V_RIG_KM_S: float = 1352.12

# sigma_Phi frame principle: 1/16
SIGMA_PHI: float = 1.0 / 16.0

# Default drift / anchor parameters (empirically estimated from P17–P39 sessions)
KAPPA_DEFAULT: float = 0.30   # drift rate per session without anchors
LAMBDA_DEFAULT: float = 0.80  # anchor damping coefficient

# CREP collaboration regime bounds
GAMMA_COLLAB_MIN: float = 0.35
GAMMA_COLLAB_MAX: float = 0.55

# Q4 collaboration states (4-bit, 0000–1111)
Q4_STATE_COUNT: int = 16
