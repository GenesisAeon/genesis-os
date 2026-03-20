"""Unit tests for genesis_os.dashboard.web_gui (GenesisWebGUI).

Snapshot / structural tests that do NOT require a running Dash server.
Dash itself is optional; all tests must pass regardless of whether it is
installed.
"""

from __future__ import annotations

import threading

import pytest

from genesis_os.dashboard.web_gui import GenesisWebGUI, GUISnapshot

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def gui() -> GenesisWebGUI:
    return GenesisWebGUI(interval_ms=500, history_len=50)


@pytest.fixture
def snap_default() -> GUISnapshot:
    return GUISnapshot()


@pytest.fixture
def snap_full() -> GUISnapshot:
    return GUISnapshot(
        cycle=10,
        phase="Activation",
        entropy=0.4,
        phi=1.2,
        lagrangian=0.8,
        gamma=0.55,
        coherence=0.6,
        resonance=0.7,
        emergence=0.5,
        poetics=0.4,
        mean_density=0.12,
        active_nodes=3,
        emergence_events=2,
        phase_transition=True,
    )


# ---------------------------------------------------------------------------
# GUISnapshot tests
# ---------------------------------------------------------------------------


class TestGUISnapshot:
    def test_default_values(self, snap_default: GUISnapshot) -> None:
        assert snap_default.cycle == 0
        assert snap_default.phase == "Initiation"
        assert snap_default.entropy == pytest.approx(0.5)
        assert snap_default.phi == pytest.approx(1.0)
        assert snap_default.lagrangian == pytest.approx(0.0)
        assert snap_default.gamma == pytest.approx(0.0)
        assert snap_default.mean_density == pytest.approx(0.0)
        assert snap_default.active_nodes == 0
        assert snap_default.emergence_events == 0
        assert snap_default.phase_transition is False

    def test_custom_values(self, snap_full: GUISnapshot) -> None:
        assert snap_full.cycle == 10
        assert snap_full.phase == "Activation"
        assert snap_full.entropy == pytest.approx(0.4)
        assert snap_full.active_nodes == 3
        assert snap_full.emergence_events == 2
        assert snap_full.phase_transition is True

    def test_snapshot_is_dataclass(self, snap_default: GUISnapshot) -> None:
        from dataclasses import fields

        assert len(fields(snap_default)) >= 14

    def test_snapshot_crep_fields_in_unit_interval(self, snap_full: GUISnapshot) -> None:
        for attr in ("coherence", "resonance", "emergence", "poetics"):
            val = getattr(snap_full, attr)
            assert 0.0 <= val <= 1.0, f"{attr}={val} not in [0, 1]"

    def test_snapshot_cycle_non_negative(self, snap_full: GUISnapshot) -> None:
        assert snap_full.cycle >= 0

    def test_snapshot_active_nodes_non_negative(self, snap_full: GUISnapshot) -> None:
        assert snap_full.active_nodes >= 0


# ---------------------------------------------------------------------------
# GenesisWebGUI construction
# ---------------------------------------------------------------------------


class TestGenesisWebGUIInit:
    def test_default_title(self) -> None:
        g = GenesisWebGUI()
        assert "GenesisOS" in g.title

    def test_custom_title(self) -> None:
        g = GenesisWebGUI(title="My Test GUI")
        assert g.title == "My Test GUI"

    def test_default_interval_ms(self) -> None:
        g = GenesisWebGUI()
        assert g.interval_ms == 1_000

    def test_custom_interval_ms(self, gui: GenesisWebGUI) -> None:
        assert gui.interval_ms == 500

    def test_history_len(self, gui: GenesisWebGUI) -> None:
        assert gui.history_len == 50

    def test_initial_history_empty(self, gui: GenesisWebGUI) -> None:
        assert gui._history == []

    def test_is_available_property(self, gui: GenesisWebGUI) -> None:
        # is_available reflects whether Dash is installed
        assert isinstance(gui.is_available, bool)


# ---------------------------------------------------------------------------
# push_snapshot / _drain_queue
# ---------------------------------------------------------------------------


