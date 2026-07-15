"""Tests for RhoCalculator — benchmark targets from CREP Atlas."""

from __future__ import annotations

import pytest

from resilience_core.coupling import CouplingMatrix
from resilience_core.eigenrate import ResilienceEigenrate
from resilience_core.rho_calculator import RhoCalculator
from resilience_core.benchmarks.calibration import ATLAS_R_VALUES


def _make_calculator(r: float) -> RhoCalculator:
    return RhoCalculator(ResilienceEigenrate(r=r), CouplingMatrix())


def test_rho_amoc() -> None:
    """AMOC: Γ=0.251, r=r_required → Ρ ≈ 0.65 ± 0.10."""
    r = ATLAS_R_VALUES["amoc"]["r_required"]
    calc = _make_calculator(r)
    state = calc.compute(0.251, "amoc")
    assert 0.55 <= state.rho <= 0.75


def test_rho_arctic_near_collapse() -> None:
    """Arctic: Γ=0.920 → Ρ ≈ 0.05 (near collapse)."""
    r = ATLAS_R_VALUES["arctic"]["r_required"]
    calc = _make_calculator(r)
    state = calc.compute(0.920, "arctic")
    assert state.rho < 0.10
    assert state.near_collapse


def test_rho_sandpile() -> None:
    """Sandpile: Γ=0.296, r=r_required → Ρ ≈ 0.75 ± 0.10."""
    r = ATLAS_R_VALUES["sandpile"]["r_required"]
    calc = _make_calculator(r)
    state = calc.compute(0.296, "sandpile")
    assert 0.65 <= state.rho <= 0.85


def test_rho_quantum() -> None:
    """Quantum: Γ=0.050, r=r_required → Ρ ≈ 0.90 ± 0.05."""
    r = ATLAS_R_VALUES["quantum"]["r_required"]
    calc = _make_calculator(r)
    state = calc.compute(0.050, "quantum")
    assert 0.85 <= state.rho <= 0.95


def test_coupling_reduces_rho() -> None:
    coupling = CouplingMatrix()
    coupling.register_coupling("external", "target", effect=0.4)
    calc = RhoCalculator(ResilienceEigenrate(r=1.0), coupling)
    state_coupled = calc.compute(0.251, "target")
    uncoupled = RhoCalculator(ResilienceEigenrate(r=1.0), CouplingMatrix())
    state_free = uncoupled.compute(0.251, "target")
    assert state_coupled.rho < state_free.rho


def test_criticality_margin_at_gamma_max() -> None:
    calc = _make_calculator(r=1.0)
    state = calc.compute(0.920, "test")
    assert state.criticality_margin == pytest.approx(0.0, abs=1e-6)
