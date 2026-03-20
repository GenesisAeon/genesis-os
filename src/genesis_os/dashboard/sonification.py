"""Sonification module: mapping CREP states to audible frequencies.

Each CREP axis is mapped to a frequency band:

- **C** (Coherence): fundamental tone 220–440 Hz
- **R** (Resonance): harmonic overtone 440–880 Hz
- **E** (Emergence): sub-octave 110–220 Hz
- **P** (Poetics): upper harmonic 880–1760 Hz

The mapping uses a logarithmic scale within each band, following the
psychoacoustic equal-loudness model.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from genesis_os.core.crep import CREPScore


@dataclass
class SonificationFrame:
    """A single sonification output frame.

    Attributes:
        frequencies: Dict of axis → frequency in Hz.
        amplitudes: Dict of axis → amplitude [0.0, 1.0].
        duration_ms: Duration of the tone in milliseconds.
        cycle: Cycle index.
    """

    frequencies: dict[str, float]
    amplitudes: dict[str, float]
    duration_ms: float
    cycle: int = 0


@dataclass
class Sonifier:
    """Maps CREP scores to frequencies and optional audio synthesis.

    Delegates to the ``sonification`` plugin if available; otherwise
    returns frequency data for external use.

    Args:
        base_hz: Base frequency for the fundamental tone (default 220 Hz).
        duration_ms: Default note duration in ms (default 500).
        use_plugin: Whether to attempt loading the external plugin.
    """

    base_hz: float = 220.0
    duration_ms: float = 500.0
    use_plugin: bool = True
    _plugin: Any = field(default=None, init=False, repr=False)
    _frames: list[SonificationFrame] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if self.use_plugin:
            try:  # pragma: no cover
                import sonification as son  # type: ignore[import-not-found]

                self._plugin = son
            except ImportError:
                self._plugin = None

    def _log_scale(self, value: float, f_min: float, f_max: float) -> float:
        """Map a value in [0, 1] to [f_min, f_max] on a log scale."""
        v = max(0.0, min(1.0, value))
        return f_min * math.exp(v * math.log(f_max / f_min))

    def crep_to_frequencies(self, crep: CREPScore, cycle: int = 0) -> SonificationFrame:
        """Convert a CREPScore to a SonificationFrame.

        Args:
            crep: CREP score to sonify.
            cycle: Cycle index for the frame.

        Returns:
            SonificationFrame with frequencies and amplitudes.
        """
        freqs = {
            "C": self._log_scale(crep.coherence, self.base_hz, self.base_hz * 2),
            "R": self._log_scale(crep.resonance, self.base_hz * 2, self.base_hz * 4),
            "E": self._log_scale(crep.emergence, self.base_hz / 2, self.base_hz),
            "P": self._log_scale(crep.poetics, self.base_hz * 4, self.base_hz * 8),
        }
        amps = {
            "C": crep.coherence,
            "R": crep.resonance,
            "E": crep.emergence,
            "P": crep.poetics,
        }
        frame = SonificationFrame(
            frequencies=freqs,
            amplitudes=amps,
            duration_ms=self.duration_ms,
            cycle=cycle,
        )
        self._frames.append(frame)
        return frame

    def play(self, frame: SonificationFrame) -> bool:
        """Attempt to play the frame using the sonification plugin.

        Args:
            frame: SonificationFrame to play.

        Returns:
            True if playback succeeded via plugin, False otherwise.
        """
        if self._plugin is not None:
            try:
                self._plugin.play(frame.frequencies, frame.amplitudes, frame.duration_ms)
                return True
            except Exception:
                pass
        return False

    @property
    def frames(self) -> list[SonificationFrame]:
        """All generated frames."""
        return list(self._frames)

    def sequence(self, crep_scores: list[CREPScore]) -> list[SonificationFrame]:
        """Convert a sequence of CREP scores to sonification frames.

        Args:
            crep_scores: List of CREPScore snapshots.

        Returns:
            List of SonificationFrame objects.
        """
        return [self.crep_to_frequencies(score, cycle=i) for i, score in enumerate(crep_scores)]
