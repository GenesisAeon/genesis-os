"""Unit tests for genesis_os.dashboard.tension_metric and web_gui v2 additions."""

from __future__ import annotations

from pathlib import Path

import pytest

from genesis_os.dashboard.tension_metric import TensionMetric
from genesis_os.dashboard.web_gui import GUISnapshot, GenesisWebGUI
from genesis_os.live_data.era5_stream import ERA5Stream
from genesis_os.live_data.phase_alarm import AlarmLevel


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------


def _make_stream(tmp_path: Path) -> ERA5Stream:
    """Build a small ERA5Stream from a temp CSV."""
    csv = tmp_path / "era5_tension_test.csv"
    csv.write_text(
        "year,temp_anomaly,ice_volume\n"
        + "\n".join(f"{y},-{(y-1990)*0.1:.2f},{30.0-(y-1990)*0.5:.2f}" for y in range(1990, 2020))
        + "\n"
    )
    return ERA5Stream(data_path=csv, window=10)


@pytest.fixture
def stream(tmp_path: Path) -> ERA5Stream:
    return _make_stream(tmp_path)


@pytest.fixture
def tension(stream: ERA5Stream) -> TensionMetric:
    return TensionMetric(stream=stream, history_len=50)


@pytest.fixture
def tension_loaded(stream: ERA5Stream) -> TensionMetric:
    tm = TensionMetric(stream=stream, history_len=50)
    tm.load()
    return tm


# ---------------------------------------------------------------------------
# TensionMetric
# ---------------------------------------------------------------------------


class TestTensionMetric:
    def test_default_stream_created(self) -> None:
        tm = TensionMetric()
        assert tm.stream is not None

    def test_load_returns_list(self, tension: TensionMetric) -> None:
        alarms = tension.load()
        assert isinstance(alarms, list)

    def test_load_populates_history(self, tension_loaded: TensionMetric) -> None:
        assert len(tension_loaded.tension_series()) > 0

    def test_latest_tension_before_load(self, tension: TensionMetric) -> None:
        assert tension.latest_tension() == 0.0

    def test_latest_tension_after_load(self, tension_loaded: TensionMetric) -> None:
        assert tension_loaded.latest_tension() >= 0.0

    def test_latest_alarm_level_before_load(self, tension: TensionMetric) -> None:
        level = tension.latest_alarm_level()
        assert isinstance(level, AlarmLevel)

    def test_latest_alarm_level_after_load(self, tension_loaded: TensionMetric) -> None:
        level = tension_loaded.latest_alarm_level()
        assert isinstance(level, AlarmLevel)

    def test_year_series_length(self, tension_loaded: TensionMetric) -> None:
        assert len(tension_loaded.year_series()) == len(tension_loaded.tension_series())

    def test_variance_ratio_series_non_negative(self, tension_loaded: TensionMetric) -> None:
        for vr in tension_loaded.variance_ratio_series():
            assert vr >= 0.0

    def test_ar1_series_in_range(self, tension_loaded: TensionMetric) -> None:
        for ar1 in tension_loaded.ar1_series():
            assert -1.0 - 1e-9 <= ar1 <= 1.0 + 1e-9

    def test_peak_tension_gte_latest(self, tension_loaded: TensionMetric) -> None:
        assert tension_loaded.peak_tension() >= tension_loaded.latest_tension()

    def test_mean_tension_non_negative(self, tension_loaded: TensionMetric) -> None:
        assert tension_loaded.mean_tension() >= 0.0

    def test_peak_tension_empty(self, tension: TensionMetric) -> None:
        assert tension.peak_tension() == 0.0

    def test_mean_tension_empty(self, tension: TensionMetric) -> None:
        assert tension.mean_tension() == 0.0

    def test_summary_keys(self, tension_loaded: TensionMetric) -> None:
        s = tension_loaded.summary()
        for key in ("n_records", "latest_tension", "peak_tension", "mean_tension", "alarm_level", "total_alarms"):
            assert key in s

    def test_update_gamma_changes_tension(self, tension_loaded: TensionMetric) -> None:
        t0 = tension_loaded.latest_tension()
        tension_loaded.update_gamma(2.0)
        t1 = tension_loaded.latest_tension()
        assert t1 >= t0

    def test_load_is_idempotent(self, tension: TensionMetric) -> None:
        tension.load()
        count1 = len(tension.tension_series())
        tension.load()
        count2 = len(tension.tension_series())
        assert count1 == count2

    def test_history_len_respected(self, stream: ERA5Stream) -> None:
        tm = TensionMetric(stream=stream, history_len=5)
        tm.load()
        assert len(tm.tension_series()) <= 5

    def test_alarm_level_string_in_summary(self, tension_loaded: TensionMetric) -> None:
        s = tension_loaded.summary()
        assert s["alarm_level"] in {"NOMINAL", "ELEVATED", "WARNING", "CRITICAL"}


