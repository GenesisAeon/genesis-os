"""Aeon consciousness module — ported from Feldtheorie aeon/.

Scientific note: The Nullkern is an abstract state topology model,
not a claim about physical consciousness. The LanternNet 13.5 MHz
frequency and v_RIG=1351.8 km/s are research hypotheses (1.3% cosmic
dipole agreement), not verified physics.

Exports:
    Nullkern     — zero-point state kernel with UTAC activation
    AeonShell    — symbolic projection and signal containment
    SemanticAgent — κ-field coupled semantic agent
    LanternNet   — 8 EM-coupled lantern architecture
"""

from genesis_os.aeon.agents import SemanticAgent
from genesis_os.aeon.lantern_net import LanternNet
from genesis_os.aeon.nullkern import Nullkern
from genesis_os.aeon.shell import AeonShell

__all__ = ["AeonShell", "LanternNet", "Nullkern", "SemanticAgent"]
