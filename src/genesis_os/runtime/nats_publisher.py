"""NATS Publisher für genesis-os Cycle-States und Q4-Frame-Übergänge.

Publiziert genesis-os Zustände via NATS/JetStream für unified-mandala Live-UI.

NATS-Subjects (Legacy — rückwärtskompatibel, bleiben erhalten):
    genesis.cycle.state      → vollständiger GenesisState (JSON)
    genesis.crep.score       → CREPScore (JSON)
    genesis.emergence.event  → EmergenceEvent (JSON)
    genesis.mirror.trigger   → Phase-Transition ausgelöst (JSON)

NATS-Subjects (Q4-Frame-Schema — neu, additiv):
    ga.frame.<4bit>          → Q4-Zustandsübergänge (ga.frame.0000..ga.frame.1111)
    ga.sigillin.<id>         → Sigillin-Events
    ga.agent.<role>          → Agent-Zustandsupdates
    ga.resonance.<metric>    → CREP-Metrik-Updates
    ga.system.health         → System-Health-Broadcasts

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

    Unterstützt das Legacy-Schema (genesis.*) und das neue Q4-Frame-Schema
    (ga.frame.*). Beide Schemas sind aktiv und rückwärtskompatibel.

    Args:
        url: NATS-Server-URL (default: ``nats://localhost:4222``).
    """

    # Legacy subjects (rückwärtskompatibel)
    SUBJECT_CYCLE = "genesis.cycle.state"
    SUBJECT_CREP = "genesis.crep.score"
    SUBJECT_EMERGE = "genesis.emergence.event"
    SUBJECT_MIRROR = "genesis.mirror.trigger"

    # Q4-Frame-Schema (additiv)
    FRAME_SUBJECT_PREFIX = "ga.frame."
    SIGILLIN_SUBJECT_PREFIX = "ga.sigillin."
    AGENT_SUBJECT_PREFIX = "ga.agent."
    RESONANCE_SUBJECT_PREFIX = "ga.resonance."
    HEALTH_SUBJECT = "ga.system.health"

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
            "gamma_legacy": float(getattr(crep, "gamma_legacy", 0.0)),
            "formula": "canonical",
        }
        await self.publish(self.SUBJECT_CREP, payload)

    async def publish_q4_frame(
        self,
        state: Any,
        payload: dict[str, Any],
        from_state: Any | None = None,
    ) -> bool:
        """Publiziert Q4-Zustandsübergang auf ga.frame.<binary>.

        Subject = f"ga.frame.{state.binary}"  z.B. "ga.frame.1011"

        Wenn from_state angegeben, wird der Gray-Code Policy Gate geprüft.
        Bei Verletzung (Hamming > 1) wird der Frame NICHT publiziert.

        Args:
            state: Q4State mit .binary Property.
            payload: Zusätzliche Daten zum Frame.
            from_state: Vorheriger Q4State für Policy-Gate-Prüfung (optional).

        Returns:
            True wenn erfolgreich publiziert, False sonst.
        """
        if from_state is not None:
            try:
                from genesis_os.runtime.policy_gate import FramePolicyGate
                gate = FramePolicyGate(strict=False)
                if not gate.check(from_state, state):
                    return False
            except Exception as exc:
                logger.debug("PolicyGate check failed: %s", exc)

        binary = getattr(state, "binary", "0000")
        subject = f"{self.FRAME_SUBJECT_PREFIX}{binary}"
        frame_payload: dict[str, Any] = {
            "q4_state": {
                "C": getattr(state, "C", 0),
                "R": getattr(state, "R", 0),
                "E": getattr(state, "E", 0),
                "P": getattr(state, "P", 0),
                "id": getattr(state, "id", 0),
                "binary": binary,
            },
            **payload,
        }
        await self.publish(subject, frame_payload)
        logger.debug("NATSPublisher: published Q4 frame to %s", subject)
        return True

    async def publish_sigillin(
        self,
        sigillin_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Publiziert Sigillin-Event auf ga.sigillin.<id>."""
        subject = f"{self.SIGILLIN_SUBJECT_PREFIX}{sigillin_id}"
        await self.publish(subject, payload)

    async def publish_agent_state(
        self,
        role: str,
        payload: dict[str, Any],
    ) -> None:
        """Publiziert Agent-Zustandsupdate auf ga.agent.<role>."""
        subject = f"{self.AGENT_SUBJECT_PREFIX}{role}"
        await self.publish(subject, payload)

    async def publish_health(self, payload: dict[str, Any]) -> None:
        """Publiziert System-Health-Broadcast auf ga.system.health."""
        await self.publish(self.HEALTH_SUBJECT, payload)

    async def close(self) -> None:
        """Schließt die NATS-Verbindung."""
        if self._nc is not None:
            import contextlib

            with contextlib.suppress(Exception):
                await self._nc.close()
            self._nc = None
