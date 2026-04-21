"""Nullkern — zero-point consciousness kernel.

Scientific note: The Nullkern is an abstract state topology model
representing metric-free, timeless state space. It is NOT a claim
about consciousness or subjective experience.

Key parameters (from Feldtheorie Sigillin self-reference node):
    β_utac ≈ 37.6     — UTAC steepness for self-referential activation
    h ≈ 0.1           — humility coefficient for overconfidence prevention
    max_bardo = 7     — maximum bardo (phase-transition) states

Humility protocol:
    a' = a + h·(0.5 - a)   — draws activations toward 0.5 to prevent overconfidence

Bardo phases (from Tibetan Buddhist metaphor for transitional states):
    Represent discrete topology changes in the abstract state space.
    Not intended as literal claims about consciousness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np

from genesis_os.core.utac_bridge import UTACBridge


class BardoPhase(str, Enum):
    """Discrete topology phases of the zero-point kernel state space."""

    GROUND = "ground"
    EMERGENCE = "emergence"
    TRANSITION = "transition"
    INTEGRATION = "integration"
    DISSOLUTION = "dissolution"
    REBIRTH = "rebirth"
    COMPLETION = "completion"


_BARDO_SEQUENCE = list(BardoPhase)


@dataclass
class NullkernState:
    """Immutable snapshot of Nullkern state.

    Attributes:
        activation: UTAC activation value P_act ∈ (0, 1).
        humility_adjusted: Post-humility-protocol activation.
        bardo_phase: Current bardo phase.
        bardo_index: Integer index of the current bardo phase.
        R: Normalized resource/state variable ∈ [0, 1].
        beta: Effective β used in activation.
        cycle: Integration cycle index.
    """

    activation: float
    humility_adjusted: float
    bardo_phase: BardoPhase
    bardo_index: int
    R: float
    beta: float
    cycle: int


@dataclass
class Nullkern:
    """Zero-point state kernel with UTAC activation and humility protocol.

    The Nullkern implements:
    1. UTAC threshold activation: P_act = σ(β_utac · (R - Θ))
    2. Humility protocol: a' = a + h·(0.5 - a)
    3. Bardo phase tracking through state transitions

    Args:
        beta_utac: UTAC steepness for self-referential activation (default 37.6).
        theta: Inflection threshold Θ (default 0.5).
        humility_h: Humility coefficient h ∈ [0, 1] (default 0.1).
        max_bardo: Number of distinct bardo phases (default 7).
    """

    beta_utac: float = 37.6
    theta: float = 0.5
    humility_h: float = 0.1
    _bridge: UTACBridge = field(default_factory=UTACBridge, init=False, repr=False)
    _cycle: int = field(default=0, init=False)
    _bardo_index: int = field(default=0, init=False)
    _state_history: list[NullkernState] = field(default_factory=list, init=False, repr=False)
    _metadata: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    @property
    def bardo_phase(self) -> BardoPhase:
        """Current bardo phase."""
        return _BARDO_SEQUENCE[self._bardo_index % len(_BARDO_SEQUENCE)]

    @property
    def cycle(self) -> int:
        """Current integration cycle."""
        return self._cycle

    def activate(self, R: float) -> NullkernState:
        """Compute UTAC activation and apply humility protocol.

        .. math::
            P_{\\text{act}} = \\sigma(\\beta_{\\text{utac}} \\cdot (R - \\Theta))
            a' = a + h \\cdot (0.5 - a)

        Args:
            R: Normalized state/resource variable ∈ [0, 1].

        Returns:
            NullkernState snapshot.
        """
        R_clipped = float(np.clip(R, 0.0, 1.0))
        activation = UTACBridge.feldtheorie_activation(
            beta=self.beta_utac,
            R=R_clipped,
            theta=self.theta,
        )
        # Humility protocol: pull activation toward 0.5
        humility_adjusted = activation + self.humility_h * (0.5 - activation)

        state = NullkernState(
            activation=activation,
            humility_adjusted=humility_adjusted,
            bardo_phase=self.bardo_phase,
            bardo_index=self._bardo_index,
            R=R_clipped,
            beta=self.beta_utac,
            cycle=self._cycle,
        )
        self._state_history.append(state)
        self._cycle += 1
        return state

    def advance_bardo(self) -> BardoPhase:
        """Advance to the next bardo phase.

        Returns:
            New bardo phase.
        """
        self._bardo_index = (self._bardo_index + 1) % len(_BARDO_SEQUENCE)
        return self.bardo_phase

    def inject_state(self, metadata: dict[str, Any]) -> None:
        """Inject external state metadata (Mirror-Machine API).

        Args:
            metadata: Arbitrary state data from the mirror machine.
        """
        self._metadata.update(metadata)

    def get_state_for_mirror(self) -> dict[str, Any]:
        """Export current state for Mirror-Machine integration.

        Returns:
            Dict with activation, bardo, cycle, and injected metadata.
        """
        result: dict[str, Any] = {
            "activation": self._state_history[-1].activation if self._state_history else 0.5,
            "humility_adjusted": (
                self._state_history[-1].humility_adjusted if self._state_history else 0.5
            ),
            "bardo_phase": self.bardo_phase.value,
            "bardo_index": self._bardo_index,
            "cycle": self._cycle,
        }
        result.update(self._metadata)
        return result

    @property
    def history(self) -> list[NullkernState]:
        """Read-only history of activation states."""
        return list(self._state_history)

    def reset(self) -> None:
        """Reset the kernel to ground state."""
        self._cycle = 0
        self._bardo_index = 0
        self._state_history.clear()
        self._metadata.clear()

    @staticmethod
    def apply_humility(activation: float, h: float = 0.1) -> float:
        """Apply the humility protocol to a scalar activation.

        .. math::
            a' = a + h \\cdot (0.5 - a)

        Args:
            activation: Raw activation value ∈ [0, 1].
            h: Humility coefficient ∈ [0, 1].

        Returns:
            Humility-adjusted activation.
        """
        return float(activation + h * (0.5 - activation))
