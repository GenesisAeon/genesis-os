"""Mandala dashboard: geometric visualisation of CREP states.

Renders the four CREP axes as a circular mandala, optionally delegating
to the ``mandala-visualizer`` plugin if available. Falls back to an
ASCII representation otherwise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from genesis_os.core.crep import CREPScore
from genesis_os.core.phase import Phase


@dataclass
class MandalaFrame:
    """Single animation frame of the mandala.

    Attributes:
        lines: ASCII line buffer.
        crep: The CREP score for this frame.
        phase: Active phase when this frame was generated.
        cycle: Cycle index.
    """

    lines: list[str]
    crep: CREPScore
    phase: Phase
    cycle: int


@dataclass
class MandalaDashboard:
    """Integrated Mandala dashboard for real-time CREP visualisation.

    Uses ``mandala-visualizer`` when installed; falls back to ASCII art.

    Args:
        width: Canvas width in characters (default 60).
        height: Canvas height in characters (default 30).
        use_plugin: Whether to attempt loading the external plugin.
    """

    width: int = 60
    height: int = 30
    use_plugin: bool = True
    _plugin: Any = field(default=None, init=False, repr=False)
    _frames: list[MandalaFrame] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if self.use_plugin:
            try:  # pragma: no cover
                import mandala_visualizer as mv  # type: ignore[import-not-found]

                self._plugin = mv
            except ImportError:
                self._plugin = None

    def render_ascii(self, crep: CREPScore, phase: Phase = Phase.INITIATION, cycle: int = 0) -> str:
        """Render a mandala as ASCII art and return the string.

        The four quadrants represent C (top-left), R (top-right),
        E (bottom-right), P (bottom-left). Bar length encodes the score.

        Args:
            crep: CREP score to render.
            phase: Active phase (affects label styling).
            cycle: Current cycle index.

        Returns:
            Multi-line ASCII string.
        """
        bar_max = 20
        bars = {
            "C": int(crep.coherence * bar_max),
            "R": int(crep.resonance * bar_max),
            "E": int(crep.emergence * bar_max),
            "P": int(crep.poetics * bar_max),
        }
        separator = "+" + "-" * (bar_max + 10) + "+"
        lines: list[str] = [
            separator,
            f"| Mandala  Phase:{phase.value:<12} Cycle:{cycle:<5}|",
            separator,
        ]
        for axis, length in bars.items():
            bar = "█" * length + "░" * (bar_max - length)
            axis_map = {"C": "coherence", "R": "resonance", "E": "emergence", "P": "poetics"}
            score = getattr(crep, axis_map[axis])
            lines.append(f"| {axis}  [{bar}] {score:.3f} |")
        lines += [separator, f"| Γ = {crep.gamma:.6f}{' ' * (bar_max + 2)}|", separator]
        frame = MandalaFrame(lines=lines, crep=crep, phase=phase, cycle=cycle)
        self._frames.append(frame)
        return "\n".join(lines)

    def render_polar(self, crep: CREPScore) -> list[tuple[float, float, str]]:
        """Return CREP axes as polar coordinates for external renderers.

        Args:
            crep: CREP score to render.

        Returns:
            List of (radius, angle_rad, label) tuples.
        """
        axes = [
            (crep.coherence, 0.0, "C"),
            (crep.resonance, math.pi / 2.0, "R"),
            (crep.emergence, math.pi, "E"),
            (crep.poetics, 3.0 * math.pi / 2.0, "P"),
        ]
        return [(r, angle, label) for r, angle, label in axes]

    @property
    def frames(self) -> list[MandalaFrame]:
        """All rendered frames."""
        return list(self._frames)

    def plugin_render(self, crep: CREPScore, **kwargs: Any) -> Any:
        """Delegate rendering to the mandala-visualizer plugin.

        Falls back to ASCII if the plugin is not available.

        Args:
            crep: CREP score.
            **kwargs: Passed to the plugin renderer.

        Returns:
            Plugin render result or ASCII string.
        """
        if self._plugin is not None:
            try:
                return self._plugin.render(crep.to_vector(), **kwargs)
            except Exception:
                pass
        return self.render_ascii(crep)
