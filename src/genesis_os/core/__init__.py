"""Core modules for genesis-os: orchestrator, CREP evaluation, and phase management."""

from __future__ import annotations

from genesis_os.core.crep import CREPEvaluator, CREPScore
from genesis_os.core.orchestrator import GenesisConfig, GenesisOS
from genesis_os.core.phase import Phase, PhaseMatrix, PhaseTransition

__all__ = [
    "CREPEvaluator",
    "CREPScore",
    "GenesisConfig",
    "GenesisOS",
    "Phase",
    "PhaseMatrix",
    "PhaseTransition",
]
