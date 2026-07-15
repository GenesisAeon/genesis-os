"""Universal structural constants for the UTAC resilience framework.

These values are invariant across all domains — only r (the domain
fingerprint) varies between physical and semantic systems.
"""

from __future__ import annotations

# CREP coupling structure constant (Römer 2026 whitepaper)
SIGMA: float = 2.2

# Frame-Principle boundary (1/16)
SIGMA_PHI: float = 1.0 / 16.0  # 0.0625

# Saturated-system ceiling — ERA5 Arctic is the most saturated known system
GAMMA_MAX: float = 0.920

# Coupling collapse threshold (empirically calibrated)
C_CRITICAL: float = 0.5

# Near-collapse warning: Ρ below this value triggers frame-principle alert
COLLAPSE_THRESHOLD: float = SIGMA_PHI
