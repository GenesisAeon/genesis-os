"""Tests targeting specific uncovered code paths to meet the 99% coverage goal.

Covers:
- CREPEvaluator.weighted_average with zero weights
- MandalaDashboard plugin init (use_plugin=True without package)
- MandalaDashboard.plugin_render with mocked plugin
- Sonifier plugin init (use_plugin=True without package)
- Sonifier.play with mocked plugin
- CLI _run_visualize and _run_sonify paths
- PluginRegistry.discover auto path and ImportError in _load
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from genesis_os.cli.main import _push_gui_snapshot, _run_sonify, _run_visualize, _start_gui, app
from genesis_os.core.crep import CREPEvaluator, CREPScore
from genesis_os.core.orchestrator import GenesisState
from genesis_os.core.phase import Phase
from genesis_os.dashboard.mandala import MandalaDashboard
from genesis_os.dashboard.sonification import Sonifier

runner = CliRunner()


# ──────────────────────────────────────────────────────────────────────────────
# CREPEvaluator.weighted_average — zero weight sum
# ──────────────────────────────────────────────────────────────────────────────


class TestCREPWeightedAverageZeroWeights:
    def test_zero_weights_returns_zero(self) -> None:
        ev = CREPEvaluator()
        ev.evaluate({"coherence": 0.5, "resonance": 0.5, "emergence": 0.5, "poetics": 0.5})
        result = ev.weighted_average(weights=(0.0, 0.0, 0.0, 0.0))
        assert result == pytest.approx(0.0)


# ──────────────────────────────────────────────────────────────────────────────
# MandalaDashboard — plugin init and plugin_render
# ──────────────────────────────────────────────────────────────────────────────


class TestMandalaDashboardPlugin:
    @pytest.fixture
    def crep(self) -> CREPScore:
        return CREPScore(coherence=0.7, resonance=0.6, emergence=0.5, poetics=0.8)

    def test_use_plugin_true_without_package_sets_plugin_none(self) -> None:
        """use_plugin=True + package absent → _plugin is None (covers the except branch)."""
        dashboard = MandalaDashboard(use_plugin=True)
        assert dashboard._plugin is None

    def test_plugin_render_with_mock_plugin_success(self, crep: CREPScore) -> None:
        """plugin_render with a working mocked _plugin covers lines 134-135."""
        dashboard = MandalaDashboard(use_plugin=False)
        mock_plugin = MagicMock()
        mock_plugin.render.return_value = "plugin_output"
        dashboard._plugin = mock_plugin
        result = dashboard.plugin_render(crep)
        assert result == "plugin_output"
        mock_plugin.render.assert_called_once()

    def test_plugin_render_with_mock_plugin_exception_fallback(self, crep: CREPScore) -> None:
        """plugin_render exception path → fallback to ASCII (covers lines 136-137)."""
        dashboard = MandalaDashboard(use_plugin=False)
        mock_plugin = MagicMock()
        mock_plugin.render.side_effect = RuntimeError("render error")
        dashboard._plugin = mock_plugin
        result = dashboard.plugin_render(crep)
        assert isinstance(result, str)

    def test_plugin_render_no_plugin_falls_back(self, crep: CREPScore) -> None:
        dashboard = MandalaDashboard(use_plugin=False)
        assert dashboard._plugin is None
        result = dashboard.plugin_render(crep)
        assert isinstance(result, str)


# ──────────────────────────────────────────────────────────────────────────────
# Sonifier — plugin init and play
# ──────────────────────────────────────────────────────────────────────────────


class TestSonifierPlugin:
    @pytest.fixture
    def crep(self) -> CREPScore:
        return CREPScore(coherence=0.7, resonance=0.6, emergence=0.5, poetics=0.8)

    def test_use_plugin_true_without_package_sets_plugin_none(self) -> None:
        """use_plugin=True + package absent → _plugin is None."""
        sonifier = Sonifier(use_plugin=True)
        assert sonifier._plugin is None

    def test_play_with_mock_plugin_success(self, crep: CREPScore) -> None:
        """play with a working mocked _plugin returns True (covers lines 114-116)."""
        sonifier = Sonifier(use_plugin=False)
        mock_plugin = MagicMock()
        sonifier._plugin = mock_plugin
        frame = sonifier.crep_to_frequencies(crep)
        result = sonifier.play(frame)
        assert result is True

    def test_play_with_mock_plugin_exception_returns_false(self, crep: CREPScore) -> None:
        """play exception path → returns False (covers lines 117-118)."""
        sonifier = Sonifier(use_plugin=False)
        mock_plugin = MagicMock()
        mock_plugin.play.side_effect = RuntimeError("play failed")
        sonifier._plugin = mock_plugin
        frame = sonifier.crep_to_frequencies(crep)
        result = sonifier.play(frame)
        assert result is False


# ──────────────────────────────────────────────────────────────────────────────
# CLI — _run_visualize and _run_sonify helper functions
# ──────────────────────────────────────────────────────────────────────────────


class TestCLIHelpers:
    @pytest.fixture
    def state_with_crep(self) -> GenesisState:
        state = GenesisState()
        state.crep = CREPScore(coherence=0.7, resonance=0.6, emergence=0.5, poetics=0.8)
        state.phase = Phase.INITIATION
        return state

    def test_run_visualize_with_state_and_crep(self, state_with_crep: GenesisState) -> None:
        """_run_visualize with state that has crep covers lines 142-144."""
        _run_visualize(state_with_crep)  # should not raise

    def test_run_visualize_with_none_state(self) -> None:
        """_run_visualize with None state does not raise."""
        _run_visualize(None)

    def test_run_visualize_state_no_crep(self) -> None:
        """_run_visualize with state but no crep covers the else branch."""
        state = GenesisState()
        _run_visualize(state)

    def test_run_sonify_with_crep(self, state_with_crep: GenesisState) -> None:
        """_run_sonify with state that has crep covers lines 158-160."""
        _run_sonify(state_with_crep)  # should not raise

    def test_run_sonify_no_crep(self) -> None:
        """_run_sonify with state but no crep."""
        state = GenesisState()
        _run_sonify(state)


# ──────────────────────────────────────────────────────────────────────────────
# CLI cycle — phases flag with transitions
# ──────────────────────────────────────────────────────────────────────────────


class TestCLICyclePhaseTransitions:
    def test_cycle_phases_with_low_threshold_transitions_logged(self) -> None:
        """Run cycle with --phases on a config that triggers transitions (covers lines 121-122)."""
        result = runner.invoke(
            app,
            ["cycle", "--phases", "--max-cycles", "20", "--seed", "1"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0

    def test_cycle_visualize_flag(self) -> None:
        """--visualize flag runs _run_visualize (covers line 131)."""
        result = runner.invoke(
            app,
            ["cycle", "--visualize", "--max-cycles", "3", "--seed", "1"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0

    def test_cycle_sonify_flag(self) -> None:
        """--sonify flag runs _run_sonify (covers lines 133-134)."""
        result = runner.invoke(
            app,
            ["cycle", "--sonify", "--max-cycles", "3", "--seed", "1"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0


# ──────────────────────────────────────────────────────────────────────────────
# CLI — phases flag logging branches (transitions + emergence events)
# ──────────────────────────────────────────────────────────────────────────────


class TestCLIPhasesLoggingBranches:
    def test_phases_logs_transitions_branch(self) -> None:
        """Cover the state.transitions logging branch inside phase_transition_loop."""
        from genesis_os.core.orchestrator import GenesisOS, GenesisState
        from genesis_os.core.phase import Phase, PhaseTransition

        # Patch GenesisOS.phase_transition_loop to yield a state with transitions
        original_loop = GenesisOS.phase_transition_loop

        def mock_loop(self_inner, max_cycles=None, callback=None):  # type: ignore[no-untyped-def]
            state = GenesisState()
            state.crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
            t = PhaseTransition(
                from_phase=Phase.INITIATION,
                to_phase=Phase.ACTIVATION,
                trigger_gamma=0.8,
                cycle=1,
            )
            state.transitions.append(t)
            state.cycle = 1
            yield state

        from unittest.mock import patch as mock_patch

        with mock_patch.object(GenesisOS, "phase_transition_loop", mock_loop):
            result = runner.invoke(
                app,
                ["cycle", "--phases", "--max-cycles", "1", "--seed", "1"],
                catch_exceptions=False,
            )
        assert result.exit_code == 0

    def test_phases_logs_emergence_events_branch(self) -> None:
        """Cover the state.emergence_events logging branch inside phase_transition_loop."""
        from genesis_os.core.crep import CREPScore
        from genesis_os.core.orchestrator import GenesisOS, GenesisState
        from genesis_os.runtime.emergence import EmergenceEvent

        def mock_loop(self_inner, max_cycles=None, callback=None):  # type: ignore[no-untyped-def]
            state = GenesisState()
            crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
            state.crep = crep
            ev = EmergenceEvent(
                cycle=1,
                node_count=3,
                emergence_rate=0.5,
                lagrangian=1.0,
                gamma=crep.gamma,
                density_delta=0.01,
                crep=crep,
            )
            state.emergence_events.append(ev)
            state.cycle = 1
            yield state

        from unittest.mock import patch as mock_patch

        with mock_patch.object(GenesisOS, "phase_transition_loop", mock_loop):
            result = runner.invoke(
                app,
                ["cycle", "--phases", "--max-cycles", "1", "--seed", "1"],
                catch_exceptions=False,
            )
        assert result.exit_code == 0

    def test_push_gui_snapshot_with_valid_state(self) -> None:
        """Cover _push_gui_snapshot helper with a full state."""
        from genesis_os.dashboard.web_gui import GenesisWebGUI

        state = GenesisState()
        state.crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        state.cycle = 5
        state.entropy = 0.4
        state.phi = 1.1
        state.lagrangian = 0.9
        state.metadata["emergence_summary"] = {
            "mean_density": 0.05,
            "active_nodes": 2,
        }
        gui = GenesisWebGUI()
        _push_gui_snapshot(gui, state)
        gui._drain_queue()
        assert len(gui._history) == 1


# ──────────────────────────────────────────────────────────────────────────────
# Orchestrator — custom engine branch (line 120)
# ──────────────────────────────────────────────────────────────────────────────


class TestOrchestratorCustomEngine:
    def test_custom_engine_injected(self) -> None:
        """Pass a custom engine to GenesisOS to cover line 120 (engine is not None)."""
        from unittest.mock import MagicMock

        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        mock_engine = MagicMock()
        mock_engine.compute.return_value = {
            "lagrangian": 0.5,
            "entropy": 0.4,
            "kinetic": 0.1,
            "potential": 0.1,
            "phi": 1.0,
            "gamma": 0.3,
            "coherence": 0.5,
            "resonance": 0.5,
            "emergence": 0.5,
            "poetics": 0.5,
        }
        g = GenesisOS(config=GenesisConfig(seed=1), engine=mock_engine)
        state = g.step()
        assert state is not None
        mock_engine.compute.assert_called_once()


# ──────────────────────────────────────────────────────────────────────────────
# WebGUI — entropy chart with phase_transition vline (line 207)
# WebGUI — run() when _app is None (line 415)
# ──────────────────────────────────────────────────────────────────────────────


class TestWebGUICoverageGaps:
    def test_entropy_chart_with_phase_transition_vline(self) -> None:
        """Cover the add_vline branch (line 207) by providing a snapshot with phase_transition=True."""
        from genesis_os.dashboard.web_gui import GenesisWebGUI, GUISnapshot

        gui = GenesisWebGUI()
        snaps = [
            GUISnapshot(cycle=0, entropy=0.5, phase_transition=False),
            GUISnapshot(cycle=1, entropy=0.45, phase_transition=True),
            GUISnapshot(cycle=2, entropy=0.42, phase_transition=False),
        ]
        fig = gui._entropy_lagrangian_figure(snaps)
        assert fig is not None

    def test_run_builds_app_when_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Cover the self.build_app() call inside run() when _app is None (line 415)."""
        from unittest.mock import MagicMock
        from unittest.mock import patch as mock_patch

        from genesis_os.dashboard.web_gui import GenesisWebGUI

        gui = GenesisWebGUI()
        assert gui._app is None

        mock_app = MagicMock()
        mock_app.run = MagicMock()

        with mock_patch.object(gui, "build_app", return_value=mock_app) as mock_build:
            # After build_app call, _app would still be None unless set by mock.
            # We simulate build_app setting _app
            def side_effect() -> MagicMock:
                gui._app = mock_app
                return mock_app

            mock_build.side_effect = side_effect
            import contextlib

            with contextlib.suppress(Exception):
                gui.run(host="127.0.0.1", port=19999)
        mock_build.assert_called_once()


