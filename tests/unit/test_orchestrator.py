"""Unit tests for genesis_os.core.orchestrator."""

from __future__ import annotations

import pytest

from genesis_os.core.orchestrator import GenesisConfig, GenesisOS, GenesisState
from genesis_os.core.phase import Phase

# ──────────────────────────────────────────────────────────────────────────────
# GenesisConfig
# ──────────────────────────────────────────────────────────────────────────────


class TestGenesisConfig:
    def test_default_values(self) -> None:
        cfg = GenesisConfig()
        assert cfg.entropy == pytest.approx(0.5)
        assert cfg.alpha == pytest.approx(0.1)
        assert cfg.max_cycles == 100
        assert cfg.seed is None

    def test_custom_values(self) -> None:
        cfg = GenesisConfig(entropy=0.3, alpha=0.05, max_cycles=50, seed=7)
        assert cfg.entropy == pytest.approx(0.3)
        assert cfg.seed == 7

    def test_entropy_validation_min(self) -> None:
        with pytest.raises(Exception):
            GenesisConfig(entropy=-0.1)

    def test_entropy_validation_max(self) -> None:
        with pytest.raises(Exception):
            GenesisConfig(entropy=1.1)

    def test_alpha_positive(self) -> None:
        with pytest.raises(Exception):
            GenesisConfig(alpha=0.0)

    def test_max_cycles_positive(self) -> None:
        with pytest.raises(Exception):
            GenesisConfig(max_cycles=0)

    def test_phi_init_positive(self) -> None:
        with pytest.raises(Exception):
            GenesisConfig(phi_init=0.0)


# ──────────────────────────────────────────────────────────────────────────────
# GenesisOS init
# ──────────────────────────────────────────────────────────────────────────────


class TestGenesisOSInit:
    def test_created_with_defaults(self) -> None:
        g = GenesisOS()
        assert g.config is not None

    def test_initial_phase_is_initiation(self, genesis: GenesisOS) -> None:
        assert genesis.phase == Phase.INITIATION

    def test_initial_entropy_from_config(self) -> None:
        cfg = GenesisConfig(entropy=0.3, seed=1)
        g = GenesisOS(config=cfg)
        assert g.state.entropy == pytest.approx(0.3)

    def test_initial_phi_from_config(self) -> None:
        cfg = GenesisConfig(phi_init=2.0, seed=1)
        g = GenesisOS(config=cfg)
        assert g.phi == pytest.approx(2.0)

    def test_initial_cycle_zero(self, genesis: GenesisOS) -> None:
        assert genesis.state.cycle == 0

    def test_state_is_genesis_state(self, genesis: GenesisOS) -> None:
        assert isinstance(genesis.state, GenesisState)


# ──────────────────────────────────────────────────────────────────────────────
# GenesisOS.step
# ──────────────────────────────────────────────────────────────────────────────


class TestGenesisOSStep:
    def test_step_returns_state(self, genesis: GenesisOS) -> None:
        state = genesis.step()
        assert isinstance(state, GenesisState)

    def test_step_increments_cycle(self, genesis: GenesisOS) -> None:
        genesis.step()
        assert genesis.state.cycle == 1

    def test_step_populates_crep(self, genesis: GenesisOS) -> None:
        state = genesis.step()
        assert state.crep is not None

    def test_step_produces_finite_lagrangian(self, genesis: GenesisOS) -> None:
        import math

        state = genesis.step()
        assert math.isfinite(state.lagrangian)

    def test_step_entropy_in_bounds(self, genesis: GenesisOS) -> None:
        state = genesis.step()
        assert 0.0 <= state.entropy <= 1.0

    def test_step_phi_positive(self, genesis: GenesisOS) -> None:
        state = genesis.step()
        assert state.phi > 0.0

    def test_multiple_steps_advance_cycle(self, genesis: GenesisOS) -> None:
        for _ in range(5):
            genesis.step()
        assert genesis.state.cycle == 5


# ──────────────────────────────────────────────────────────────────────────────
# GenesisOS.self_reflect
# ──────────────────────────────────────────────────────────────────────────────


class TestGenesisOSSelfReflect:
    def test_self_reflect_returns_float(self, genesis: GenesisOS) -> None:
        result = genesis.self_reflect()
        assert isinstance(result, float)

    def test_self_reflect_no_history_returns_initial_phi(self, genesis: GenesisOS) -> None:
        result = genesis.self_reflect()
        assert result == pytest.approx(genesis.config.phi_init)

    def test_self_reflect_updates_phi(self, genesis: GenesisOS) -> None:
        genesis.step()
        genesis.step()
        phi_before = genesis.phi
        phi_after = genesis.self_reflect()
        # phi may change
        assert isinstance(phi_after, float)
        assert phi_after > 0.0

    def test_phi_stays_positive_after_many_steps(self, genesis: GenesisOS) -> None:
        for _ in range(20):
            genesis.step()
        assert genesis.phi > 0.0


