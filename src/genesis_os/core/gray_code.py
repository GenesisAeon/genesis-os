"""Gray-Code Utilities für Q4-Zustandsübergänge.

Gray-Code garantiert Hamming-Distanz = 1 zwischen aufeinanderfolgenden Codes.
Das ist die mathematische Grundlage des Q4 Policy Gates: Der Systemzustand
kann sich nur in einer CREP-Dimension gleichzeitig ändern.

Lokale Implementierung — wird künftig durch genesis-q4-core ersetzt.
"""

from __future__ import annotations


def encode(n: int) -> int:
    """Kodiert eine Ganzzahl in Gray-Code: g(n) = n XOR (n >> 1)."""
    return n ^ (n >> 1)


def decode(g: int) -> int:
    """Dekodiert Gray-Code zurück zur Binärzahl (invertierbar)."""
    mask = g >> 1
    while mask:
        g ^= mask
        mask >>= 1
    return g


def hamming_distance(a: int, b: int) -> int:
    """Hamming-Distanz zwischen zwei Ganzzahlen (Anzahl unterschiedlicher Bits)."""
    return bin(a ^ b).count("1")


def gray_hamming_distance(n: int, m: int) -> int:
    """Hamming-Distanz zwischen den Gray-Codes von n und m."""
    return hamming_distance(encode(n), encode(m))


def validate_gray_sequence(states: list[int]) -> bool:
    """Prüft ob alle aufeinanderfolgenden Zustände Hamming-Distanz = 1 haben.

    Für alle i: hamming_distance(states[i], states[i+1]) == 1.
    Geeignet für Sequenzen von State-IDs (z.B. GRAY_ORDER-Traversal),
    bei der benachbarte Elemente sich direkt um 1 Bit unterscheiden.
    """
    if len(states) < 2:
        return True
    return all(
        hamming_distance(states[i], states[i + 1]) == 1
        for i in range(len(states) - 1)
    )


def all_gray_pairs_valid() -> bool:
    """Verifiziert die Gray-Code-Invariante für alle 15 aufeinanderfolgenden Paare 0..14.

    Dies ist eine Kerngarantie: für n in 0..14 gilt immer
    hamming_distance(gray(n), gray(n+1)) == 1.
    """
    return all(hamming_distance(encode(n), encode(n + 1)) == 1 for n in range(15))


def suggest_gray_path(from_id: int, to_id: int) -> list[int]:
    """Gibt den kürzesten Gray-Code-Pfad zwischen zwei Q4-State-IDs zurück.

    Nutzt bit-by-bit Korrektur: jeder Schritt ändert genau 1 Bit.
    Ergebnis: Liste von State-IDs inkl. Start und Ziel.
    """
    if not (0 <= from_id <= 15 and 0 <= to_id <= 15):
        raise ValueError(f"State IDs must be in 0..15, got {from_id}, {to_id}")

    path = [from_id]
    current = from_id
    while current != to_id:
        diff = current ^ to_id
        # Flip das niedrigste gesetzte Bit
        lsb = diff & (-diff)
        current ^= lsb
        path.append(current)
    return path
