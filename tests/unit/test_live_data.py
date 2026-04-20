"""Unit tests for genesis_os.live_data — ERA5 stream, tension metric, phase alarms."""

from __future__ import annotations

from pathlib import Path

import pytest

from genesis_os.live_data.era5_stream import ERA5Stream, TensionReading
from genesis_os.live_data.phase_alarm import AlarmLevel, PhaseAlarm, PhaseAlarmMonitor

# ---------------------------------------------------------------------------
# ERA5Stream
# ---------------------------------------------------------------------------


@pytest.fixture
def stream(tmp_path: Path) -> ERA5Stream:
    csv = tmp_path / "era5_test.csv"
    csv.write_text(
        "year,temp_anomaly,ice_volume\n"
        "2000,-0.5,32.0\n"
        "2001,-0.6,31.0\n"
        "2002,-0.8,30.0\n"
        "2003,-1.0,28.0\n"
        "2004,-1.2,26.0\n"
        "2005,-1.4,24.0\n"
        "2006,-1.6,22.0\n"
        "2007,-1.8,20.0\n"
        "2008,-2.0,18.0\n"
        "2009,-2.2,16.0\n"
        "2010,-2.4,14.0\n"
        "2011,-2.6,12.0\n"
        "2012,-2.8,10.0\n"
        "2013,-3.0,8.0\n"
        "2014,-3.2,6.0\n"
        "2015,-3.4,4.0\n"
    )
    return ERA5Stream(data_path=csv, window=5)


@pytest.fixture
def stream_default() -> ERA5Stream:
    return ERA5Stream(window=15)


class TestERA5Stream:
    def test_loads_records(self, stream: ERA5Stream) -> None:
        assert stream.n_records == 16

    def test_years_property(self, stream: ERA5Stream) -> None:
        assert stream.years[0] == 2000
        assert stream.years[-1] == 2015

    def test_baseline_variance_positive(self, stream: ERA5Stream) -> None:
        assert stream.baseline_variance > 0.0

    def test_stream_yields_correct_count(self, stream: ERA5Stream) -> None:
        readings = list(stream.stream())
        assert len(readings) == 16

    def test_readings_returns_list(self, stream: ERA5Stream) -> None:
        r = stream.readings()
        assert isinstance(r, list)
        assert len(r) == 16

    def test_tension_reading_fields(self, stream: ERA5Stream) -> None:
        r = stream.readings()
        first = r[0]
        assert isinstance(first, TensionReading)
        assert first.year == 2000
        assert first.temp_anomaly == pytest.approx(-0.5)
        assert first.ice_volume == pytest.approx(32.0)
        assert first.tension >= 0.0
        assert isinstance(first.variance_ratio, float)
        assert isinstance(first.ar1, float)

    def test_latest_returns_last_year(self, stream: ERA5Stream) -> None:
        latest = stream.latest()
        assert latest.year == 2015

    def test_gamma_coupling_scales_tension(self, stream: ERA5Stream) -> None:
        r0 = stream.readings(gamma=0.0)
        r1 = stream.readings(gamma=1.0)
        # raw tension is gamma-independent; tension_crep scales with gamma
        t0 = [r.tension_crep for r in r0]
        t1 = [r.tension_crep for r in r1]
        assert any(t1[i] > t0[i] for i in range(len(t0)) if t0[i] > 0)

    def test_raw_tension_independent_of_gamma(self, stream: ERA5Stream) -> None:
        r0 = stream.readings(gamma=0.0)
        r1 = stream.readings(gamma=2.0)
        for a, b in zip(r0, r1, strict=True):
            assert a.tension == pytest.approx(b.tension)

    def test_tension_non_negative(self, stream: ERA5Stream) -> None:
        for r in stream.stream():
            assert r.tension >= 0.0

    def test_variance_ratio_non_negative(self, stream: ERA5Stream) -> None:
        for r in stream.stream():
            assert r.variance_ratio >= 0.0

    def test_ar1_in_range(self, stream: ERA5Stream) -> None:
        for r in stream.stream():
            assert -1.0 <= r.ar1 <= 1.0

    def test_default_data_path(self, stream_default: ERA5Stream) -> None:
        assert stream_default.n_records > 0
        assert stream_default.years[0] == 1940

    def test_empty_file_raises(self, tmp_path: Path) -> None:
        csv = tmp_path / "empty.csv"
        csv.write_text("year,temp_anomaly,ice_volume\n")
        with pytest.raises(ValueError, match="empty"):
            ERA5Stream(data_path=csv)

    def test_stream_with_short_window(self, tmp_path: Path) -> None:
        csv = tmp_path / "short.csv"
        csv.write_text("year,temp_anomaly,ice_volume\n2000,-0.1,10.0\n2001,-0.2,10.0\n")
        s = ERA5Stream(data_path=csv, window=5)
        readings = s.readings()
        assert len(readings) == 2

    def test_ar1_static_zero_variance(self) -> None:
        import numpy as np

        series = np.array([1.0, 1.0, 1.0])
        result = ERA5Stream._ar1(series)
        assert result == 0.0

    def test_ar1_static_short(self) -> None:
        import numpy as np

        assert ERA5Stream._ar1(np.array([1.0])) == 0.0


