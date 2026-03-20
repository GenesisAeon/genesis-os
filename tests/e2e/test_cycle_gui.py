"""End-to-end tests for the genesis-os v0.2.0 cycle with GUI and emergence.

Tests cover:
- CLI cycle with emergence JSON output
- CosmicWebSimulator integration in full cycles
- GUI snapshot generation without a live server
- Contract: emergence_events in final state
"""

from __future__ import annotations

import json
import math

import pytest
from typer.testing import CliRunner

from genesis_os import CosmicWebSimulator, GenesisOS, __version__
from genesis_os.cli.main import app
from genesis_os.core.orchestrator import GenesisConfig, GenesisState
from genesis_os.dashboard.web_gui import GenesisWebGUI, GUISnapshot
from genesis_os.runtime.emergence import EmergenceEvent

runner = CliRunner()


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


class TestVersion:
    def test_version_is_0_2_0(self) -> None:
        assert __version__ == "0.2.0"

    def test_cli_info_shows_0_2_0(self) -> None:
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output


# ---------------------------------------------------------------------------
# CLI simulate with emergence fields
# ---------------------------------------------------------------------------


class TestCLISimulateEmergence:
    def test_simulate_has_emergence_events_key(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "10", "--seed", "42"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "emergence_events" in data

    def test_simulate_emergence_events_non_negative(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "10", "--seed", "1"])
        data = json.loads(result.output)
        assert data["emergence_events"] >= 0

    def test_simulate_has_emergence_summary_key(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "10", "--seed", "2"])
        data = json.loads(result.output)
        assert "emergence_summary" in data

    def test_simulate_emergence_summary_mean_density(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "10", "--seed", "3"])
        data = json.loads(result.output)
        summary = data["emergence_summary"]
        assert "mean_density" in summary
        assert 0.0 <= summary["mean_density"] <= 1.0

    def test_simulate_emergence_summary_active_nodes(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "10", "--seed", "4"])
        data = json.loads(result.output)
        summary = data["emergence_summary"]
        assert "active_nodes" in summary
        assert summary["active_nodes"] >= 0

    def test_simulate_emergence_summary_event_count(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "10", "--seed", "5"])
        data = json.loads(result.output)
        summary = data["emergence_summary"]
        assert "event_count" in summary

    def test_simulate_version_0_2_0(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "5"])
        data = json.loads(result.output)
        assert data["version"] == "0.2.0"

    def test_simulate_deterministic_emergence_with_seed(self) -> None:
        args = ["cycle", "--simulate", "--seed", "77", "--max-cycles", "10"]
        r1 = json.loads(runner.invoke(app, args).output)
        r2 = json.loads(runner.invoke(app, args).output)
        assert r1["emergence_events"] == r2["emergence_events"]
        assert r1["emergence_summary"]["mean_density"] == pytest.approx(
            r2["emergence_summary"]["mean_density"], rel=1e-5
        )

    def test_simulate_entropy_in_bounds_after_emergence(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "20", "--seed", "6"])
        data = json.loads(result.output)
        assert 0.0 <= data["entropy"] <= 1.0


# ---------------------------------------------------------------------------
# CLI cycle with --phases prints emergence events
# ---------------------------------------------------------------------------


