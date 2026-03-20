"""Phase matrix and transition logic for GenesisOS.

Each phase maps to a dominant CREP axis. Transitions are triggered when
the Γ(C,R,E,P) coupling term crosses a threshold defined per phase.

Phase sequence:
    Initiation → Activation → Integration → Reflection → Initiation (loop)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Phase(str, Enum):
    """Named phases of the Genesis cycle, corresponding to CREP axes."""

    INITIATION = "Initiation"
    ACTIVATION = "Activation"
    INTEGRATION = "Integration"
    REFLECTION = "Reflection"

    @property
    def crep_focus(self) -> str:
        """Return the dominant CREP axis for this phase."""
        mapping = {
            Phase.INITIATION: "C",
            Phase.ACTIVATION: "R",
            Phase.INTEGRATION: "E",
            Phase.REFLECTION: "P",
        }
        return mapping[self]

    @property
    def next_phase(self) -> Phase:
        """Return the subsequent phase in the cycle."""
        sequence = [Phase.INITIATION, Phase.ACTIVATION, Phase.INTEGRATION, Phase.REFLECTION]
        idx = sequence.index(self)
        return sequence[(idx + 1) % len(sequence)]

    @property
    def description(self) -> str:
        """Human-readable description."""
        descriptions = {
            Phase.INITIATION: "Concept and coherence – seeding the field",
            Phase.ACTIVATION: "Resonance and exchange – coupling subsystems",
            Phase.INTEGRATION: "Emergence and development – complex patterns arise",
            Phase.REFLECTION: "Poetics and persistence – self-reflection update",
        }
        return descriptions[self]


@dataclass
class PhaseTransition:
    """Record of a completed phase transition.

    Attributes:
        from_phase: Phase before the transition.
        to_phase: Phase after the transition.
        trigger_gamma: The Γ value that triggered the transition.
        cycle: Cycle index at which the transition occurred.
        metadata: Arbitrary additional data.
    """

    from_phase: Phase
    to_phase: Phase
    trigger_gamma: float
    cycle: int
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_full_cycle(self) -> bool:
        """Return True if this transition completes a full CREP cycle."""
        return self.from_phase == Phase.REFLECTION and self.to_phase == Phase.INITIATION


@dataclass
class PhaseMatrix:
    """Manages the state machine of phase transitions.

    The matrix holds the current phase, tracks transition history, and
    provides the transition threshold per phase.

    Args:
        initial_phase: Starting phase (default: INITIATION).
        thresholds: Per-phase Γ threshold for triggering transition.
            Keys are Phase enum values; missing phases default to 0.6.
    """

    initial_phase: Phase = Phase.INITIATION
    thresholds: dict[Phase, float] = field(
        default_factory=lambda: {
            Phase.INITIATION: 0.55,
            Phase.ACTIVATION: 0.60,
            Phase.INTEGRATION: 0.65,
            Phase.REFLECTION: 0.70,
        }
    )
    _current_phase: Phase = field(init=False)
    _transitions: list[PhaseTransition] = field(default_factory=list, init=False)
    _cycle_count: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self._current_phase = self.initial_phase

    @property
    def current_phase(self) -> Phase:
        """The currently active phase."""
        return self._current_phase

    @property
    def cycle_count(self) -> int:
        """Number of phase transitions recorded."""
        return self._cycle_count

    @property
    def transitions(self) -> list[PhaseTransition]:
        """Read-only view of all recorded transitions."""
        return list(self._transitions)

    @property
    def full_cycles(self) -> int:
        """Number of complete CREP cycles (Reflection → Initiation transitions)."""
        return sum(1 for t in self._transitions if t.is_full_cycle)

    def threshold_for(self, phase: Phase | None = None) -> float:
        """Return the Γ threshold for the given (or current) phase."""
        p = phase if phase is not None else self._current_phase
        return self.thresholds.get(p, 0.6)

    def should_transition(self, gamma: float) -> bool:
        """Return True if gamma meets the transition threshold for the current phase."""
        return gamma >= self.threshold_for()

    def advance(
        self, gamma: float, metadata: dict[str, Any] | None = None
    ) -> PhaseTransition | None:
        """Attempt a phase transition if the threshold is met.

        Args:
            gamma: Current CREP coupling value Γ.
            metadata: Optional data to attach to the transition record.

        Returns:
            A PhaseTransition record if a transition occurred, else None.
        """
        if not self.should_transition(gamma):
            return None
        from_phase = self._current_phase
        to_phase = from_phase.next_phase
        self._current_phase = to_phase
        self._cycle_count += 1
        transition = PhaseTransition(
            from_phase=from_phase,
            to_phase=to_phase,
            trigger_gamma=gamma,
            cycle=self._cycle_count,
            metadata=metadata or {},
        )
        self._transitions.append(transition)
        return transition

    def reset(self) -> None:
        """Reset to initial phase and clear transition history."""
        self._current_phase = self.initial_phase
        self._transitions.clear()
        self._cycle_count = 0
