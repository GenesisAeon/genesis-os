"""DualDetector — Vereint genesis-os Phase-Transition-Loop (deterministisch)
mit unified-mandala CollapseDetector (stochastisch, SDE).

Führt beide Detektoren parallel aus und gibt einen vereinten Status zurück.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from genesis_os.core.crep import CREPScore
from genesis_os.core.utac_stoch_bridge import SIGMA_PHI, euler_maruyama_step
from genesis_os.mirror.tension_metric import (
    CRITICAL_TENSION_THRESHOLD,
    regenerative_noise_damping,
)


@dataclass
class DualDetectorResult:
    """Vereintes Ergebnis beider Detektoren.

    Attributes:
        deterministic_stable: ODE-Fixpunkt-Stabilität (H ≈ H*).
        stochastic_collapse_risk: P(collapse) aus Monte-Carlo-SDE [0,1].
        tension: Aktuelle Tension(t).
        mirror_triggered: Tension > kritischer Schwellwert.
        recommendation: ``"continue"`` | ``"monitor"`` | ``"halt"``.
    """

    deterministic_stable: bool
    stochastic_collapse_risk: float
    tension: float
    mirror_triggered: bool
    recommendation: str


class DualDetector:
    """Vereinigt deterministische ODE-Fixpunkt-Analyse mit stochastischer
    Monte-Carlo-Collapse-Wahrscheinlichkeit.

    Args:
        r: Wachstumsrate des UTAC-ODE/SDE.
        K: Kapazitätsgrenze.
        sigma: Kopplungsstärke tanh(σ·Γ).
        n_sde_runs: Anzahl Monte-Carlo-Pfade für stochastische Analyse.
        regenerative: Aktiviert 87.2× neuromorphisches Rauschen-Dämpfung.
        seed: Zufallsseed für Reproduzierbarkeit.
    """

    def __init__(
        self,
        r: float = 0.12,
        K: float = 1.0,
        sigma: float = 2.2,
        n_sde_runs: int = 100,
        regenerative: bool = False,
        seed: int | None = None,
    ) -> None:
        self.r = r
        self.K = K
        self.sigma = sigma
        self.n_sde_runs = n_sde_runs
        self.regenerative = regenerative
        self._rng = np.random.default_rng(seed)
        self.eta = regenerative_noise_damping(
            float(np.sqrt(SIGMA_PHI)), regenerative=regenerative
        )

    def detect(
        self,
        H: float,
        crep: CREPScore,
        tension: float = 0.0,
    ) -> DualDetectorResult:
        """Führt beide Detektoren aus und gibt vereinten Status zurück.

        Args:
            H: Aktueller Entropiezustand.
            crep: Aktueller CREP-Score.
            tension: Aktuelle Tension-Metrik.

        Returns:
            DualDetectorResult mit kombinierter Bewertung.
        """
        # Deterministisch: Fixpunkt H* = K · tanh(σ · Γ)
        h_star = self.K * float(np.tanh(self.sigma * crep.gamma))
        det_stable = abs(H - h_star) < 0.1 * self.K

        # Stochastisch: Monte-Carlo Collapse-Wahrscheinlichkeit
        collapses = 0
        for _ in range(self.n_sde_runs):
            x = H
            for _ in range(50):
                x = euler_maruyama_step(
                    x,
                    self.r,
                    self.K,
                    self.sigma,
                    crep.gamma,
                    dt=0.01,
                    eta=self.eta,
                    rng=self._rng,
                )
            if x < 0.05 * self.K:
                collapses += 1
        collapse_risk = collapses / max(self.n_sde_runs, 1)

        # Mirror: Tension > kritischer Schwellwert
        mirror_triggered = tension > CRITICAL_TENSION_THRESHOLD

        # Empfehlung
        if collapse_risk > 0.5 or mirror_triggered:
            rec = "halt"
        elif collapse_risk > 0.2 or tension > CRITICAL_TENSION_THRESHOLD * 0.7:
            rec = "monitor"
        else:
            rec = "continue"

        return DualDetectorResult(
            deterministic_stable=det_stable,
            stochastic_collapse_risk=collapse_risk,
            tension=tension,
            mirror_triggered=mirror_triggered,
            recommendation=rec,
        )
