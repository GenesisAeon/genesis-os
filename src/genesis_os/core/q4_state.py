"""Q4-Zustandsraum: 4-Bit diskrete Zustände für GenesisAeon.

Lokale Implementierung des Q4-Zustandsraums.
Wird künftig durch das eigenständige genesis-q4-core Package ersetzt.

Mathematische Grundlagen:
    16 Zustände = 4 Bit  (H = log₂(16) = 4 Bit — NICHT 16 Bit!)
    ID = 8*C + 4*R + 2*E + P  → 0..15
    Gray-Code: g(n) = n XOR (n >> 1)
    Hamming-Distanz aufeinanderfolgender Gray-Codes: immer = 1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

#: Kanonische Gray-Code-Traversal aller 16 Q4-Zustände.
#: Benachbarte Einträge unterscheiden sich exakt um 1 Bit.
GRAY_ORDER: Final[list[int]] = [0, 1, 3, 2, 6, 7, 5, 4, 12, 13, 15, 14, 10, 11, 9, 8]

#: Anzahl Zustände im Q4-Raum.
Q4_STATE_COUNT: Final[int] = 16

#: Bit-Breite des Q4-Zustandsraums: log₂(16) = 4 Bit.
Q4_ENTROPY_BITS: Final[float] = 4.0

#: Anzahl Kanten im Tesserakt (= gültige 1-Bit-Übergänge).
TESSERACT_EDGES: Final[int] = 32


class InvalidQ4StateError(ValueError):
    """Ungültige CREP-Flag-Werte (müssen 0 oder 1 sein)."""


class InvalidTransitionError(ValueError):
    """Zustandsübergang verletzt Gray-Code Policy Gate (Hamming > 1)."""


@dataclass(frozen=True)
class Q4State:
    """4-Bit diskreter Zustand im GenesisAeon Q4-Zustandsraum.

    Codiert den binären Schwellenwert-Status aller vier CREP-Dimensionen.
    Jede Dimension ist 0 (unter Schwellenwert) oder 1 (über Schwellenwert).

    Attributes:
        C: Kohärenz-Flag (0 oder 1).
        R: Resonanz-Flag (0 oder 1).
        E: Emergenz-Flag (0 oder 1).
        P: Poetik-Flag (0 oder 1).

    Note:
        16 Zustände = 4 Bit. Ein einzelner Zustand bei Gleichverteilung
        (p = 1/16) trägt 4 Bit Selbst-Information. Nicht 16 Bit.
    """

    C: int
    R: int
    E: int
    P: int

    def __post_init__(self) -> None:
        for name, val in (("C", self.C), ("R", self.R), ("E", self.E), ("P", self.P)):
            if val not in (0, 1):
                raise InvalidQ4StateError(
                    f"Q4State.{name} must be 0 or 1, got {val!r}"
                )

    @property
    def id(self) -> int:
        """Numerische ID im Bereich 0..15. Berechnet als 8C + 4R + 2E + P."""
        return 8 * self.C + 4 * self.R + 2 * self.E + self.P

    @property
    def binary(self) -> str:
        """4-Bit Binärdarstellung als String, z.B. '1011'."""
        return f"{self.id:04b}"

    @property
    def gray_id(self) -> int:
        """Gray-kodierte ID: g(id) = id XOR (id >> 1)."""
        n = self.id
        return n ^ (n >> 1)

    @property
    def entropy_bits(self) -> float:
        """Entropie des Q4-Raums bei Gleichverteilung: log₂(16) = 4.0 Bit."""
        return Q4_ENTROPY_BITS

    def neighbors(self) -> list[Q4State]:
        """Gibt alle gültigen Gray-Code-Nachbarzustände zurück (Hamming = 1)."""
        result = []
        for bit in range(4):
            flipped_id = self.id ^ (1 << bit)
            result.append(Q4State.from_id(flipped_id))
        return result

    @classmethod
    def from_id(cls, state_id: int) -> Q4State:
        """Erzeugt Q4State aus numerischer ID (0..15)."""
        if not 0 <= state_id <= 15:
            raise InvalidQ4StateError(f"state_id must be 0..15, got {state_id}")
        return cls(
            C=(state_id >> 3) & 1,
            R=(state_id >> 2) & 1,
            E=(state_id >> 1) & 1,
            P=state_id & 1,
        )

    @classmethod
    def from_binary(cls, binary: str) -> Q4State:
        """Erzeugt Q4State aus 4-Bit-Binärstring, z.B. '1011'."""
        if len(binary) != 4 or not all(c in "01" for c in binary):
            raise InvalidQ4StateError(f"Expected 4-bit binary string, got {binary!r}")
        return cls(C=int(binary[0]), R=int(binary[1]), E=int(binary[2]), P=int(binary[3]))

    def __repr__(self) -> str:
        return (
            f"Q4State(C={self.C}, R={self.R}, E={self.E}, P={self.P},"
            f" id={self.id}, binary='{self.binary}')"
        )

    def to_dict(self) -> dict[str, int | str]:
        """Serialisiert Q4State als Dictionary."""
        return {
            "C": self.C,
            "R": self.R,
            "E": self.E,
            "P": self.P,
            "id": self.id,
            "binary": self.binary,
        }
