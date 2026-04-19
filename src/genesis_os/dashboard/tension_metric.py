"""Live Tension Metric computation for the Mandala-Dashboard v2 (Milestone 3.3).

Bridges the ERA5 live-data stream with the web GUI by maintaining a
rolling tension history that can be pushed into :class:`GUISnapshot`
for real-time visualisation.

The tension metric τ(t) reflects how close the observed system is to a
critical phase transition, combining:

* **Variance ratio** σ²_window / σ²_baseline  (rising near tipping points)
* **Critical slowing down** |AR(1)| coefficient (rising near tipping points)

The CREP-coupled variant τ_Γ = τ · (1 + Γ) amplifies the signal when
the internal CREP state is already elevated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from genesis_os.live_data.era5_stream import ERA5Stream, TensionReading
from genesis_os.live_data.phase_alarm import AlarmLevel, PhaseAlarm, PhaseAlarmMonitor


@dataclass
class TensionMetric:
    """Stateful tension-metric processor for the live dashboard.

    Reads from an :class:`~genesis_os.live_data.era5_stream.ERA5Stream`,
    tracks rolling tension history, and forwards alarms to a
    :class:`~genesis_os.live_data.phase_alarm.PhaseAlarmMonitor`.

    Args:
        stream: ERA5 data stream to read from.  Created automatically if
            ``None`` (uses the bundled CSV).
        history_len: Maximum tension readings to retain in memory.
        gamma: Initial CREP coupling Γ for τ_Γ computation.
    """

    stream: ERA5Stream | None = None
    history_len: int = 100
    gamma: float = 0.0

    _monitor: PhaseAlarmMonitor = field(init=False, repr=False)
    _history: list[TensionReading] = field(default_factory=list, init=False, repr=False)
    _loaded: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if self.stream is None:
            self.stream = ERA5Stream(gamma=self.gamma)
        self._monitor = PhaseAlarmMonitor()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load(self, gamma: float | None = None) -> list[PhaseAlarm]:
        """Load all ERA5 readings and process alarms.

        This is idempotent — repeated calls reload from scratch.

        Args:
            gamma: Override the CREP coupling Γ.

        Returns:
            List of :class:`~genesis_os.live_data.phase_alarm.PhaseAlarm`
            events detected across the full record.
        """
        effective_gamma = gamma if gamma is not None else self.gamma
        self._history.clear()
        self._monitor.reset()

        assert self.stream is not None  # set in __post_init__
        for reading in self.stream.stream(gamma=effective_gamma):
            self._history.append(reading)
            if len(self._history) > self.history_len:
                self._history.pop(0)
            self._monitor.process(
                year=reading.year,
                tension=reading.tension,
                variance_ratio=reading.variance_ratio,
                ar1=reading.ar1,
            )
        self._loaded = True
        return list(self._monitor.alarms)

    def update_gamma(self, gamma: float) -> None:
        """Update the CREP coupling Γ and reload tension history.

        Args:
            gamma: New CREP coupling value.
        """
        self.gamma = gamma
        assert self.stream is not None  # set in __post_init__
        self.stream.gamma = gamma
        self.load(gamma=gamma)

    # ------------------------------------------------------------------
    # Live snapshot helpers
    # ------------------------------------------------------------------

    def latest_tension(self) -> float:
        """Return the most recent tension value, or ``0.0`` if no data loaded."""
        if not self._history:
            return 0.0
        return self._history[-1].tension

    def latest_alarm_level(self) -> AlarmLevel:
        """Return the alarm level corresponding to the latest tension value."""
        if not self._alarms_exist():
            return AlarmLevel.NOMINAL
        return self._monitor.classify(self.latest_tension())

    def _alarms_exist(self) -> bool:
        return self._loaded

    def tension_series(self) -> list[float]:
        """Return the full tension τ(t) history as a list."""
        return [r.tension for r in self._history]

    def year_series(self) -> list[int]:
        """Return the year axis corresponding to :meth:`tension_series`."""
        return [r.year for r in self._history]

    def variance_ratio_series(self) -> list[float]:
        """Return the sliding-window variance ratio series."""
        return [r.variance_ratio for r in self._history]

    def ar1_series(self) -> list[float]:
        """Return the AR(1) autocorrelation series."""
        return [r.ar1 for r in self._history]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def peak_tension(self) -> float:
        """Return the maximum tension value observed."""
        if not self._history:
            return 0.0
        return float(max(r.tension for r in self._history))

    def mean_tension(self) -> float:
        """Return the mean tension over the retained history."""
        if not self._history:
            return 0.0
        return float(np.mean([r.tension for r in self._history]))

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return a diagnostic summary of the tension metric state."""
        return {
            "n_records": len(self._history),
            "latest_tension": self.latest_tension(),
            "peak_tension": self.peak_tension(),
            "mean_tension": self.mean_tension(),
            "alarm_level": self.latest_alarm_level().value,
            "total_alarms": self._monitor.alarm_count,
            "alarm_summary": self._monitor.summary(),
        }
