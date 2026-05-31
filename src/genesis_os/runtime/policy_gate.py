"""Frame Policy Gate: Gray-Code-Übergangsprüfung vor NATS-Publikation.

Erzwingt die Invariante: Nur Q4-Zustandsübergänge mit Hamming-Distanz = 1
dürfen auf ga.frame.*-Subjects publiziert werden.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from genesis_os.core.gray_code import hamming_distance
from genesis_os.core.q4_state import InvalidTransitionError, Q4State

logger = logging.getLogger(__name__)


@dataclass
class FramePolicyGate:
    """Gray-Code Policy Gate für NATS Frame-Publikationen.

    Jeder Zustandsübergang muss Hamming-Distanz = 1 haben.
    Verstöße werden geloggt und können als Fehler oder Warnung behandelt werden.

    Args:
        strict: Bei True → InvalidTransitionError, bei False → nur Log-Warnung.
    """

    strict: bool = True
    _violation_count: int = field(default=0, init=False, repr=False)

    def check(self, from_state: Q4State, to_state: Q4State) -> bool:
        """Prüft ob der Übergang gültig ist (Hamming = 1).

        Args:
            from_state: Ausgangszustand.
            to_state: Zielzustand.

        Returns:
            True wenn gültig.

        Raises:
            InvalidTransitionError: Wenn strict=True und Hamming > 1.
        """
        if from_state == to_state:
            return True

        dist = hamming_distance(from_state.id, to_state.id)
        if dist == 1:
            logger.debug(
                "PolicyGate: ✓ %s → %s (Hamming=%d)",
                from_state.binary, to_state.binary, dist,
            )
            return True

        self._violation_count += 1
        msg = (
            f"PolicyGate violation: {from_state.binary} → {to_state.binary} "
            f"(Hamming={dist}, must be 1). Violation #{self._violation_count}."
        )
        if self.strict:
            raise InvalidTransitionError(msg)
        logger.warning(msg)
        return False

    @property
    def violation_count(self) -> int:
        """Anzahl der Policy-Verletzungen seit Instanziierung."""
        return self._violation_count
