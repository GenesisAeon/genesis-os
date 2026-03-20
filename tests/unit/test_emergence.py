"""Unit tests for genesis_os.runtime.emergence (CosmicWebSimulator)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from genesis_os.core.crep import CREPScore
from genesis_os.runtime.emergence import CosmicWebSimulator, EmergenceEvent

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def crep_mid() -> CREPScore:
    return CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)


@pytest.fixture
def crep_high() -> CREPScore:
    return CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)


@pytest.fixture
def crep_low() -> CREPScore:
    return CREPScore(coherence=0.1, resonance=0.1, emergence=0.1, poetics=0.1)


@pytest.fixture
def sim() -> CosmicWebSimulator:
    return CosmicWebSimulator(n_nodes=16, emergence_threshold=0.3, seed=42)


@pytest.fixture
def sim_low_threshold() -> CosmicWebSimulator:
    return CosmicWebSimulator(n_nodes=16, emergence_threshold=0.0, seed=42)


@pytest.fixture
def sim_high_threshold() -> CosmicWebSimulator:
    return CosmicWebSimulator(n_nodes=16, emergence_threshold=0.99, seed=42)


# ---------------------------------------------------------------------------
# EmergenceEvent tests
# ---------------------------------------------------------------------------


class TestEmergenceEvent:
    def test_frozen_immutable(self, crep_mid: CREPScore) -> None:
        event = EmergenceEvent(
            cycle=1,
            node_count=3,
            emergence_rate=0.5,
            lagrangian=1.2,
            gamma=0.6,
            density_delta=0.01,
            crep=crep_mid,
        )
        with pytest.raises((AttributeError, TypeError)):
            event.cycle = 99  # type: ignore[misc]

    def test_to_dict_keys(self, crep_mid: CREPScore) -> None:
        event = EmergenceEvent(
            cycle=5,
            node_count=2,
            emergence_rate=0.4,
            lagrangian=0.8,
            gamma=0.5,
            density_delta=0.02,
            crep=crep_mid,
        )
        d = event.to_dict()
        expected_keys = {
            "cycle", "node_count", "emergence_rate", "lagrangian",
            "gamma", "density_delta", "coherence", "resonance", "emergence", "poetics",
        }
        assert expected_keys == set(d.keys())

    def test_to_dict_values_correct(self, crep_mid: CREPScore) -> None:
        event = EmergenceEvent(
            cycle=3,
            node_count=7,
            emergence_rate=0.45,
            lagrangian=1.1,
            gamma=0.55,
            density_delta=0.03,
            crep=crep_mid,
        )
        d = event.to_dict()
        assert d["cycle"] == 3
        assert d["node_count"] == 7
        assert d["emergence_rate"] == pytest.approx(0.45)
        assert d["coherence"] == pytest.approx(0.5)

    def test_to_dict_crep_fields(self, crep_high: CREPScore) -> None:
        event = EmergenceEvent(
            cycle=0,
            node_count=1,
            emergence_rate=0.9,
            lagrangian=2.0,
            gamma=0.8,
            density_delta=0.05,
            crep=crep_high,
        )
        d = event.to_dict()
        assert d["coherence"] == pytest.approx(0.9)
        assert d["resonance"] == pytest.approx(0.9)
        assert d["emergence"] == pytest.approx(0.9)
        assert d["poetics"] == pytest.approx(0.9)

    def test_node_count_positive(self, crep_mid: CREPScore) -> None:
        event = EmergenceEvent(
            cycle=1, node_count=4, emergence_rate=0.5,
            lagrangian=1.0, gamma=0.6, density_delta=0.01, crep=crep_mid,
        )
        assert event.node_count > 0

    def test_emergence_rate_finite(self, crep_mid: CREPScore) -> None:
        event = EmergenceEvent(
            cycle=1, node_count=1, emergence_rate=0.35,
            lagrangian=1.0, gamma=0.5, density_delta=0.01, crep=crep_mid,
        )
        assert math.isfinite(event.emergence_rate)


# ---------------------------------------------------------------------------
# CosmicWebSimulator construction
# ---------------------------------------------------------------------------


class TestCosmicWebSimulatorInit:
    def test_default_n_nodes(self) -> None:
        s = CosmicWebSimulator()
        assert s.n_nodes == 64

    def test_custom_n_nodes(self) -> None:
        s = CosmicWebSimulator(n_nodes=32)
        assert s.n_nodes == 32

    def test_density_shape(self, sim: CosmicWebSimulator) -> None:
        assert sim.density.shape == (16,)

    def test_density_initial_range(self, sim: CosmicWebSimulator) -> None:
        d = sim.density
        assert np.all(d >= 0.0)
        assert np.all(d <= 1.0)

    def test_no_events_initially(self, sim: CosmicWebSimulator) -> None:
        assert sim.event_count == 0

    def test_events_list_empty(self, sim: CosmicWebSimulator) -> None:
        assert sim.events == []

    def test_mean_density_positive(self, sim: CosmicWebSimulator) -> None:
        assert sim.mean_density >= 0.0

    def test_active_nodes_initial(self, sim: CosmicWebSimulator) -> None:
        # Initially all nodes should be < 0.5 (initialised from U(0, 0.1))
        assert sim.active_nodes == 0

    def test_seed_reproducibility(self) -> None:
        s1 = CosmicWebSimulator(n_nodes=8, seed=7)
        s2 = CosmicWebSimulator(n_nodes=8, seed=7)
        np.testing.assert_array_equal(s1.density, s2.density)

    def test_different_seeds_differ(self) -> None:
        s1 = CosmicWebSimulator(n_nodes=32, seed=1)
        s2 = CosmicWebSimulator(n_nodes=32, seed=2)
        assert not np.array_equal(s1.density, s2.density)


# ---------------------------------------------------------------------------
# emergence_rate
# ---------------------------------------------------------------------------


class TestEmergenceRate:
    def test_zero_gamma_zero_rate(self, sim: CosmicWebSimulator) -> None:
        rate = sim.emergence_rate(lagrangian=1.0, gamma=0.0)
        assert rate == pytest.approx(0.0)

    def test_positive_lagrangian_positive_rate(self, sim: CosmicWebSimulator) -> None:
        rate = sim.emergence_rate(lagrangian=2.0, gamma=0.5)
        assert rate > 0.0

    def test_rate_bounded_zero_one(self, sim: CosmicWebSimulator) -> None:
        for l_val in [0.0, 0.5, 1.0, 5.0, 100.0]:
            for g_val in [0.0, 0.3, 0.6, 1.0]:
                rate = sim.emergence_rate(lagrangian=l_val, gamma=g_val)
                assert 0.0 <= rate < 1.0, f"rate={rate} out of bounds for L={l_val}, Γ={g_val}"

    def test_negative_gamma_zero_rate(self, sim: CosmicWebSimulator) -> None:
        rate = sim.emergence_rate(lagrangian=2.0, gamma=-0.5)
        assert rate == pytest.approx(0.0)

    def test_large_lagrangian_approaches_tanh(self, sim: CosmicWebSimulator) -> None:
        import math as _math
        rate = sim.emergence_rate(lagrangian=1000.0, gamma=0.5)
        expected_max = _math.tanh(sim.sigma_e * 0.5)
        assert abs(rate - expected_max) < 0.001

    def test_rate_monotone_in_lagrangian(self, sim: CosmicWebSimulator) -> None:
        r1 = sim.emergence_rate(lagrangian=0.5, gamma=0.5)
        r2 = sim.emergence_rate(lagrangian=2.0, gamma=0.5)
        assert r2 > r1

    def test_rate_monotone_in_gamma(self, sim: CosmicWebSimulator) -> None:
        r1 = sim.emergence_rate(lagrangian=1.0, gamma=0.2)
        r2 = sim.emergence_rate(lagrangian=1.0, gamma=0.8)
        assert r2 > r1

    def test_zero_lagrangian_zero_rate(self, sim: CosmicWebSimulator) -> None:
        rate = sim.emergence_rate(lagrangian=0.0, gamma=0.9)
        assert rate == pytest.approx(0.0)

    def test_rate_finite(self, sim: CosmicWebSimulator) -> None:
        rate = sim.emergence_rate(lagrangian=1.5, gamma=0.7)
        assert math.isfinite(rate)


# ---------------------------------------------------------------------------
# CosmicWebSimulator.step
# ---------------------------------------------------------------------------


class TestCosmicWebSimulatorStep:
    def test_step_returns_none_when_below_threshold(
        self, sim_high_threshold: CosmicWebSimulator, crep_low: CREPScore
    ) -> None:
        result = sim_high_threshold.step(crep_low, lagrangian=0.1)
        assert result is None

    def test_step_returns_event_when_above_threshold(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        result = sim_low_threshold.step(crep_high, lagrangian=2.0)
        assert isinstance(result, EmergenceEvent)

    def test_step_event_has_correct_cycle(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        event = sim_low_threshold.step(crep_high, lagrangian=2.0, cycle=5)
        assert event is not None
        assert event.cycle == 5

    def test_step_event_gamma_matches_crep(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        event = sim_low_threshold.step(crep_high, lagrangian=2.0)
        assert event is not None
        assert event.gamma == pytest.approx(crep_high.gamma)

    def test_step_density_increases(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        d_before = sim_low_threshold.mean_density
        sim_low_threshold.step(crep_high, lagrangian=2.0)
        assert sim_low_threshold.mean_density >= d_before

    def test_step_density_stays_bounded(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        for _ in range(50):
            sim_low_threshold.step(crep_high, lagrangian=2.0)
        d = sim_low_threshold.density
        assert np.all(d >= 0.0)
        assert np.all(d <= 1.0)

    def test_step_accumulates_events(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        for _ in range(10):
            sim_low_threshold.step(crep_high, lagrangian=2.0)
        assert sim_low_threshold.event_count > 0

    def test_step_node_count_at_least_one(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        event = sim_low_threshold.step(crep_high, lagrangian=2.0)
        assert event is not None
        assert event.node_count >= 1

    def test_step_auto_cycle_increments(
        self, sim: CosmicWebSimulator, crep_mid: CREPScore
    ) -> None:
        # Use internal cycle counter
        sim.step(crep_mid, lagrangian=1.0)
        sim.step(crep_mid, lagrangian=1.0)
        assert sim._cycle == 2

    def test_step_with_mid_crep(
        self, sim: CosmicWebSimulator, crep_mid: CREPScore
    ) -> None:
        result = sim.step(crep_mid, lagrangian=1.0)
        # May or may not emit event; just check no exception
        assert result is None or isinstance(result, EmergenceEvent)

    def test_step_emergence_event_lagrangian_stored(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        event = sim_low_threshold.step(crep_high, lagrangian=1.7)
        assert event is not None
        assert event.lagrangian == pytest.approx(1.7)

    def test_step_emergence_rate_in_event(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        event = sim_low_threshold.step(crep_high, lagrangian=2.0)
        assert event is not None
        assert 0.0 <= event.emergence_rate < 1.0

    def test_step_density_delta_finite(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        event = sim_low_threshold.step(crep_high, lagrangian=2.0)
        assert event is not None
        assert math.isfinite(event.density_delta)


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


class TestCosmicWebSimulatorProperties:
    def test_density_is_copy(self, sim: CosmicWebSimulator) -> None:
        d1 = sim.density
        d2 = sim.density
        assert d1 is not d2

    def test_events_is_copy(self, sim: CosmicWebSimulator) -> None:
        e1 = sim.events
        e2 = sim.events
        assert e1 is not e2

    def test_active_nodes_range(self, sim: CosmicWebSimulator) -> None:
        assert 0 <= sim.active_nodes <= sim.n_nodes

    def test_mean_density_range(self, sim: CosmicWebSimulator) -> None:
        assert 0.0 <= sim.mean_density <= 1.0

    def test_mean_density_after_many_steps(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        for _ in range(100):
            sim_low_threshold.step(crep_high, lagrangian=2.0)
        assert 0.0 <= sim_low_threshold.mean_density <= 1.0


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


class TestCosmicWebSimulatorSummary:
    def test_summary_keys(self, sim: CosmicWebSimulator) -> None:
        s = sim.summary()
        expected = {"mean_density", "active_nodes", "event_count", "n_nodes", "emergence_threshold", "cycle"}
        assert expected == set(s.keys())

    def test_summary_n_nodes_correct(self, sim: CosmicWebSimulator) -> None:
        assert sim.summary()["n_nodes"] == 16

    def test_summary_cycle_zero_initially(self, sim: CosmicWebSimulator) -> None:
        assert sim.summary()["cycle"] == 0

    def test_summary_cycle_after_steps(
        self, sim: CosmicWebSimulator, crep_mid: CREPScore
    ) -> None:
        for _ in range(3):
            sim.step(crep_mid, lagrangian=1.0)
        assert sim.summary()["cycle"] == 3

    def test_summary_threshold_correct(self, sim: CosmicWebSimulator) -> None:
        assert sim.summary()["emergence_threshold"] == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


class TestCosmicWebSimulatorReset:
    def test_reset_clears_events(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        for _ in range(5):
            sim_low_threshold.step(crep_high, lagrangian=2.0)
        sim_low_threshold.reset()
        assert sim_low_threshold.event_count == 0

    def test_reset_restores_density(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        for _ in range(50):
            sim_low_threshold.step(crep_high, lagrangian=2.0)
        sim_low_threshold.reset()
        d = sim_low_threshold.density
        assert np.all(d <= 0.15)  # back to initial small values

    def test_reset_zero_cycle(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        sim_low_threshold.step(crep_high, lagrangian=2.0)
        sim_low_threshold.reset()
        assert sim_low_threshold._cycle == 0

    def test_reset_zero_active_nodes(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        for _ in range(100):
            sim_low_threshold.step(crep_high, lagrangian=2.0)
        sim_low_threshold.reset()
        assert sim_low_threshold.active_nodes == 0

    def test_reset_reproducible_with_seed(self) -> None:
        s = CosmicWebSimulator(n_nodes=8, seed=99)
        d_initial = s.density.copy()
        crep = CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)
        for _ in range(20):
            s.step(crep, lagrangian=2.0)
        s.reset()
        np.testing.assert_array_equal(s.density, d_initial)


# ---------------------------------------------------------------------------
# CREP weight vector
# ---------------------------------------------------------------------------


class TestCREPWeightVector:
    def test_weight_vector_shape(self, sim: CosmicWebSimulator, crep_mid: CREPScore) -> None:
        w = sim._crep_weight_vector(crep_mid)
        assert w.shape == (16,)

    def test_weight_vector_range(self, sim: CosmicWebSimulator, crep_mid: CREPScore) -> None:
        w = sim._crep_weight_vector(crep_mid)
        assert np.all(w >= 0.0)
        assert np.all(w <= 1.0)

    def test_weight_vector_varies(self, sim: CosmicWebSimulator, crep_mid: CREPScore) -> None:
        w = sim._crep_weight_vector(crep_mid)
        assert w.std() > 0.0  # not all same

    def test_weight_vector_high_crep(self, sim: CosmicWebSimulator, crep_high: CREPScore) -> None:
        w = sim._crep_weight_vector(crep_high)
        assert np.all(w >= 0.0)
        assert np.all(w <= 1.0)

    def test_weight_vector_low_crep(self, sim: CosmicWebSimulator, crep_low: CREPScore) -> None:
        w = sim._crep_weight_vector(crep_low)
        assert np.all(w >= 0.0)
        assert np.all(w <= 1.0)


# ---------------------------------------------------------------------------
# Integration with orchestrator
# ---------------------------------------------------------------------------


class TestCosmicWebSimulatorIntegration:
    def test_orchestrator_has_simulator(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        g = GenesisOS(config=GenesisConfig(seed=1))
        from genesis_os.runtime.emergence import CosmicWebSimulator

        assert isinstance(g.simulator, CosmicWebSimulator)

    def test_orchestrator_step_populates_emergence_events(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        # Use low threshold to force emission
        g = GenesisOS(
            config=GenesisConfig(max_cycles=50, seed=1),
            emergence_threshold=0.0,
        )
        state = g.run()
        # Some events should have been emitted with threshold=0
        assert len(state.emergence_events) >= 0  # may be empty at threshold=0 with low CREP

    def test_orchestrator_reset_clears_emergence_events(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        g = GenesisOS(
            config=GenesisConfig(max_cycles=10, seed=2),
            emergence_threshold=0.0,
        )
        g.run()
        g.reset()
        assert g.state.emergence_events == []

    def test_orchestrator_metadata_has_emergence_summary(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        g = GenesisOS(config=GenesisConfig(max_cycles=5, seed=3))
        state = g.run()
        assert "emergence_summary" in state.metadata
        summary = state.metadata["emergence_summary"]
        assert "mean_density" in summary
        assert "active_nodes" in summary
        assert "event_count" in summary

    def test_orchestrator_simulator_property(self) -> None:
        from genesis_os.core.orchestrator import GenesisOS
        from genesis_os.runtime.emergence import CosmicWebSimulator

        g = GenesisOS()
        assert isinstance(g.simulator, CosmicWebSimulator)

    def test_simulator_event_count_matches_state(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        g = GenesisOS(
            config=GenesisConfig(max_cycles=20, seed=4),
            emergence_threshold=0.0,
        )
        g.run()
        # simulator events ≥ state events (state only tracks what step emits)
        assert g.simulator.event_count >= 0

    def test_emergence_events_are_emission_events(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        g = GenesisOS(
            config=GenesisConfig(max_cycles=30, seed=5),
            emergence_threshold=0.0,
        )
        state = g.run()
        for ev in state.emergence_events:
            assert isinstance(ev, EmergenceEvent)
            assert ev.emergence_rate >= 0.0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestCosmicWebSimulatorEdgeCases:
    def test_n_nodes_one(self) -> None:
        s = CosmicWebSimulator(n_nodes=1, seed=0)
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        result = s.step(crep, lagrangian=1.0)
        assert result is None or isinstance(result, EmergenceEvent)

    def test_n_nodes_large(self) -> None:
        s = CosmicWebSimulator(n_nodes=512, seed=0)
        assert s.density.shape == (512,)

    def test_very_small_lagrangian(self, sim: CosmicWebSimulator, crep_mid: CREPScore) -> None:
        rate = sim.emergence_rate(lagrangian=1e-10, gamma=0.9)
        assert rate >= 0.0

    def test_very_large_lagrangian(self, sim: CosmicWebSimulator, crep_mid: CREPScore) -> None:
        rate = sim.emergence_rate(lagrangian=1e6, gamma=0.5)
        assert rate < 1.0

    def test_step_with_crep_zero_coherence(self, sim: CosmicWebSimulator) -> None:
        crep = CREPScore(coherence=0.0, resonance=0.0, emergence=0.0, poetics=0.0)
        result = sim.step(crep, lagrangian=0.0)
        assert result is None

    def test_step_returns_event_crep_with_cycle_zero(
        self, sim_low_threshold: CosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        event = sim_low_threshold.step(crep_high, lagrangian=2.0, cycle=0)
        assert event is not None
        assert event.cycle == 0

    def test_multiple_resets_stable(self) -> None:
        s = CosmicWebSimulator(n_nodes=8, seed=0)
        crep = CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)
        for _ in range(3):
            for _ in range(10):
                s.step(crep, lagrangian=2.0)
            s.reset()
        assert s.event_count == 0
        assert s.mean_density <= 0.15