# ---------------------------------------------------------------------------
# PhaseAlarmMonitor
# ---------------------------------------------------------------------------


@pytest.fixture
def monitor() -> PhaseAlarmMonitor:
    return PhaseAlarmMonitor()


class TestAlarmLevel:
    def test_nominal_not_actionable(self) -> None:
        assert not AlarmLevel.NOMINAL.is_actionable

    def test_elevated_not_actionable(self) -> None:
        assert not AlarmLevel.ELEVATED.is_actionable

    def test_warning_actionable(self) -> None:
        assert AlarmLevel.WARNING.is_actionable

    def test_critical_actionable(self) -> None:
        assert AlarmLevel.CRITICAL.is_actionable

    def test_string_values(self) -> None:
        assert AlarmLevel.NOMINAL.value == "NOMINAL"
        assert AlarmLevel.CRITICAL.value == "CRITICAL"


class TestPhaseAlarm:
    def test_frozen(self) -> None:
        alarm = PhaseAlarm(year=2020, tension=1.5, level=AlarmLevel.WARNING, message="test")
        with pytest.raises(Exception):
            alarm.year = 2021  # type: ignore[misc]

    def test_to_dict_keys(self) -> None:
        alarm = PhaseAlarm(
            year=2020,
            tension=1.5,
            level=AlarmLevel.WARNING,
            message="test",
            variance_ratio=1.2,
            ar1=0.8,
        )
        d = alarm.to_dict()
        for key in ("year", "tension", "level", "message", "variance_ratio", "ar1"):
            assert key in d

    def test_to_dict_level_is_string(self) -> None:
        alarm = PhaseAlarm(year=2020, tension=2.0, level=AlarmLevel.CRITICAL, message="crit")
        assert alarm.to_dict()["level"] == "CRITICAL"