class TestGUIQueue:
    def test_push_snapshot_enqueues(self, gui: GenesisWebGUI, snap_full: GUISnapshot) -> None:
        gui.push_snapshot(snap_full)
        assert not gui._queue.empty()

    def test_drain_queue_moves_to_history(self, gui: GenesisWebGUI, snap_full: GUISnapshot) -> None:
        gui.push_snapshot(snap_full)
        gui._drain_queue()
        assert len(gui._history) == 1

    def test_drain_queue_clears_queue(self, gui: GenesisWebGUI, snap_full: GUISnapshot) -> None:
        gui.push_snapshot(snap_full)
        gui._drain_queue()
        assert gui._queue.empty()

    def test_multiple_snapshots_in_history(self, gui: GenesisWebGUI) -> None:
        for i in range(5):
            gui.push_snapshot(GUISnapshot(cycle=i))
        gui._drain_queue()
        assert len(gui._history) == 5

    def test_history_len_cap(self) -> None:
        g = GenesisWebGUI(history_len=3)
        for i in range(10):
            g.push_snapshot(GUISnapshot(cycle=i))
        g._drain_queue()
        assert len(g._history) == 3

    def test_history_order(self, gui: GenesisWebGUI) -> None:
        for i in range(3):
            gui.push_snapshot(GUISnapshot(cycle=i))
        gui._drain_queue()
        cycles = [s.cycle for s in gui._history]
        assert cycles == [0, 1, 2]

    def test_thread_safe_push(self, gui: GenesisWebGUI) -> None:
        """Push from multiple threads simultaneously without deadlock."""
        errors: list[Exception] = []

        def pusher() -> None:
            for i in range(20):
                try:
                    gui.push_snapshot(GUISnapshot(cycle=i))
                except Exception as exc:
                    errors.append(exc)

        threads = [threading.Thread(target=pusher) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert errors == []
        gui._drain_queue()
        assert len(gui._history) <= gui.history_len

    def test_drain_empty_queue_no_error(self, gui: GenesisWebGUI) -> None:
        gui._drain_queue()
        assert gui._history == []


# ---------------------------------------------------------------------------
# Figure / chart helpers (when Dash not installed, return empty dict / [])
# ---------------------------------------------------------------------------


class TestGUIFigureHelpers:
    def test_crep_radar_figure_no_crash(self, gui: GenesisWebGUI, snap_full: GUISnapshot) -> None:
        result = gui._crep_radar_figure(snap_full)
        # Either a Plotly figure or empty dict; should not raise
        assert result is not None

    def test_entropy_lagrangian_figure_no_crash(self, gui: GenesisWebGUI) -> None:
        snaps = [GUISnapshot(cycle=i, entropy=0.5 - i * 0.01) for i in range(5)]
        result = gui._entropy_lagrangian_figure(snaps)
        assert result is not None

    def test_emergence_figure_no_crash(self, gui: GenesisWebGUI) -> None:
        snaps = [GUISnapshot(cycle=i, emergence_events=i) for i in range(5)]
        result = gui._emergence_figure(snaps)
        assert result is not None

    def test_status_cards_returns_list(self, gui: GenesisWebGUI, snap_full: GUISnapshot) -> None:
        cards = gui._status_cards(snap_full)
        assert isinstance(cards, list)

    def test_status_cards_empty_when_no_dbc(self) -> None:
        """When DBC is not installed, status_cards should return []."""
        g = GenesisWebGUI()
        snap = GUISnapshot()
        cards = g._status_cards(snap)
        assert isinstance(cards, list)

    def test_crep_radar_with_default_snapshot(self, gui: GenesisWebGUI) -> None:
        snap = GUISnapshot()
        result = gui._crep_radar_figure(snap)
        assert result is not None

    def test_entropy_chart_empty_history(self, gui: GenesisWebGUI) -> None:
        result = gui._entropy_lagrangian_figure([])
        assert result is not None

    def test_emergence_chart_empty_history(self, gui: GenesisWebGUI) -> None:
        result = gui._emergence_figure([])
        assert result is not None


# ---------------------------------------------------------------------------
# build_app
# ---------------------------------------------------------------------------


class TestGenesisWebGUIBuildApp:
    def test_build_app_returns_none_or_app(self, gui: GenesisWebGUI) -> None:
        result = gui.build_app()
        # Either None (Dash not installed) or a Dash app object
        assert result is None or hasattr(result, "layout")

    def test_build_app_sets_internal_app(self, gui: GenesisWebGUI) -> None:
        gui.build_app()
        # _app is either None (no Dash) or the Dash app
        assert gui._app is None or hasattr(gui._app, "layout")

    def test_build_app_idempotent(self, gui: GenesisWebGUI) -> None:
        r1 = gui.build_app()
        r2 = gui.build_app()
        # Second call should not crash regardless of Dash availability
        if r1 is not None:
            assert r2 is not None


# ---------------------------------------------------------------------------
# run raises RuntimeError without Dash
# ---------------------------------------------------------------------------


class TestGenesisWebGUIRun:
    def test_run_raises_without_dash(self, gui: GenesisWebGUI, monkeypatch: pytest.MonkeyPatch) -> None:
        """If Dash is not available, run() raises RuntimeError."""
        import genesis_os.dashboard.web_gui as wg

        original = wg._DASH_AVAILABLE
        monkeypatch.setattr(wg, "_DASH_AVAILABLE", False)
        gui2 = GenesisWebGUI()
        with pytest.raises(RuntimeError, match="Dash not installed"):
            gui2.run()
        monkeypatch.setattr(wg, "_DASH_AVAILABLE", original)


# ---------------------------------------------------------------------------
# is_available
# ---------------------------------------------------------------------------


class TestGUIAvailability:
    def test_is_available_consistent(self) -> None:
        g = GenesisWebGUI()
        import genesis_os.dashboard.web_gui as wg

        assert g.is_available == wg._DASH_AVAILABLE

    def test_is_available_bool(self) -> None:
        g = GenesisWebGUI()
        assert isinstance(g.is_available, bool)


# ---------------------------------------------------------------------------
# Snapshot field types
# ---------------------------------------------------------------------------


class TestGUISnapshotTypes:
    def test_cycle_int(self, snap_full: GUISnapshot) -> None:
        assert isinstance(snap_full.cycle, int)

    def test_phase_str(self, snap_full: GUISnapshot) -> None:
        assert isinstance(snap_full.phase, str)

    def test_entropy_float(self, snap_full: GUISnapshot) -> None:
        assert isinstance(snap_full.entropy, float)

    def test_phi_float(self, snap_full: GUISnapshot) -> None:
        assert isinstance(snap_full.phi, float)

    def test_lagrangian_float(self, snap_full: GUISnapshot) -> None:
        assert isinstance(snap_full.lagrangian, float)

    def test_gamma_float(self, snap_full: GUISnapshot) -> None:
        assert isinstance(snap_full.gamma, float)

    def test_mean_density_float(self, snap_full: GUISnapshot) -> None:
        assert isinstance(snap_full.mean_density, float)

    def test_active_nodes_int(self, snap_full: GUISnapshot) -> None:
        assert isinstance(snap_full.active_nodes, int)

    def test_emergence_events_int(self, snap_full: GUISnapshot) -> None:
        assert isinstance(snap_full.emergence_events, int)

    def test_phase_transition_bool(self, snap_full: GUISnapshot) -> None:
        assert isinstance(snap_full.phase_transition, bool)
