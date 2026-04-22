"""OPA-Bridge — Optionale Verbindung zu unified-mandala OPA-Policies.

Wenn unified-mandala OPA-Server läuft, kann genesis-os Policies abrufen.
Graceful Fallback: ohne OPA → default allow.
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
class PolicyDecision:
    """OPA-Policy-Entscheidung.

    Attributes:
        allowed: True wenn Policy erlaubt.
        reason: Begründung.
        policy_name: Name der evaluierten Policy.
    """

    allowed: bool
    reason: str
    policy_name: str


class OPABridge:
    """Verbindet genesis-os mit unified-mandala OPA-Policies.

    Args:
        opa_url: URL des OPA-Servers (default: ``http://localhost:8181``).
        timeout: HTTP-Timeout in Sekunden.
    """

    def __init__(
        self,
        opa_url: str = "http://localhost:8181",
        timeout: float = 3.0,
    ) -> None:
        self.opa_url = opa_url
        self.timeout = timeout
        self._client: object | None = None
        if _HTTPX_AVAILABLE:
            import httpx as _httpx

            self._client = _httpx.Client(timeout=timeout)

    def evaluate(
        self,
        state_data: dict[str, object],
        policy: str = "genesis/allow",
    ) -> PolicyDecision:
        """Evaluiert eine OPA-Policy für den aktuellen State.

        Args:
            state_data: State-Daten als Dict (wird als OPA ``input`` übertragen).
            policy: OPA Policy-Pfad (default: ``genesis/allow``).

        Returns:
            PolicyDecision — default ``allow=True`` wenn OPA nicht erreichbar.
        """
        if not _HTTPX_AVAILABLE or self._client is None:
            return PolicyDecision(True, "httpx not installed, default allow", policy)

        try:
            resp = self._client.post(  # type: ignore[union-attr]
                f"{self.opa_url}/v1/data/{policy}",
                json={"input": state_data},
            )
            if resp.status_code == 200:
                result = resp.json()
                # OPA /v1/data/{policy} returns {"result": <bool>} for boolean rules
                raw = result.get("result")
                allowed = bool(raw) if raw is not None else True
                return PolicyDecision(
                    allowed=allowed,
                    reason="OPA policy evaluated",
                    policy_name=policy,
                )
        except Exception as exc:
            logger.debug("OPABridge.evaluate: %s", exc)

        return PolicyDecision(True, "OPA not available, default allow", policy)

    def is_available(self) -> bool:
        """Prüft ob OPA-Server erreichbar ist."""
        if not _HTTPX_AVAILABLE or self._client is None:
            return False
        try:
            resp = self._client.get(  # type: ignore[union-attr]
                f"{self.opa_url}/health", timeout=1.0
            )
            return resp.status_code == 200
        except Exception:
            return False

    def close(self) -> None:
        """Schließt den HTTP-Client."""
        if self._client is not None:
            import contextlib

            with contextlib.suppress(Exception):
                self._client.close()  # type: ignore[union-attr]