class TestPhaseAlarmMonitor:
    def test_classify_nominal(self, monitor: PhaseAlarmMonitor) -> None:
        assert monitor.classify(0.3) == AlarmLevel.NOMINAL

    def test_classify_elevated(self, monitor: PhaseAlarmMonitor) -> None:
        assert monitor.classify(0.9) == AlarmLevel.ELEVATED

    def test_classify_warning(self, monitor: PhaseAlarmMonitor) -> None:
        assert monitor.classify(1.5) == AlarmLevel.WARNING

    def test_classify_critical(self, monitor: PhaseAlarmMonitor) -> None:
        assert monitor.classify(2.0) == AlarmLevel.CRITICAL

    def test_process_nominal_returns_none(self, monitor: PhaseAlarmMonitor) -> None:
        assert monitor.process(2000, 0.3) is None

    def test_process_warning_returns_alarm(self, monitor: PhaseAlarmMonitor) -> None:
        alarm = monitor.process(2000, 1.5, variance_ratio=1.0, ar1=0.7)
        assert alarm is not None
        assert alarm.level == AlarmLevel.WARNING

    def test_process_critical_returns_alarm(self, monitor: PhaseAlarmMonitor) -> None:
        alarm = monitor.process(2000, 2.5)
        assert alarm is not None
        assert alarm.level == AlarmLevel.CRITICAL

    def test_alarm_count(self, monitor: PhaseAlarmMonitor) -> None:
        monitor.process(2000, 1.5)
        monitor.process(2001, 2.0)
        assert monitor.alarm_count == 2

    def test_suppression_same_level(self, monitor: PhaseAlarmMonitor) -> None:
        monitor.process(2000, 1.5)
        result = monitor.process(2001, 1.5)
        assert result is None  # suppressed (gap=1 < min_gap=3)

    def test_suppression_lifts_after_gap(self, monitor: PhaseAlarmMonitor) -> None:
        monitor.process(2000, 1.5)
        result = monitor.process(2004, 1.5)
        assert result is not None

    def test_critical_alarms_property(self, monitor: PhaseAlarmMonitor) -> None:
        monitor.process(2000, 1.5)  # WARNING
        monitor.process(2010, 2.5)  # CRITICAL
        assert len(monitor.critical_alarms) == 1
        assert monitor.critical_alarms[0].level == AlarmLevel.CRITICAL

    def test_alarms_property_is_copy(self, monitor: PhaseAlarmMonitor) -> None:
        monitor.process(2000, 1.5)
        a = monitor.alarms
        a.clear()
        assert monitor.alarm_count == 1

    def test_summary_structure(self, monitor: PhaseAlarmMonitor) -> None:
        monitor.process(2000, 1.5)
        s = monitor.summary()
        assert "total_alarms" in s
        assert "by_level" in s
        assert "last_alarm" in s

    def test_summary_empty(self, monitor: PhaseAlarmMonitor) -> None:
        s = monitor.summary()
        assert s["total_alarms"] == 0
        assert s["last_alarm"] is None

    def test_reset_clears_alarms(self, monitor: PhaseAlarmMonitor) -> None:
        monitor.process(2000, 1.5)
        monitor.reset()
        assert monitor.alarm_count == 0

    def test_reset_clears_suppression(self, monitor: PhaseAlarmMonitor) -> None:
        monitor.process(2000, 1.5)
        monitor.reset()
        result = monitor.process(2001, 1.5)
        assert result is not None

    def test_alarm_message_contains_year(self, monitor: PhaseAlarmMonitor) -> None:
        alarm = monitor.process(2020, 2.0)
        assert alarm is not None
        assert "2020" in alarm.message

    def test_alarm_message_contains_level(self, monitor: PhaseAlarmMonitor) -> None:
        alarm = monitor.process(2020, 2.0)
        assert alarm is not None
        assert "CRITICAL" in alarm.message

    def test_elevated_alarm(self, monitor: PhaseAlarmMonitor) -> None:
        alarm = monitor.process(2020, 1.0)
        assert alarm is not None
        assert alarm.level == AlarmLevel.ELEVATED

    def test_alarm_stores_variance_ar1(self, monitor: PhaseAlarmMonitor) -> None:
        alarm = monitor.process(2020, 2.0, variance_ratio=1.5, ar1=0.8)
        assert alarm is not None
        assert alarm.variance_ratio == pytest.approx(1.5)
        assert alarm.ar1 == pytest.approx(0.8)

    def test_different_levels_independent_suppression(self, monitor: PhaseAlarmMonitor) -> None:
        monitor.process(2000, 2.5)  # CRITICAL
        result = monitor.process(2001, 1.5)  # WARNING (different level)
        assert result is not None

    def test_live_data_module_imports(self) -> None:
        import genesis_os.live_data as m

        assert m.ERA5Stream is ERA5Stream
        assert m.TensionReading is TensionReading
        assert m.AlarmLevel is AlarmLevel
        assert m.PhaseAlarm is PhaseAlarm
        assert m.PhaseAlarmMonitor is PhaseAlarmMonitor