class TestCLICycleWithPhases:
    def test_cycle_phases_runs_without_error(self) -> None:
        result = runner.invoke(app, ["cycle", "--phases", "--max-cycles", "5", "--seed", "10"])
        assert result.exit_code == 0

    def test_cycle_with_all_flags_runs(self) -> None:
        result = runner.invoke(
            app,
            ["cycle", "--phases", "--simulate", "--max-cycles", "5", "--seed", "11"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "emergence_events" in data


# ---------------------------------------------------------------------------
# Full cycle emergence integration
# ---------------------------------------------------------------------------


class TestFullCycleEmergence:
    def test_state_has_emergence_events_field(self) -> None:
        cfg = GenesisConfig(max_cycles=10, seed=20)
        g = GenesisOS(config=cfg)
        state = g.run()
        assert hasattr(state, "emergence_events")
        assert isinstance(state.emergence_events, list)

    def test_emergence_events_all_are_events(self) -> None:
        cfg = GenesisConfig(max_cycles=20, seed=21)
        g = GenesisOS(config=cfg, emergence_threshold=0.0)
        state = g.run()
        for ev in state.emergence_events:
            assert isinstance(ev, EmergenceEvent)

    def test_emergence_events_have_valid_rates(self) -> None:
        cfg = GenesisConfig(max_cycles=20, seed=22)
        g = GenesisOS(config=cfg, emergence_threshold=0.0)
        state = g.run()
        for ev in state.emergence_events:
            assert 0.0 <= ev.emergence_rate < 1.0

    def test_emergence_events_lagrangians_finite(self) -> None:
        cfg = GenesisConfig(max_cycles=20, seed=23)
        g = GenesisOS(config=cfg, emergence_threshold=0.0)
        state = g.run()
        for ev in state.emergence_events:
            assert math.isfinite(ev.lagrangian)

    def test_emergence_events_cycle_monotone(self) -> None:
        cfg = GenesisConfig(max_cycles=30, seed=24)
        g = GenesisOS(config=cfg, emergence_threshold=0.0)
        state = g.run()
        cycles = [ev.cycle for ev in state.emergence_events]
        assert cycles == sorted(cycles)

    def test_emergence_events_crep_in_unit_interval(self) -> None:
        cfg = GenesisConfig(max_cycles=20, seed=25)
        g = GenesisOS(config=cfg, emergence_threshold=0.0)
        state = g.run()
        for ev in state.emergence_events:
            assert 0.0 <= ev.crep.coherence <= 1.0
            assert 0.0 <= ev.crep.resonance <= 1.0
            assert 0.0 <= ev.crep.emergence <= 1.0
            assert 0.0 <= ev.crep.poetics <= 1.0

    def test_metadata_emergence_summary_present(self) -> None:
        cfg = GenesisConfig(max_cycles=10, seed=26)
        g = GenesisOS(config=cfg)
        state = g.run()
        assert "emergence_summary" in state.metadata

    def test_simulator_accessible(self) -> None:
        g = GenesisOS()
        assert isinstance(g.simulator, CosmicWebSimulator)

    def test_reset_clears_emergence_events(self) -> None:
        cfg = GenesisConfig(max_cycles=10, seed=27)
        g = GenesisOS(config=cfg, emergence_threshold=0.0)
        g.run()
        g.reset()
        assert g.state.emergence_events == []
        assert g.simulator.event_count == 0

    def test_rerun_after_reset_consistent(self) -> None:
        cfg = GenesisConfig(max_cycles=5, seed=28)
        g = GenesisOS(config=cfg, emergence_threshold=0.0)
        s1 = g.run()
        g.reset()
        s2 = g.run()
        assert s1.cycle == s2.cycle

    def test_step_adds_emergence_to_state(self) -> None:
        cfg = GenesisConfig(seed=29)
        g = GenesisOS(config=cfg, emergence_threshold=0.0)
        state = g.step()
        # After one step with threshold=0, events may or may not be emitted
        # (rate depends on CREP values), but state must have the field
        assert hasattr(state, "emergence_events")

    def test_generator_yields_states_with_emergence(self) -> None:
        cfg = GenesisConfig(max_cycles=5, seed=30)
        g = GenesisOS(config=cfg)
        for state in g.phase_transition_loop():
            assert hasattr(state, "emergence_events")

    def test_emergence_event_to_dict_serialisable(self) -> None:
        cfg = GenesisConfig(max_cycles=20, seed=31)
        g = GenesisOS(config=cfg, emergence_threshold=0.0)
        state = g.run()
        for ev in state.emergence_events:
            d = ev.to_dict()
            assert isinstance(d, dict)
            serialised = json.dumps(d)
            back = json.loads(serialised)
            assert back["node_count"] == d["node_count"]


# ---------------------------------------------------------------------------
# GUI snapshot integration (no live server)
# ---------------------------------------------------------------------------


class TestGUISnapshotIntegration:
    def test_gui_snapshot_from_state(self) -> None:
        cfg = GenesisConfig(max_cycles=5, seed=40)
        g = GenesisOS(config=cfg)
        state = g.run()
        esummary = state.metadata.get("emergence_summary", {})
        snap = GUISnapshot(
            cycle=state.cycle,
            phase=state.phase.value,
            entropy=state.entropy,
            phi=state.phi,
            lagrangian=state.lagrangian,
            gamma=state.crep.gamma if state.crep else 0.0,
            coherence=state.crep.coherence if state.crep else 0.5,
            resonance=state.crep.resonance if state.crep else 0.5,
            emergence=state.crep.emergence if state.crep else 0.5,
            poetics=state.crep.poetics if state.crep else 0.5,
            mean_density=float(esummary.get("mean_density", 0.0)),
            active_nodes=int(esummary.get("active_nodes", 0)),
            emergence_events=len(state.emergence_events),
            phase_transition=False,
        )
        assert snap.cycle == state.cycle
        assert snap.phase == state.phase.value
        assert 0.0 <= snap.entropy <= 1.0

    def test_push_multiple_snapshots_to_gui(self) -> None:
        cfg = GenesisConfig(max_cycles=5, seed=41)
        g = GenesisOS(config=cfg)
        gui = GenesisWebGUI(interval_ms=200, history_len=10)

        for state in g.phase_transition_loop():
            esummary = state.metadata.get("emergence_summary", {})
            snap = GUISnapshot(
                cycle=state.cycle,
                phase=state.phase.value,
                entropy=state.entropy,
                phi=state.phi,
                lagrangian=state.lagrangian,
                gamma=state.crep.gamma if state.crep else 0.0,
                mean_density=float(esummary.get("mean_density", 0.0)),
                active_nodes=int(esummary.get("active_nodes", 0)),
                emergence_events=len(state.emergence_events),
            )
            gui.push_snapshot(snap)

        gui._drain_queue()
        assert len(gui._history) == 5

    def test_gui_history_entropy_in_bounds(self) -> None:
        cfg = GenesisConfig(max_cycles=10, seed=42)
        g = GenesisOS(config=cfg)
        gui = GenesisWebGUI(history_len=20)

        for state in g.phase_transition_loop():
            gui.push_snapshot(GUISnapshot(cycle=state.cycle, entropy=state.entropy))

        gui._drain_queue()
        for snap in gui._history:
            assert 0.0 <= snap.entropy <= 1.0

    def test_gui_build_app_does_not_crash(self) -> None:
        gui = GenesisWebGUI()
        result = gui.build_app()
        # No exception regardless of Dash availability
        assert result is None or hasattr(result, "layout")

    def test_gui_crep_radar_with_full_history(self) -> None:
        cfg = GenesisConfig(max_cycles=10, seed=43)
        g = GenesisOS(config=cfg)
        gui = GenesisWebGUI(history_len=20)

        for state in g.phase_transition_loop():
            gui.push_snapshot(GUISnapshot(
                cycle=state.cycle,
                coherence=state.crep.coherence if state.crep else 0.5,
                resonance=state.crep.resonance if state.crep else 0.5,
                emergence=state.crep.emergence if state.crep else 0.5,
                poetics=state.crep.poetics if state.crep else 0.5,
                gamma=state.crep.gamma if state.crep else 0.0,
            ))

        gui._drain_queue()
        last = gui._history[-1]
        fig = gui._crep_radar_figure(last)
        assert fig is not None

    def test_gui_emergence_chart_with_history(self) -> None:
        gui = GenesisWebGUI(history_len=20)
        for i in range(5):
            gui.push_snapshot(GUISnapshot(cycle=i, emergence_events=i, mean_density=0.1 * i))
        gui._drain_queue()
        fig = gui._emergence_figure(gui._history)
        assert fig is not None


# ---------------------------------------------------------------------------
# CLI with --gui flag (no live server – just tests the non-blocking path)
# ---------------------------------------------------------------------------


class TestCLIGUIFlag:
    def test_cycle_gui_flag_accepted(self) -> None:
        """--gui flag must be accepted without crashing (Dash may not start)."""
        result = runner.invoke(
            app,
            ["cycle", "--max-cycles", "3", "--seed", "50", "--gui"],
        )
        # Exit code may be 0 whether or not Dash is installed
        assert result.exit_code == 0

    def test_cycle_gui_simulate_together(self) -> None:
        """--gui and --simulate can coexist; simulate takes priority."""
        result = runner.invoke(
            app,
            ["cycle", "--simulate", "--gui", "--max-cycles", "5", "--seed", "51"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "emergence_events" in data

    def test_cycle_gui_port_option_accepted(self) -> None:
        result = runner.invoke(
            app,
            ["cycle", "--max-cycles", "3", "--seed", "52", "--gui", "--gui-port", "8051"],
        )
        assert result.exit_code == 0

    def test_cycle_gui_host_option_accepted(self) -> None:
        result = runner.invoke(
            app,
            ["cycle", "--max-cycles", "3", "--seed", "53", "--gui", "--gui-host", "127.0.0.1"],
        )
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Contract: CosmicWebSimulator as public API
# ---------------------------------------------------------------------------


class TestCosmicWebSimulatorPublicAPI:
    def test_importable_from_genesis_os(self) -> None:
        from genesis_os import CosmicWebSimulator

        assert CosmicWebSimulator is not None

    def test_in_all(self) -> None:
        import genesis_os

        assert "CosmicWebSimulator" in genesis_os.__all__

    def test_default_construction(self) -> None:
        s = CosmicWebSimulator()
        assert s.n_nodes == 64

    def test_emergence_rate_method_exists(self) -> None:
        s = CosmicWebSimulator()
        from genesis_os.core.crep import CREPScore

        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        rate = s.emergence_rate(lagrangian=1.0, gamma=crep.gamma)
        assert 0.0 <= rate < 1.0

    def test_step_method_exists(self) -> None:
        s = CosmicWebSimulator()
        from genesis_os.core.crep import CREPScore

        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        result = s.step(crep=crep, lagrangian=1.0)
        assert result is None or isinstance(result, EmergenceEvent)

    def test_summary_method_exists(self) -> None:
        s = CosmicWebSimulator()
        summary = s.summary()
        assert isinstance(summary, dict)

    def test_reset_method_exists(self) -> None:
        s = CosmicWebSimulator()
        s.reset()
        assert s.event_count == 0


# ---------------------------------------------------------------------------
# Contract: cosmic-web adapter with emergence
# ---------------------------------------------------------------------------


class TestCosmicWebAdapterContract:
    def test_adapter_importable(self) -> None:
        import genesis_os.plugins.adapters.cosmic_web as cw

        assert hasattr(cw, "plugin_fn")

    def test_adapter_plugin_fn_callable(self) -> None:
        import genesis_os.plugins.adapters.cosmic_web as cw

        assert callable(cw.plugin_fn)

    def test_adapter_returns_dict(self) -> None:
        import genesis_os.plugins.adapters.cosmic_web as cw
        from genesis_os.core.crep import CREPScore

        state = GenesisState()
        state.crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        result = cw.plugin_fn(state)
        assert isinstance(result, dict)

    def test_adapter_available_key_bool(self) -> None:
        import genesis_os.plugins.adapters.cosmic_web as cw

        state = GenesisState()
        result = cw.plugin_fn(state)
        avail_keys = [k for k in result if k.endswith("_available")]
        for k in avail_keys:
            assert isinstance(result[k], bool)

    def test_adapter_no_raise_empty_state(self) -> None:
        import genesis_os.plugins.adapters.cosmic_web as cw

        state = GenesisState()
        try:
            cw.plugin_fn(state)
        except Exception as exc:
            pytest.fail(f"cosmic_web.plugin_fn raised: {exc!r}")

    def test_fieldtheory_adapter_importable(self) -> None:
        import genesis_os.plugins.adapters.fieldtheory as ft

        assert hasattr(ft, "plugin_fn")

    def test_fieldtheory_adapter_returns_dict(self) -> None:
        import genesis_os.plugins.adapters.fieldtheory as ft

        state = GenesisState()
        state.phi = 1.2
        result = ft.plugin_fn(state)
        assert isinstance(result, dict)

    def test_fieldtheory_available_key(self) -> None:
        import genesis_os.plugins.adapters.fieldtheory as ft

        state = GenesisState()
        result = ft.plugin_fn(state)
        assert any(k.endswith("_available") for k in result)
