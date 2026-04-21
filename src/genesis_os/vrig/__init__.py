"""v_RIG — Information-Geometric Velocity Framework.

Implements the Fisher-Rao information-geometric velocity for detecting
parameter-space regime changes in UTAC ODE fits.

Scientific note: The v_RIG constant ~1351.8 km/s arises from:
    c / (α · Φ) ≈ 299792.458 / (137.036 · 1.6180) ≈ 1351.8 km/s
This 1.3% agreement with the CMB dipole is a research hypothesis,
not a verified physical correspondence.

Primary application: detection of the ~1998 Arctic sea ice regime shift
via rolling-window UTAC parameter velocity spikes.
"""

from genesis_os.vrig.velocity import VRIGVelocity
from genesis_os.vrig.regime_detector import RegimeDetector

__all__ = ["VRIGVelocity", "RegimeDetector"]
