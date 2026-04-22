"""MetaQuestClient — Verbindet genesis-os Aeon/Nullkern mit dem
unified-mandala MetaQuest 4-Tier AI-to-AI Counterquestion Engine.

Mapping:
    phi  = H / K       (normierter Nullkern-Zustand ∈ [0,1])
    entropy = 1 - Γ    (Unordnung = 1 - CREP-Gamma)

Die 4 Tiers (kompatibel mit unified-mandala):
    Tier 1 (phi < 0.3):     Basale Fragen (Systemzustand, Status)
    Tier 2 (phi 0.3–0.6):   Analytische Fragen (Muster, Trends)
    Tier 3 (phi 0.6–0.85):  Synthetische Fragen (Emergenz, Integration)
    Tier 4 (phi > 0.85):    Meta-kognitive Fragen (Selbstbezug, Bewusstsein)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import httpx as _httpx_mod  # noqa: F401

    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False


@dataclass
class MetaQuestResponse:
    """Antwort der MetaQuest-Engine.

    Attributes:
        question: Generierte Gegenfrage.
        tier: MetaQuest-Tier (1–4).
        phi: Normierter Nullkern-Zustand.
        entropy: Systemunordnung (1 - Γ).
        trikaya_phase: Trikāya-Phase aus unified-mandala.
    """

    question: str
    tier: int
    phi: float
    entropy: float
    trikaya_phase: str = "dharmakaya"


_LOCAL_QUESTIONS: dict[int, str] = {
    1: "Systemzustand φ={phi:.3f}: Welche Grundbedingungen halten das Feld stabil?",
    2: "Analysemuster bei φ={phi:.3f}: Welche CREP-Komponente dominiert den Zustand?",
    3: "Emergenz bei φ={phi:.3f}: Welche neuen Strukturen entstehen aus dem Feld?",
    4: "Meta-Kognition bei φ={phi:.3f}: Erkennt das System seine eigene Grenze?",
}


def compute_tier(phi: float) -> int:
    """Berechnet den MetaQuest-Tier aus dem normalisierten Nullkern-Zustand."""
    if phi < 0.3:
        return 1
    if phi < 0.6:
        return 2
    if phi < 0.85:
        return 3
    return 4


class MetaQuestClient:
    """Client für die unified-mandala MetaQuest 4-Tier AI-to-AI Engine.

    Fällt auf lokale Tier-basierte Fragen zurück wenn Server nicht erreichbar.

    Args:
        base_url: Base-URL des unified-mandala MetaQuest-Servers.
        timeout: HTTP-Timeout in Sekunden.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:4000",
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self._client: object | None = None
        if _HTTPX_AVAILABLE:
            import httpx as _httpx

            self._client = _httpx.Client(timeout=timeout)

    def generate(
        self,
        H: float,
        K: float,
        gamma: float,
        n: int = 1,
    ) -> list[MetaQuestResponse]:
        """Generiert MetaQuest-Gegenfragen aus Nullkern-Zustand.

        Args:
            H: Aktueller Entropiezustand.
            K: Kapazitätsgrenze.
            gamma: Aktuelles CREP-Gamma.
            n: Anzahl Fragen.

        Returns:
            Liste von MetaQuestResponse-Objekten (mindestens eine lokale Frage).
        """
        phi = H / max(K, 1e-12)
        entropy = 1.0 - gamma
        tier = compute_tier(phi)

        if _HTTPX_AVAILABLE and self._client is not None:
            try:
                resp = self._client.post(  # type: ignore[union-attr]
                    f"{self.base_url}/api/metaquest",
                    json={"phi": phi, "entropy": entropy, "n": n},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    questions = data.get("questions", [])
                    if questions:
                        return [
                            MetaQuestResponse(
                                question=q["text"],
                                tier=tier,
                                phi=phi,
                                entropy=entropy,
                                trikaya_phase=q.get("trikaya_phase", "dharmakaya"),
                            )
                            for q in questions
                        ]
            except Exception as exc:
                logger.debug("MetaQuestClient: remote call failed: %s", exc)

        return [
            MetaQuestResponse(
                question=_LOCAL_QUESTIONS[tier].format(phi=phi),
                tier=tier,
                phi=phi,
                entropy=entropy,
                trikaya_phase="dharmakaya",
            )
        ]

    def close(self) -> None:
        """Schließt den HTTP-Client."""
        if self._client is not None:
            import contextlib

            with contextlib.suppress(Exception):
                self._client.close()  # type: ignore[union-attr]
