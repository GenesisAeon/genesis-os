"""Phase-transition alarm system for the Mirror-Machine (Milestone 3.2).

Monitors the Tension Metric τ(t) from the ERA5 stream and emits
structured :class:`PhaseAlarm` events when τ crosses configurable
severity thresholds — wiring the live climate signal into the
UTAC-Logistic feedback loop.

Alarm levels (default thresholds):

+-------------+---------------------+
| Level       | τ threshold         |
+=============+=====================+
| NOMINAL     | τ < 0.8             |
+-------------+---------------------+
| ELEVATED    | 0.8 ≤ τ < 1.2       |
+-------------+---------------------+
| WARNING     | 1.2 ≤ τ < 1.8       |
+-------------+---------------------+
| CRITICAL    | τ ≥ 1.8             |
+-------------+---------------------+
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class AlarmLevel(str, Enum):
    """Severity level for a phase-transition alarm."""

    NOMINAL = "NOMINAL"
    ELEVATED = "ELEVATED"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    @property
    def is_actionable(self) -> bool:
        """Return ``True`` if the alarm level warrants operator attention."""
        return self in {AlarmLevel.WARNING, AlarmLevel.CRITICAL}


@dataclass(frozen=True)
class PhaseAlarm:
    """Immutable record of a single phase-transition alarm event.

    Attributes:
        year: Calendar year at which the alarm was raised.
        tension: Tension metric τ value that triggered the alarm.
        level: Alarm severity level.
        message: Human-readable alarm description.
        variance_ratio: Sliding-window variance / baseline variance at alarm.
        ar1: Lag-1 autocorrelation at alarm.
    """

    year: int
    tension: float
    level: AlarmLevel
    message: str
    variance_ratio: float = 0.0
    ar1: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary."""
        return {
            "year": self.year,
            "tension": self.tension,
            "level": self.level.value,
            "message": self.message,
            "variance_ratio": self.variance_ratio,
            "ar1": self.ar1,
        }


@dataclass
class PhaseAlarmMonitor:
    """Monitors tension readings and emits :class:`PhaseAlarm` events.

    Compares each incoming τ value against severity thresholds and
    records alarms.  Can be wired directly into the Mirror-Machine
    UTAC-Loop to modulate the carrying capacity K or growth rate r
    in response to live climate signals.

    Args:
        threshold_elevated: τ threshold for ELEVATED level (default ``0.8``).
        threshold_warning: τ threshold for WARNING level (default ``1.2``).
        threshold_critical: τ threshold for CRITICAL level (default ``1.8``).
        min_gap: Minimum years between alarms at the same level to suppress
            repeated firing (default ``3``).
    """

    threshold_elevated: float = 0.8
    threshold_warning: float = 1.2
    threshold_critical: float = 1.8
    min_gap: int = 3

    _alarms: list[PhaseAlarm] = None  # type: ignore[assignment]
    _last_alarm_year: dict[AlarmLevel, int] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self._alarms = []
        self._last_alarm_year = {}

    # ------------------------------------------------------------------
    # Level classification
    # ------------------------------------------------------------------

    def classify(self, tension: float) -> AlarmLevel:
        """Map a tension value to its alarm level.

        Args:
            tension: Tension metric τ ≥ 0.

        Returns:
            Corresponding :class:`AlarmLevel`.
        """
        if tension >= self.threshold_critical:
            return AlarmLevel.CRITICAL
        if tension >= self.threshold_warning:
            return AlarmLevel.WARNING
        if tension >= self.threshold_elevated:
            return AlarmLevel.ELEVATED
        return AlarmLevel.NOMINAL

    # ------------------------------------------------------------------
    # Alarm processing
    # ------------------------------------------------------------------

    def _suppressed(self, level: AlarmLevel, year: int) -> bool:
        """Return ``True`` if this alarm should be suppressed due to recency."""
        last = self._last_alarm_year.get(level)
        if last is None:
            return False
        return (year - last) < self.min_gap

    def process(
        self,
        year: int,
        tension: float,
        variance_ratio: float = 0.0,
        ar1: float = 0.0,
    ) -> PhaseAlarm | None:
        """Evaluate a tension reading and optionally emit an alarm.

        Args:
            year: Calendar year of the reading.
            tension: Tension metric τ(t).
            variance_ratio: Sliding-window variance ratio (informational).
            ar1: Lag-1 AR(1) coefficient (informational).

        Returns:
            :class:`PhaseAlarm` if a non-nominal alarm fires, else ``None``.
        """
        level = self.classify(tension)
        if level == AlarmLevel.NOMINAL:
            return None
        if self._suppressed(level, year):
            return None

        message = self._format_message(level, year, tension)
        alarm = PhaseAlarm(
            year=year,
            tension=tension,
            level=level,
            message=message,
            variance_ratio=variance_ratio,
            ar1=ar1,
        )
        self._alarms.append(alarm)
        self._last_alarm_year[level] = year
        return alarm

    @staticmethod
    def _format_message(level: AlarmLevel, year: int, tension: float) -> str:
        """Build a human-readable alarm message."""
        prefix = {
            AlarmLevel.ELEVATED: "Elevated tension detected",
            AlarmLevel.WARNING: "WARNING: High tension — phase transition risk",
            AlarmLevel.CRITICAL: "CRITICAL: Imminent phase transition — τ exceeds critical threshold",
        }
        return f"[{level.value}] {prefix[level]} at year {year} (τ={tension:.3f})"

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def alarms(self) -> list[PhaseAlarm]:
        """All emitted alarms (defensive copy)."""
        return list(self._alarms)

    @property
    def alarm_count(self) -> int:
        """Total number of alarms emitted."""
        return len(self._alarms)

    @property
    def critical_alarms(self) -> list[PhaseAlarm]:
        """All CRITICAL-level alarms."""
        return [a for a in self._alarms if a.level == AlarmLevel.CRITICAL]

    def summary(self) -> dict[str, Any]:
        """Return a summary of the monitor state."""
        by_level: dict[str, int] = {level.value: 0 for level in AlarmLevel}
        for alarm in self._alarms:
            by_level[alarm.level.value] += 1
        return {
            "total_alarms": self.alarm_count,
            "by_level": by_level,
            "last_alarm": self._alarms[-1].to_dict() if self._alarms else None,
        }

    def reset(self) -> None:
        """Clear all recorded alarms and suppression state."""
        self._alarms.clear()
        self._last_alarm_year.clear()
