"""CREP TypeScript Bridge — Python-Client für unified-mandala @mandala/crep.

Ruft den unified-mandala CREP-Bridge REST-Endpunkt auf und ermöglicht
Zugang zur Trikāya-Klassifikation sowie governance-orientierten CREP-Metriken.

Graceful Fallback: Wenn der unified-mandala Server nicht erreichbar ist,
wird der lokale kanonische CREP-Wert zurückgegeben ohne Fehler.
"""

from __future__ import annotations

import logging

from genesis_os.core.crep import CREPScore

logger = logging.getLogger(__name__)

try:
    import httpx as _httpx_mod  # noqa: F401

    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False


class CREPTypeScriptBridge:
    """Ruft den unified-mandala @mandala/crep TypeScript-Endpunkt auf.

    Bietet damit Zugang zur Trikāya-Klassifikation und governance-
    orientierten CREP-Metriken aus unified-mandala.

    Args:
        base_url: Basis-URL des unified-mandala CREP-Bridge Servers.
        timeout: HTTP-Timeout in Sekunden.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:4099",
        timeout: float = 5.0,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self._client: object | None = None
        if _HTTPX_AVAILABLE:
            import httpx as _httpx

            self._client = _httpx.Client(timeout=timeout)

    def evaluate_remote(self, crep: CREPScore) -> dict[str, object]:
        """CREP-Score via unified-mandala Brücke evaluieren.

        Args:
            crep: Lokaler CREPScore — wird an den Remote-Endpunkt gesendet.

        Returns:
            Dict mit ``gamma``, ``trikaya_phase``, und weiteren UM-Metriken.
            Fällt auf lokalen kanonischen Gamma zurück wenn Server nicht erreichbar.
        """
        if not _HTTPX_AVAILABLE or self._client is None:
            return self._local_fallback(crep)

        try:

            payload = {
                "C": crep.coherence,
                "R": crep.resonance,
                "E": crep.emergence,
                "P": crep.poetics,
            }
            resp = self._client.post(  # type: ignore[union-attr]
                f"{self.base_url}/crep/evaluate", json=payload
            )
            resp.raise_for_status()
            return dict(resp.json())
        except Exception as exc:
            logger.debug("CREPTypeScriptBridge: remote call failed: %s", exc)
            return self._local_fallback(crep)

    def is_available(self) -> bool:
        """Prüft ob der unified-mandala CREP-Bridge erreichbar ist."""
        if not _HTTPX_AVAILABLE or self._client is None:
            return False
        try:

            resp = self._client.get(  # type: ignore[union-attr]
                f"{self.base_url}/crep/health", timeout=1.0
            )
            return resp.status_code == 200
        except Exception:
            return False

    def _local_fallback(self, crep: CREPScore) -> dict[str, object]:
        """Lokaler Fallback: kanonisches Gamma + Basis-Trikāya-Klassifikation."""
        gamma = crep.gamma
        trikaya = self._classify_trikaya(gamma)
        return {
            "gamma": gamma,
            "formula": "geometric_mean",
            "trikaya_phase": trikaya,
            "source": "local_fallback",
            "C": crep.coherence,
            "R": crep.resonance,
            "E": crep.emergence,
            "P": crep.poetics,
        }

    @staticmethod
    def _classify_trikaya(gamma: float) -> str:
        """Bestimmt Trikāya-Phase aus CREP-Gamma."""
        if gamma > 0.75:
            return "nirmanakaya"
        if gamma > 0.45:
            return "sambhogakaya"
        return "dharmakaya"

    def close(self) -> None:
        """Schließt den HTTP-Client."""
        if self._client is not None:
            import contextlib

            with contextlib.suppress(Exception):
                self._client.close()  # type: ignore[union-attr]
