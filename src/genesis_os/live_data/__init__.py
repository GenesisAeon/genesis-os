"""Real-time data integration for Cycle-3 Live-Data milestone (3.2).

Provides streaming access to ERA5 Arctic sea-ice reanalysis data,
computes the Tension Metric τ(t), and emits phase-transition alarms
when critical thresholds are crossed.
"""

from genesis_os.live_data.era5_stream import ERA5Stream, TensionReading
from genesis_os.live_data.phase_alarm import AlarmLevel, PhaseAlarm, PhaseAlarmMonitor

__all__ = [
    "AlarmLevel",
    "ERA5Stream",
    "PhaseAlarm",
    "PhaseAlarmMonitor",
    "TensionReading",
]
