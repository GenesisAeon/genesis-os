"""NATS Publisher für genesis-os Cycle-States.

Publiziert genesis-os Zustände via NATS/JetStream für unified-mandala Live-UI.

NATS-Subjects (Konvention):
    genesis.cycle.state      → vollständiger GenesisState (JSON)
    genesis.crep.score       → CREPScore (JSON)
    genesis.emergence.event  → EmergenceEvent (JSON)
    genesis.mirror.trigger   → Phase-Transition ausgelöst (JSON)

Graceful Degradation: Wenn nats-py nicht installiert oder Server nicht
erreichbar, werden alle publish-Aufrufe stillschweigend ignoriert.
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import nats  # type: ignore[import-untyped]

    _NATS_AVAILABLE = True
except ImportError:
    _NATS_AVAILABLE = False


class NATSPublisher:
    """Publiziert genesis-os Zustände via NATS/JetStream.

    Args:
        url: NATS-Server-URL (default: ``nats://localhost:4222``).
    """

    SUBJECT_CYCLE = "genesis.cycle.state"
    SUBJECT_CREP = "genesis.crep.score"
    SUBJECT_EMERGE = "genesis.emergence.event"
    SUBJECT_MIRROR = "genesis.mirror.trigger"

    def __init__(self, url: str = "nats://localhost:4222") -> None:
        self.url = url
        self._nc: Any = None
        self._available = _NATS_AVAILABLE

    async def connect(self) -> bool:
        """Verbindet mit NATS-Server.

        Returns:
            True wenn Verbindung erfolgreich, False sonst.
        """
        if not self._available:
            return False
        try:
            self._nc = await nats.connect(self.url)
            logger.info("NATSPublisher: connected to %s", self.url)
            return True
        except Exception as exc:
            logger.debug("NATSPublisher: connect failed: %s", exc)
            return False

    async def publish(self, subject: str, data: dict[str, Any]) -> None:
        """Publiziert ein JSON-Paket auf einem NATS-Subject."""
        if self._nc is not None:
            try:
                if hasattr(self._nc, "is_connected") and self._nc.is_connected:
                    await self._nc.publish(subject, json.dumps(data).encode())
            except Exception as exc:
                logger.debug("NATSPublisher.publish: %s", exc)

    async def publish_cycle_state(self, state: Any) -> None:
        """Publiziert GenesisState auf genesis.cycle.state."""
        payload: dict[str, Any] = {
            "cycle": getattr(state, "cycle", 0),
            "phase": (
                state.phase.value
                if hasattr(state.phase, "value")
                else str(getattr(state, "phase", "unknown"))
            ),
            "entropy": float(getattr(state, "entropy", 0.0)),
            "phi": float(getattr(state, "phi", 0.0)),
            "lagrangian": float(getattr(state, "lagrangian", 0.0)),
            "gamma": (
                float(state.crep.gamma) if getattr(state, "crep", None) is not None else 0.0
            ),
            "emergence_count": len(getattr(state, "emergence_events", [])),
        }
        await self.publish(self.SUBJECT_CYCLE, payload)

    async def publish_crep_score(self, crep: Any) -> None:
        """Publiziert CREPScore auf genesis.crep.score."""
        payload = {
            "C": float(getattr(crep, "coherence", 0.0)),
            "R": float(getattr(crep, "resonance", 0.0)),
            "E": float(getattr(crep, "emergence", 0.0)),
            "P": float(getattr(crep, "poetics", 0.0)),
            "gamma": float(getattr(crep, "gamma", 0.0)),
            "gamma_canonical": float(getattr(crep, "gamma_canonical", 0.0)),
            "formula": "legacy",
        }
        await self.publish(self.SUBJECT_CREP, payload)

    async def close(self) -> None:
        """Schließt die NATS-Verbindung."""
        if self._nc is not None:
            import contextlib

            with contextlib.suppress(Exception):
                await self._nc.close()
            self._nc = None