# ──────────────────────────────────────────────────────────────────────────────
# GenesisOS.phase_transition_loop
# ──────────────────────────────────────────────────────────────────────────────


class TestGenesisOSPhaseTransitionLoop:
    def test_loop_yields_states(self, genesis: GenesisOS) -> None:
        states = list(genesis.phase_transition_loop(max_cycles=5))
        assert len(states) == 5

    def test_loop_yields_genesis_state_instances(self, genesis: GenesisOS) -> None:
        for state in genesis.phase_transition_loop(max_cycles=3):
            assert isinstance(state, GenesisState)

    def test_loop_cycles_increase(self, genesis: GenesisOS) -> None:
        prev = 0
        for state in genesis.phase_transition_loop(max_cycles=5):
            assert state.cycle > prev
            prev = state.cycle

    def test_early_stop_via_callback(self, genesis: GenesisOS) -> None:
        states = []

        def stop_at_3(s: GenesisState) -> bool | None:
            states.append(s)
            return s.cycle >= 3

        list(genesis.phase_transition_loop(max_cycles=100, callback=stop_at_3))
        assert len(states) <= 4  # stops at or just after cycle 3

    def test_callback_none_runs_full(self, genesis: GenesisOS) -> None:
        states = list(genesis.phase_transition_loop(max_cycles=10))
        assert len(states) == 10

    def test_low_threshold_triggers_transitions(self, genesis_low_threshold: GenesisOS) -> None:
        final = genesis_low_threshold.run()
        assert len(final.transitions) > 0

    def test_high_threshold_no_transitions(self, genesis_high_threshold: GenesisOS) -> None:
        final = genesis_high_threshold.run()
        assert len(final.transitions) == 0


# ──────────────────────────────────────────────────────────────────────────────
# GenesisOS.run
# ──────────────────────────────────────────────────────────────────────────────


class TestGenesisOSRun:
    def test_run_returns_final_state(self, genesis: GenesisOS) -> None:
        state = genesis.run(max_cycles=5)
        assert isinstance(state, GenesisState)

    def test_run_respects_max_cycles(self) -> None:
        cfg = GenesisConfig(max_cycles=7, seed=1)
        g = GenesisOS(config=cfg)
        state = g.run()
        assert state.cycle == 7

    def test_run_with_override_max_cycles(self, genesis: GenesisOS) -> None:
        state = genesis.run(max_cycles=3)
        assert state.cycle == 3


# ──────────────────────────────────────────────────────────────────────────────
# GenesisOS.reset
# ──────────────────────────────────────────────────────────────────────────────


class TestGenesisOSReset:
    def test_reset_restores_phase(self, genesis: GenesisOS) -> None:
        genesis.run(max_cycles=5)
        genesis.reset()
        assert genesis.phase == Phase.INITIATION

    def test_reset_restores_cycle_zero(self, genesis: GenesisOS) -> None:
        genesis.run(max_cycles=5)
        genesis.reset()
        assert genesis.state.cycle == 0

    def test_reset_restores_entropy(self) -> None:
        cfg = GenesisConfig(entropy=0.3, seed=1)
        g = GenesisOS(config=cfg)
        g.run(max_cycles=5)
        g.reset()
        assert g.state.entropy == pytest.approx(0.3)

    def test_reset_restores_phi(self) -> None:
        cfg = GenesisConfig(phi_init=2.5, seed=1)
        g = GenesisOS(config=cfg)
        g.run(max_cycles=5)
        g.reset()
        assert g.phi == pytest.approx(2.5)

    def test_reset_clears_transitions(self, genesis_low_threshold: GenesisOS) -> None:
        genesis_low_threshold.run()
        genesis_low_threshold.reset()
        assert genesis_low_threshold.state.transitions == []


# ──────────────────────────────────────────────────────────────────────────────
# Plugin injection
# ──────────────────────────────────────────────────────────────────────────────


class TestGenesisOSPlugins:
    def test_plugin_called_each_step(self) -> None:
        call_count = [0]

        def my_plugin(state: GenesisState) -> dict:
            call_count[0] += 1
            return {}

        g = GenesisOS(config=GenesisConfig(seed=1), plugins={"test": my_plugin})
        g.run(max_cycles=5)
        assert call_count[0] == 5

    def test_plugin_data_accessible_in_metadata(self) -> None:
        def my_plugin(state: GenesisState) -> dict:
            return {"my_value": 42}

        g = GenesisOS(config=GenesisConfig(seed=1), plugins={"test": my_plugin})
        state = g.step()
        assert state.metadata.get("my_value") == 42

    def test_failing_plugin_does_not_crash(self) -> None:
        def bad_plugin(state: GenesisState) -> dict:
            raise RuntimeError("intentional failure")

        g = GenesisOS(config=GenesisConfig(seed=1), plugins={"bad": bad_plugin})
        state = g.step()  # should not raise
        assert state is not None
