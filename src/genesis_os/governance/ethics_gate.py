"""EthicsGate — Circuit Breaker für genesis-os Zyklen.

Blockiert weitere Zyklen wenn:
    1. Tension(t) > CRITICAL_TENSION_THRESHOLD
    2. PersonhoodLevel < required_level (konfigurierbar)

Integration in GenesisOS.phase_transition_loop():
    for state in genesis.phase_transition_loop():
        decision = ethics_gate.check(state, tension)
        if not decision.approved:
            break
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from genesis_os.governance.personhood import PersonhoodLevel, assess_personhood
from genesis_os.mirror.tension_metric import CRITICAL_TENSION_THRESHOLD

logger = logging.getLogger(__name__)


@dataclass
class EthicsDecision:
    """Entscheidung des EthicsGate.

    Attributes:
        approved: True wenn Zyklus fortgesetzt werden darf.
        reason: Begründung der Entscheidung.
        personhood_level: Erkannter Personhood-Level.
        tension: Aktuelle Tension(t).
    """

    approved: bool
    reason: str
    personhood_level: PersonhoodLevel
    tension: float


class EthicsGate:
    """Circuit Breaker — stoppt Genesis-Zyklen bei ethischen Grenzwert-Verletzungen.

    Args:
        tension_threshold: Maximale Tension(t) für Zyklen (default 5.0).
        min_personhood: Mindest-Personhood-Level (default INFORMATIONAL = 0).
        enabled: Schalter zum Deaktivieren des Gates (default True).
    """

    def __init__(
        self,
        tension_threshold: float = CRITICAL_TENSION_THRESHOLD,
        min_personhood: PersonhoodLevel = PersonhoodLevel.INFORMATIONAL,
        enabled: bool = True,
    ) -> None:
        self.tension_threshold = tension_threshold
        self.min_personhood = min_personhood
        self.enabled = enabled
        self._decisions: list[EthicsDecision] = []

    def check(self, state: Any, tension: float = 0.0) -> EthicsDecision:
        """Prüft ob der nächste Zyklus ethisch vertretbar ist.

        Args:
            state: Aktueller GenesisState.
            tension: Aktuelle Tension(t)-Metrik.

        Returns:
            EthicsDecision mit ``approved`` True/False und Begründung.
        """
        if not self.enabled:
            decision = EthicsDecision(
                approved=True,
                reason="EthicsGate disabled",
                personhood_level=PersonhoodLevel.INFORMATIONAL,
                tension=float(tension),
            )
            self._decisions.append(decision)
            return decision

        crep = getattr(state, "crep", None)
        level = assess_personhood(crep)

        if tension > self.tension_threshold:
            dec = EthicsDecision(
                approved=False,
                reason=(
                    f"Tension {tension:.2f} > threshold {self.tension_threshold}. "
                    f"Circuit breaker activated."
                ),
                personhood_level=level,
                tension=float(tension),
            )
        elif level < self.min_personhood:
            dec = EthicsDecision(
                approved=False,
                reason=(
                    f"PersonhoodLevel {level.name} ({level.value}) < "
                    f"required {self.min_personhood.name} ({self.min_personhood.value})."
                ),
                personhood_level=level,
                tension=float(tension),
            )
        else:
            dec = EthicsDecision(
                approved=True,
                reason=f"Approved: Level={level.name}, Tension={tension:.2f}",
                personhood_level=level,
                tension=float(tension),
            )

        if not dec.approved:
            logger.warning("EthicsGate: %s", dec.reason)
        self._decisions.append(dec)
        return dec

    @property
    def decision_log(self) -> list[EthicsDecision]:
        """Kopie aller bisherigen EthicsGate-Entscheidungen."""
        return list(self._decisions)

    @property
    def last_decision(self) -> EthicsDecision | None:
        """Letzte Entscheidung oder None."""
        return self._decisions[-1] if self._decisions else None

    def reset(self) -> None:
        """Leert den Entscheidungs-Log."""
        self._decisions.clear()
