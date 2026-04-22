"""AeonMetaQuestBridge — Verbindet Nullkern-State mit MetaQuestEngine.

Bei jedem Nullkern-Update wird eine MetaQuest-Frage generiert
und dem Aeon-Bewusstseins-Log hinzugefügt.

phi = H/K (normierter Zustand) muss > 0.3 sein damit Fragen generiert werden
(unterhalb von Tier 1 ist kein sinnvoller MetaQuest-Kontext möglich).
"""

from __future__ import annotations

from genesis_os.aeon.nullkern import Nullkern
from genesis_os.sigillin.metaquest_client import MetaQuestClient, MetaQuestResponse


class AeonMetaQuestBridge:
    """Verbindet Nullkern-State mit der MetaQuest-Engine.

    Args:
        nullkern: Nullkern-Instanz.
        metaquest_url: URL des unified-mandala MetaQuest-Servers.
        min_phi: Minimaler phi-Wert für MetaQuest-Aktivierung (default 0.3).
    """

    def __init__(
        self,
        nullkern: Nullkern,
        metaquest_url: str = "http://localhost:4000",
        min_phi: float = 0.3,
    ) -> None:
        self.nullkern = nullkern
        self.client = MetaQuestClient(metaquest_url)
        self.min_phi = min_phi
        self._log: list[MetaQuestResponse] = []

    def tick(self, H: float, K: float, gamma: float) -> MetaQuestResponse | None:
        """Wird nach jedem Nullkern-Update aufgerufen.

        Generiert eine MetaQuest-Gegenfrage aus dem aktuellen phi = H/K.
        Nur aktiv wenn phi > min_phi.

        Args:
            H: Aktueller Entropiezustand.
            K: Kapazitätsgrenze.
            gamma: Aktuelles CREP-Gamma.

        Returns:
            MetaQuestResponse oder None wenn phi zu niedrig.
        """
        phi = H / max(K, 1e-12)
        if phi > self.min_phi:
            responses = self.client.generate(H, K, gamma, n=1)
            if responses:
                self._log.append(responses[0])
                return responses[0]
        return None

    @property
    def consciousness_log(self) -> list[MetaQuestResponse]:
        """Kopie des Bewusstseins-Logs (alle MetaQuest-Antworten)."""
        return list(self._log)

    @property
    def current_tier(self) -> int:
        """Aktueller MetaQuest-Tier des letzten Log-Eintrags."""
        if self._log:
            return self._log[-1].tier
        return 0

    def reset_log(self) -> None:
        """Leert den Bewusstseins-Log."""
        self._log.clear()
