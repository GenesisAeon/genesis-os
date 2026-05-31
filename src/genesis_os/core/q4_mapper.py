"""Q4-Mapper: Kritische Schnittstelle zwischen kontinuierlichem und diskretem Layer.

Dies ist der EINZIGE erlaubte Weg von kontinuierlichen CREP-Float-Werten
zu diskreten Q4-Zuständen. Kontinuierliche CREP-Werte DÜRFEN NICHT direkt
an Q4-Logik übergeben werden — immer via Q4Mapper (Layer-Separation-Regel).

Dreischicht-Architektur:
    Schicht 1: Geometrie (Φ/1.6)    — kontinuierlich
    Schicht 2: Zustand (Q4/4-Bit)   — diskret
    Schicht 3: Kopplung (Gray-Code) — Übergänge

Dieser Mapper ist der definierte Übergang von Schicht 1 → Schicht 2.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final

from genesis_os.core.crep import CREPScore
from genesis_os.core.gray_code import hamming_distance, encode as gray_encode
from genesis_os.core.q4_state import Q4State, InvalidTransitionError

logger = logging.getLogger(__name__)

#: Standard-Schwellenwerte für CREP → Q4-Mapping (LeChat-Analyse, Mai 2026).
DEFAULT_Q4_THRESHOLDS: Final[dict[str, float]] = {
    "C": 0.5,
    "R": 0.6,
    "E": 0.7,
    "P": 0.8,
}


class LayerSeparationError(TypeError):
    """Wird ausgelöst wenn versucht wird, Floats direkt an Q4-Logik zu übergeben."""


@dataclass
class Q4Mapper:
    """Wandelt kontinuierliche CREP-Float-Werte in diskrete 4-Bit Q4-Zustände um.

    Dies ist die kritische Schnittstelle zwischen Layer 1 (kontinuierlich)
    und Layer 2 (diskret). Ohne diesen Mapper darf kein Code CREP-Floats
    direkt in Q4-Logik einspeisen.

    Args:
        thresholds: Schwellenwerte für jede CREP-Dimension.
                    Defaults: C=0.5, R=0.6, E=0.7, P=0.8.

    Example:
        mapper = Q4Mapper()
        score = CREPScore(coherence=0.8, resonance=0.44, emergence=0.91, poetics=0.87)
        state = mapper.map(score)
        # → Q4State(C=1, R=0, E=1, P=1, id=11, binary='1011')
    """

    thresholds: dict[str, float] = field(
        default_factory=lambda: dict(DEFAULT_Q4_THRESHOLDS)
    )

    def __post_init__(self) -> None:
        required = {"C", "R", "E", "P"}
        missing = required - set(self.thresholds)
        if missing:
            raise ValueError(f"Missing thresholds for dimensions: {missing}")
        for dim, val in self.thresholds.items():
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"Threshold for {dim} must be in [0,1], got {val}")

    def map(self, score: CREPScore) -> Q4State:
        """Wandelt CREPScore in Q4State um.

        Jede CREP-Dimension wird mit ihrem Schwellenwert verglichen:
            C_flag = 1 if score.coherence >= thresholds['C'] else 0

        Args:
            score: CREPScore mit float-Werten in [0, 1].

        Returns:
            Q4State mit binären Flags (0 oder 1) für jede Dimension.
        """
        return Q4State(
            C=int(score.coherence >= self.thresholds["C"]),
            R=int(score.resonance >= self.thresholds["R"]),
            E=int(score.emergence >= self.thresholds["E"]),
            P=int(score.poetics >= self.thresholds["P"]),
        )

    def map_with_timestamp(
        self, score: CREPScore, t: float
    ) -> tuple[Q4State, float]:
        """Wandelt CREPScore in Q4State um und gibt den Zeitstempel zurück."""
        return self.map(score), t

    def calibrate(self, history: list[CREPScore]) -> dict[str, float]:
        """Auto-Kalibrierung: Setzt Schwellenwerte auf den Median der historischen Werte.

        Sinnvoll wenn die Verteilung der CREP-Werte im Datensatz bekannt ist.
        Nach der Kalibrierung werden ca. 50% der Samples als '1' kodiert.

        Args:
            history: Liste historischer CREPScore-Snapshots.

        Returns:
            Neu kalibrierte Schwellenwerte (auch in self.thresholds gespeichert).
        """
        if not history:
            return dict(self.thresholds)

        import statistics

        new_thresholds = {
            "C": statistics.median(s.coherence for s in history),
            "R": statistics.median(s.resonance for s in history),
            "E": statistics.median(s.emergence for s in history),
            "P": statistics.median(s.poetics for s in history),
        }
        self.thresholds = new_thresholds
        logger.info("Q4Mapper: calibrated thresholds to %s", new_thresholds)
        return new_thresholds


@dataclass
class ThresholdCrossingDetector:
    """Erkennt Schwellenwertüberschreitungen als potenzielle Q4-Zustandsübergänge.

    Beobachtet aufeinanderfolgende CREPScores und meldet welche CREP-Dimensionen
    ihren Schwellenwert gekreuzt haben. Jede Kreuzung ist ein potenzieller
    Q4-Zustandsübergang.

    Bindet in den bestehenden Phase-Transition-Loop von genesis-os ein.

    Args:
        mapper: Q4Mapper der die Schwellenwerte definiert.
    """

    mapper: Q4Mapper = field(default_factory=Q4Mapper)
    _last_state: Q4State | None = field(default=None, init=False, repr=False)

    def update(self, score: CREPScore) -> list[str]:
        """Aktualisiert internen Zustand und gibt gequerte Dimensionen zurück.

        Args:
            score: Aktueller CREPScore.

        Returns:
            Liste der Dimensionsnamen die ihren Schwellenwert gekreuzt haben,
            z.B. ['R', 'E']. Leer wenn kein Übergang stattgefunden hat.
        """
        current = self.mapper.map(score)
        crossings: list[str] = []

        if self._last_state is not None:
            for dim, prev_flag, curr_flag in (
                ("C", self._last_state.C, current.C),
                ("R", self._last_state.R, current.R),
                ("E", self._last_state.E, current.E),
                ("P", self._last_state.P, current.P),
            ):
                if prev_flag != curr_flag:
                    crossings.append(dim)
                    logger.debug(
                        "ThresholdCrossingDetector: %s crossed (%d→%d)",
                        dim, prev_flag, curr_flag,
                    )

        self._last_state = current
        return crossings

    def current_state(self) -> Q4State | None:
        """Gibt den zuletzt berechneten Q4-Zustand zurück."""
        return self._last_state

    def reset(self) -> None:
        """Setzt internen Zustand zurück."""
        self._last_state = None


def validate_q4_transition(from_state: Q4State, to_state: Q4State) -> None:
    """Prüft ob ein Q4-Zustandsübergang dem Gray-Code Policy Gate entspricht.

    Erlaubt sind nur Übergänge mit Hamming-Distanz = 1 (ein Bit Unterschied).
    Der Systemzustand kann sich nur in einer CREP-Dimension gleichzeitig ändern.

    Args:
        from_state: Ausgangszustand.
        to_state: Zielzustand.

    Raises:
        InvalidTransitionError: Wenn Hamming-Distanz > 1.
    """
    dist = hamming_distance(from_state.id, to_state.id)
    if dist != 1:
        raise InvalidTransitionError(
            f"Invalid Q4 transition {from_state.binary} → {to_state.binary}: "
            f"Hamming distance = {dist}, must be 1 (Gray-Code Policy Gate). "
            f"Use suggest_gray_path() to find a valid transition sequence."
        )
