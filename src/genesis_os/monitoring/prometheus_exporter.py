"""Prometheus-Metriken für genesis-os.

Unified-mandala Grafana-Dashboard kann diese importieren.

Metriken:
    genesis_entropy_current           Aktuelle Entropie H
    genesis_crep_gamma_current        Aktuelles CREP-Gamma (legacy)
    genesis_crep_gamma_canonical      Aktuelles kanonisches CREP-Gamma
    genesis_phi_current               Aktuelles Φ(H)
    genesis_lagrangian_current        Aktueller Lagrangian-Wert
    genesis_cycle_total               Gesamtzahl der Zyklen
    genesis_emergence_events_total    Gesamtanzahl Emergence Events
    genesis_tension_current           Aktuelle Tension(t) [falls Klimadaten]

Graceful Degradation: Wenn prometheus-client nicht installiert, werden
alle Methoden zu No-Ops.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Gauge, start_http_server  # type: ignore[import-untyped]

    _PROMETHEUS_AVAILABLE = True
except ImportError:
    _PROMETHEUS_AVAILABLE = False


class GenesisPrometheusExporter:
    """Prometheus-Metriken-Exporter für genesis-os.

    Args:
        port: HTTP-Port für /metrics Endpunkt (default: 9100).
    """

    def __init__(self, port: int = 9100) -> None:
        self.port = port
        self._started = False

        if _PROMETHEUS_AVAILABLE:
            self.entropy: Any = Gauge("genesis_entropy_current", "Current entropy H")
            self.gamma: Any = Gauge(
                "genesis_crep_gamma_current", "Current CREP gamma (legacy)"
            )
            self.gamma_canonical: Any = Gauge(
                "genesis_crep_gamma_canonical", "Current CREP gamma (canonical)"
            )
            self.phi: Any = Gauge("genesis_phi_current", "Current Phi(H)")
            self.lagrangian: Any = Gauge(
                "genesis_lagrangian_current", "Current Lagrangian value"
            )
            self.cycles: Any = Counter("genesis_cycle_total", "Total cycles executed")
            self.emergence: Any = Counter(
                "genesis_emergence_events_total", "Total emergence events"
            )
            self.tension: Any = Gauge("genesis_tension_current", "Current Tension(t)")

    def start(self) -> bool:
        """Startet den HTTP /metrics Endpunkt.

        Returns:
            True wenn erfolgreich gestartet, False wenn prometheus_client fehlt.
        """
        if not _PROMETHEUS_AVAILABLE:
            logger.debug("GenesisPrometheusExporter: prometheus_client not installed.")
            return False
        try:
            start_http_server(self.port)
            self._started = True
            logger.info("GenesisPrometheusExporter: listening on :%d/metrics", self.port)
            return True
        except Exception as exc:
            logger.warning("GenesisPrometheusExporter: failed to start: %s", exc)
            return False

    def update(self, state: Any, tension: float = 0.0) -> None:
        """Aktualisiert alle Metriken aus einem GenesisState.

        Args:
            state: GenesisState Objekt.
            tension: Aktuelle Tension(t) Metrik.
        """
        if not _PROMETHEUS_AVAILABLE:
            return
        try:
            self.entropy.set(float(getattr(state, "entropy", 0.0)))
            crep = getattr(state, "crep", None)
            if crep is not None:
                self.gamma.set(float(getattr(crep, "gamma", 0.0)))
                self.gamma_canonical.set(float(getattr(crep, "gamma_canonical", 0.0)))
            self.phi.set(float(getattr(state, "phi", 0.0)))
            self.lagrangian.set(float(getattr(state, "lagrangian", 0.0)))
            self.cycles.inc()
            n_emerge = len(getattr(state, "emergence_events", []))
            if n_emerge > 0:
                self.emergence.inc(n_emerge)
            self.tension.set(float(tension))
        except Exception as exc:
            logger.debug("GenesisPrometheusExporter.update: %s", exc)

    @property
    def is_available(self) -> bool:
        """True wenn prometheus_client installiert ist."""
        return _PROMETHEUS_AVAILABLE