# ---------------------------------------------------------------------------
# GUISnapshot v2 — new fields
# ---------------------------------------------------------------------------


class TestGUISnapshotV2:
    def test_default_tension(self) -> None:
        snap = GUISnapshot()
        assert snap.tension == 0.0

    def test_default_alarm_level(self) -> None:
        snap = GUISnapshot()
        assert snap.alarm_level == "NOMINAL"

    def test_default_variance_ratio(self) -> None:
        snap = GUISnapshot()
        assert snap.variance_ratio == 0.0

    def test_default_ar1(self) -> None:
        snap = GUISnapshot()
        assert snap.ar1 == 0.0

    def test_set_tension(self) -> None:
        snap = GUISnapshot(tension=1.5, alarm_level="WARNING", variance_ratio=1.2, ar1=0.7)
        assert snap.tension == pytest.approx(1.5)
        assert snap.alarm_level == "WARNING"
        assert snap.variance_ratio == pytest.approx(1.2)
        assert snap.ar1 == pytest.approx(0.7)


# ---------------------------------------------------------------------------
# GenesisWebGUI._alarm_color static method
# ---------------------------------------------------------------------------


class TestAlarmColor:
    def test_nominal_color(self) -> None:
        color = GenesisWebGUI._alarm_color("NOMINAL")
        assert color.startswith("#")

    def test_elevated_color(self) -> None:
        assert GenesisWebGUI._alarm_color("ELEVATED") != GenesisWebGUI._alarm_color("NOMINAL")

    def test_warning_color(self) -> None:
        assert GenesisWebGUI._alarm_color("WARNING") != GenesisWebGUI._alarm_color("NOMINAL")

    def test_critical_color(self) -> None:
        assert GenesisWebGUI._alarm_color("CRITICAL") != GenesisWebGUI._alarm_color("WARNING")

    def test_unknown_level_fallback(self) -> None:
        color = GenesisWebGUI._alarm_color("UNKNOWN")
        assert color == "#aaa"

    def test_all_known_levels(self) -> None:
        for level in ("NOMINAL", "ELEVATED", "WARNING", "CRITICAL"):
            color = GenesisWebGUI._alarm_color(level)
            assert len(color) == 7
            assert color.startswith("#")


# ---------------------------------------------------------------------------
# GenesisWebGUI._status_cards includes tension cards (when Dash not available)
# ---------------------------------------------------------------------------


class TestWebGUIStatusCards:
    def test_status_cards_returns_list(self) -> None:
        gui = GenesisWebGUI()
        snap = GUISnapshot(tension=1.2, alarm_level="WARNING")
        cards = gui._status_cards(snap)
        assert isinstance(cards, list)

    def test_status_cards_include_tension_and_alarm(self) -> None:
        gui = GenesisWebGUI()
        snap = GUISnapshot(tension=1.5, alarm_level="WARNING", ar1=0.6)
        cards = gui._status_cards(snap)
        assert len(cards) > 0


class TestTensionFigure:
    def test_tension_figure_empty_history(self) -> None:
        gui = GenesisWebGUI()
        result = gui._tension_figure([])
        assert result is not None

    def test_tension_figure_single_snapshot(self) -> None:
        gui = GenesisWebGUI()
        snap = GUISnapshot(cycle=0, tension=0.5, variance_ratio=0.8, ar1=0.6)
        result = gui._tension_figure([snap])
        assert result is not None

    def test_tension_figure_multiple_snapshots(self) -> None:
        gui = GenesisWebGUI()
        history = [
            GUISnapshot(cycle=i, tension=0.3 + i * 0.1, variance_ratio=0.5 + i * 0.05, ar1=0.4 + i * 0.02)
            for i in range(10)
        ]
        result = gui._tension_figure(history)
        assert result is not None

    def test_tension_figure_with_high_tension(self) -> None:
        gui = GenesisWebGUI()
        history = [GUISnapshot(cycle=i, tension=2.0 + i * 0.1, alarm_level="CRITICAL") for i in range(5)]
        result = gui._tension_figure(history)
        assert result is not None
