"""End-to-end tests for the complete Genesis cycle.

These tests verify the full integration: orchestrator → engine → CREP →
phase transitions → dashboard → CLI.
"""

from __future__ import annotations

import json
import math

import pytest
from typer.testing import CliRunner

from genesis_os import GenesisOS, __version__
from genesis_os.cli.main import app
from genesis_os.core.orchestrator import GenesisConfig, GenesisState
from genesis_os.core.phase import Phase
from genesis_os.dashboard.mandala import MandalaDashboard
from genesis_os.dashboard.sonification import Sonifier

runner = CliRunner()


class TestFullCycle:
    def test_complete_run_returns_state(self) -> None:
        cfg = GenesisConfig(entropy=0.4, max_cycles=20, seed=7)
        g = GenesisOS(config=cfg)
        state = g.run()
        assert isinstance(state, GenesisState)
        assert state.cycle == 20

    def test_entropy_evolves_over_cycle(self) -> None:
        cfg = GenesisConfig(entropy=0.3, max_cycles=10, seed=1)
        g = GenesisOS(config=cfg)
        initial_entropy = g.state.entropy
        state = g.run()
        # Entropy should have changed
        assert state.entropy != initial_entropy or state.cycle == 0

    def test_crep_populated_after_cycle(self) -> None:
        cfg = GenesisConfig(max_cycles=5, seed=2)
        g = GenesisOS(config=cfg)
        state = g.run()
        assert state.crep is not None

    def test_crep_values_in_unit_interval(self) -> None:
        cfg = GenesisConfig(max_cycles=10, seed=3)
        g = GenesisOS(config=cfg)
        state = g.run()
        assert state.crep is not None
        assert 0.0 <= state.crep.coherence <= 1.0
        assert 0.0 <= state.crep.resonance <= 1.0
        assert 0.0 <= state.crep.emergence <= 1.0
        assert 0.0 <= state.crep.poetics <= 1.0

    def test_lagrangian_finite(self) -> None:
        cfg = GenesisConfig(max_cycles=10, seed=4)
        g = GenesisOS(config=cfg)
        state = g.run()
        assert math.isfinite(state.lagrangian)

    def test_phi_positive_after_cycle(self) -> None:
        cfg = GenesisConfig(max_cycles=15, seed=5)
        g = GenesisOS(config=cfg)
        state = g.run()
        assert state.phi > 0.0

    def test_phase_valid_after_cycle(self) -> None:
        cfg = GenesisConfig(max_cycles=10, seed=6)
        g = GenesisOS(config=cfg)
        state = g.run()
        assert state.phase in list(Phase)

    def test_low_threshold_produces_transitions(self) -> None:
        cfg = GenesisConfig(transition_threshold=0.0, max_cycles=20, seed=7)
        g = GenesisOS(config=cfg)
        state = g.run()
        assert len(state.transitions) > 0

    def test_transitions_are_sequential(self) -> None:
        cfg = GenesisConfig(transition_threshold=0.0, max_cycles=16, seed=8)
        g = GenesisOS(config=cfg)
        state = g.run()
        for t in state.transitions:
            assert t.to_phase == t.from_phase.next_phase

    def test_transitions_have_positive_gamma(self) -> None:
        cfg = GenesisConfig(transition_threshold=0.0, max_cycles=20, seed=9)
        g = GenesisOS(config=cfg)
        state = g.run()
        for t in state.transitions:
            assert t.trigger_gamma >= 0.0

    def test_reset_restores_clean_state(self) -> None:
        cfg = GenesisConfig(entropy=0.3, max_cycles=10, seed=10)
        g = GenesisOS(config=cfg)
        g.run()
        g.reset()
        assert g.state.cycle == 0
        assert g.state.entropy == pytest.approx(0.3)
        assert g.phase == Phase.INITIATION

    def test_rerun_after_reset_same_result(self) -> None:
        cfg = GenesisConfig(entropy=0.4, max_cycles=5, seed=11)
        g = GenesisOS(config=cfg)
        state1 = g.run()
        g.reset()
        state2 = g.run()
        assert state1.cycle == state2.cycle
        assert state1.entropy == pytest.approx(state2.entropy, rel=1e-5)

    def test_generator_loop_yields_correct_count(self) -> None:
        cfg = GenesisConfig(max_cycles=8, seed=12)
        g = GenesisOS(config=cfg)
        states = list(g.phase_transition_loop())
        assert len(states) == 8


