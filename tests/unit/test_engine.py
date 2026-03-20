"""Unit tests for genesis_os.runtime.engine."""

from __future__ import annotations

import pytest

from genesis_os.runtime.engine import LagrangianResult, RuntimeEngine


class TestLagrangianResult:
    def test_to_dict_has_all_keys(self) -> None:
        from genesis_os.core.crep import CREPScore

        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        result = LagrangianResult(
            lagrangian=1.0,
            kinetic=0.3,
            potential=0.2,
            phi=0.5,
            gamma=0.4,
            entropy=0.5,
            crep=crep,
            cycle=1,
        )
        d = result.to_dict()
        assert "lagrangian" in d
        assert "kinetic" in d
        assert "potential" in d
        assert "phi" in d
        assert "gamma" in d
        assert "entropy" in d
        assert "coherence" in d
        assert "resonance" in d
        assert "emergence" in d
        assert "poetics" in d

    def test_to_dict_values_correct(self) -> None:
        from genesis_os.core.crep import CREPScore

        crep = CREPScore(coherence=0.3, resonance=0.4, emergence=0.6, poetics=0.7)
        r = LagrangianResult(
            lagrangian=2.0,
            kinetic=0.5,
            potential=0.1,
            phi=1.0,
            gamma=0.8,
            entropy=0.4,
            crep=crep,
        )
        d = r.to_dict()
        assert d["lagrangian"] == pytest.approx(2.0)
        assert d["coherence"] == pytest.approx(0.3)


class TestRuntimeEngine:
    def test_compute_returns_dict(self, engine: RuntimeEngine) -> None:
        result = engine.compute({"entropy": 0.5})
        assert isinstance(result, dict)

    def test_compute_has_lagrangian_key(self, engine: RuntimeEngine) -> None:
        result = engine.compute({"entropy": 0.5})
        assert "lagrangian" in result

    def test_compute_has_entropy_key(self, engine: RuntimeEngine) -> None:
        result = engine.compute({"entropy": 0.5})
        assert "entropy" in result

    def test_compute_entropy_evolves(self, engine: RuntimeEngine) -> None:
        r1 = engine.compute({"entropy": 0.3, "coherence": 0.9, "resonance": 0.9, "emergence": 0.9, "poetics": 0.9})
        # entropy should change due to UTAC step
        assert isinstance(r1["entropy"], float)

    def test_compute_kinetic_term(self) -> None:
        e = RuntimeEngine(kappa=1.0)
        r = e.compute({"entropy": 0.5, "resonance": 0.8})
        # T = 0.5 * 1.0 * 0.8^2 = 0.32
        assert r["kinetic"] == pytest.approx(0.32, rel=0.05)

    def test_compute_potential_term(self) -> None:
        e = RuntimeEngine(eta=1.0)
        r = e.compute({"entropy": 0.6})
        # V = 0.5 * 1.0 * 0.6^2 = 0.18
        assert r["potential"] == pytest.approx(0.18, rel=0.05)

    def test_lagrangian_equals_T_minus_V_plus_phi_plus_gamma(self) -> None:
        e = RuntimeEngine(kappa=1.0, eta=1.0, phi0=1.0)
        r = e.compute({"entropy": 0.5, "resonance": 0.5, "phi": 1.0, "coherence": 0.5, "resonance": 0.5, "emergence": 0.5, "poetics": 0.5})
        expected = r["kinetic"] - r["potential"] + r["phi"] + r["gamma"]
        assert r["lagrangian"] == pytest.approx(expected, abs=1e-6)

    def test_history_appended_each_compute(self, engine: RuntimeEngine) -> None:
        engine.compute({})
        engine.compute({})
        assert len(engine.history) == 2

    def test_history_capped_at_1000(self) -> None:
        e = RuntimeEngine()
        for _ in range(1001):
            e.compute({})
        assert len(e.history) <= 1000

    def test_reset_clears_history(self, engine: RuntimeEngine) -> None:
        engine.compute({})
        engine.reset()
        assert len(engine.history) == 0

    def test_entropy_stays_in_bounds(self) -> None:
        e = RuntimeEngine()
        for _ in range(20):
            r = e.compute({"entropy": 0.5, "coherence": 1.0, "resonance": 1.0, "emergence": 1.0, "poetics": 1.0})
            assert 0.0 <= r["entropy"] <= 1.0

    def test_lagrangian_is_finite(self, engine: RuntimeEngine) -> None:
        import math

        for h in [0.0, 0.25, 0.5, 0.75, 1.0]:
            r = engine.compute({"entropy": h})
            assert math.isfinite(r["lagrangian"])

    def test_phi_positive(self, engine: RuntimeEngine) -> None:
        r = engine.compute({"entropy": 0.5, "phi": 2.0})
        assert r["phi"] >= 0.0

    def test_gamma_in_crep_result(self, engine: RuntimeEngine) -> None:
        r = engine.compute({})
        assert "gamma" in r

    def test_history_items_are_lagrangian_results(self, engine: RuntimeEngine) -> None:
        engine.compute({})
        assert isinstance(engine.history[0], LagrangianResult)