# ──────────────────────────────────────────────────────────────────────────────
# PluginRegistry — auto_discover=True covers line 47
# ──────────────────────────────────────────────────────────────────────────────


class TestPluginRegistryAutoDiscover:
    def test_auto_discover_true_calls_discover(self) -> None:
        from genesis_os.plugins.registry import PluginRegistry

        reg = PluginRegistry(auto_discover=True)
        # Line 47 (self.discover()) is now covered
        assert isinstance(reg.active, list)
        assert isinstance(reg.failed, list)

    def test_load_import_error_covers_line_68(self) -> None:
        from genesis_os.plugins.registry import PluginRegistry

        registry = PluginRegistry(auto_discover=False)
        with patch("importlib.import_module", side_effect=ImportError("no such module")):
            result = registry._load("missing_pkg", "no.such.module")

        assert result is False
        assert "missing_pkg" in registry.failed


# ──────────────────────────────────────────────────────────────────────────────
# _start_gui — cover daemon-thread launch path (no real server)
# ──────────────────────────────────────────────────────────────────────────────


class TestStartGUICoverage:
    def test_start_gui_launches_with_mocked_gui(self) -> None:
        """Cover _start_gui main path: GenesisWebGUI created, app built, thread started."""
        mock_gui = MagicMock()
        with patch("genesis_os.dashboard.web_gui.GenesisWebGUI", return_value=mock_gui):
            result = _start_gui("127.0.0.1", 19998)
        assert result is mock_gui
        mock_gui.build_app.assert_called_once()
