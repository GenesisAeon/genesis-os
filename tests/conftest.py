"""Shared pytest fixtures for genesis-os tests."""

from __future__ import annotations

import pytest

from genesis_os.core.crep import CREPEvaluator, CREPScore
from genesis_os.core.orchestrator import GenesisConfig, GenesisOS
from genesis_os.core.phase import Phase, PhaseMatrix
from genesis_os.runtime.engine import RuntimeEngine
from genesis_os.runtime.utac import UTACLogistic

# ──────────────────────────────────────────────────────────────────────────────
# CREP fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def crep_score_mid() -> CREPScore:
    return CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)


@pytest.fixture
def crep_score_high() -> CREPScore:
    return CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)


@pytest.fixture
def crep_score_low() -> CREPScore:
    return CREPScore(coherence=0.1, resonance=0.1, emergence=0.1, poetics=0.1)


@pytest.fixture
def crep_evaluator() -> CREPEvaluator:
    return CREPEvaluator()


# ──────────────────────────────────────────────────────────────────────────────
# Phase fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def phase_matrix() -> PhaseMatrix:
    return PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.0))


@pytest.fixture
def phase_matrix_high_threshold() -> PhaseMatrix:
    return PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.99))


# ──────────────────────────────────────────────────────────────────────────────
# Engine fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def engine() -> RuntimeEngine:
    return RuntimeEngine()


@pytest.fixture
def utac() -> UTACLogistic:
    return UTACLogistic()


# ──────────────────────────────────────────────────────────────────────────────
# GenesisOS fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def config_default() -> GenesisConfig:
    return GenesisConfig(seed=42)


@pytest.fixture
def config_low_entropy() -> GenesisConfig:
    return GenesisConfig(entropy=0.1, seed=42)


@pytest.fixture
def config_high_entropy() -> GenesisConfig:
    return GenesisConfig(entropy=0.9, seed=42)


@pytest.fixture
def genesis(config_default: GenesisConfig) -> GenesisOS:
    return GenesisOS(config=config_default)


@pytest.fixture
def genesis_low_threshold() -> GenesisOS:
    config = GenesisConfig(transition_threshold=0.0, max_cycles=10, seed=42)
    return GenesisOS(config=config)


@pytest.fixture
def genesis_high_threshold() -> GenesisOS:
    config = GenesisConfig(transition_threshold=0.99, max_cycles=10, seed=42)
    return GenesisOS(config=config)