class TestCycleDashboardIntegration:
    def test_mandala_renders_all_cycles(self) -> None:
        cfg = GenesisConfig(max_cycles=5, seed=20)
        g = GenesisOS(config=cfg)
        dashboard = MandalaDashboard(use_plugin=False)
        for state in g.phase_transition_loop():
            if state.crep:
                dashboard.render_ascii(state.crep, state.phase, state.cycle)
        assert len(dashboard.frames) == 5

    def test_sonification_sequence_length(self) -> None:
        cfg = GenesisConfig(max_cycles=5, seed=21)
        g = GenesisOS(config=cfg)
        sonifier = Sonifier(use_plugin=False)
        crep_scores = []
        for state in g.phase_transition_loop():
            if state.crep:
                crep_scores.append(state.crep)
        frames = sonifier.sequence(crep_scores)
        assert len(frames) == len(crep_scores)

    def test_sonification_frequencies_finite(self) -> None:
        cfg = GenesisConfig(max_cycles=5, seed=22)
        g = GenesisOS(config=cfg)
        sonifier = Sonifier(use_plugin=False)
        for state in g.phase_transition_loop():
            if state.crep:
                frame = sonifier.crep_to_frequencies(state.crep)
                for f in frame.frequencies.values():
                    assert math.isfinite(f)
                    assert f > 0.0


class TestCycleCLIIntegration:
    def test_cli_cycle_simulate_complete(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "10", "--seed", "42"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["cycles"] == 10

    def test_cli_cycle_simulate_low_entropy(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--entropy", "0.1", "--max-cycles", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 0.0 <= data["entropy"] <= 1.0

    def test_cli_cycle_simulate_high_entropy(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--entropy", "0.9", "--max-cycles", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 0.0 <= data["entropy"] <= 1.0

    def test_cli_cycle_simulate_phi_positive(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "5"])
        data = json.loads(result.output)
        assert data["phi"] > 0.0

    def test_cli_phases_all_four(self) -> None:
        result = runner.invoke(app, ["phases"])
        for phase in Phase:
            assert phase.value in result.output

    def test_cli_info_has_version(self) -> None:
        result = runner.invoke(app, ["info"])
        assert __version__ in result.output

    def test_cli_full_run_deterministic_with_seed(self) -> None:
        args = ["cycle", "--simulate", "--seed", "99", "--max-cycles", "5"]
        r1 = json.loads(runner.invoke(app, args).output)
        r2 = json.loads(runner.invoke(app, args).output)
        assert r1["entropy"] == pytest.approx(r2["entropy"], rel=1e-5)
        assert r1["phi"] == pytest.approx(r2["phi"], rel=1e-5)


class TestMultiPhaseFullCycle:
    """Verify that a full 4-phase CREP cycle completes correctly."""

    def test_four_transitions_cycle_phase(self) -> None:
        from genesis_os.core.phase import PhaseMatrix

        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.0))
        for _ in range(4):
            pm.advance(0.5)
        assert pm.current_phase == Phase.INITIATION
        assert pm.full_cycles == 1

    def test_eight_transitions_two_full_cycles(self) -> None:
        from genesis_os.core.phase import PhaseMatrix

        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.0))
        for _ in range(8):
            pm.advance(0.5)
        assert pm.full_cycles == 2

    def test_genesis_transitions_record_from_to(self) -> None:
        cfg = GenesisConfig(transition_threshold=0.0, max_cycles=4, seed=1)
        g = GenesisOS(config=cfg)
        state = g.run()
        for t in state.transitions:
            assert t.to_phase == t.from_phase.next_phase

    def test_crep_gamma_drives_transition(self) -> None:
        """Verify that transitions only happen when gamma ≥ threshold."""
        cfg = GenesisConfig(transition_threshold=0.8, max_cycles=50, seed=5)
        g = GenesisOS(config=cfg)
        state = g.run()
        for t in state.transitions:
            assert t.trigger_gamma >= 0.8
