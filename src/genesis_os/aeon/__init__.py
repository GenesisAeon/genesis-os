"""Aeon consciousness module — ported from Feldtheorie aeon/.

Scientific note: The Nullkern is an abstract state topology model,
not a claim about physical consciousness. The LanternNet 13.5 MHz
frequency and v_RIG=1351.8 km/s are research hypotheses (1.3% cosmic
dipole agreement), not verified physics.

Exports:
    Nullkern          — zero-point state kernel with UTAC activation
    AeonShell         — symbolic projection and signal containment
    SemanticAgent     — κ-field coupled semantic agent
    LanternNet        — 8 EM-coupled lantern architecture
    CoordinatorAgent  — NATS hub + global Q4 state authority (Phase 6)
    TransformAgent    — Sigillin snapshot generator (Phase 6)
    PhilosophyAgent   — Governance/ethics evaluator (Phase 6)
    UIAgent           — Human ↔ System boundary bridge (Phase 6)
    AgentLoop         — Continuous AI-UI-AI event loop (Phase 6)
    AgentMemory       — Sigillin-lineage state trajectory memory (Phase 6)
    PolicyEngine      — Transition authorization layer (Phase 6)
"""

from genesis_os.aeon.agents import (
    AgentLoop,
    AgentMemory,
    CoordinatorAgent,
    PhilosophyAgent,
    PolicyEngine,
    SemanticAgent,
    SigillinSnapshot,
    TransformAgent,
    UIAgent,
)
from genesis_os.aeon.lantern_net import LanternNet
from genesis_os.aeon.nullkern import Nullkern
from genesis_os.aeon.shell import AeonShell

__all__ = [
    "AeonShell",
    "AgentLoop",
    "AgentMemory",
    "CoordinatorAgent",
    "LanternNet",
    "Nullkern",
    "PhilosophyAgent",
    "PolicyEngine",
    "SemanticAgent",
    "SigillinSnapshot",
    "TransformAgent",
    "UIAgent",
]
