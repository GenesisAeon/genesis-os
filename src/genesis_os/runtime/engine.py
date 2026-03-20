"""Unified Lagrangian runtime engine with UTAC-Logistic and CREP evaluation.

The Unified Lagrangian for GenesisOS is:

.. math::
    \\mathcal{L} = T - V + \\Phi(H) + \\Gamma(C, R, E, P)

where:

- :math:`T = \\frac{1}{2} \\kappa R^2` is the kinetic (resonance-coupling) term
- :math:`V = \\frac{1}{2} \\eta H^2` is the entropic resistance potential
- :math:`\\Phi(H) = \\phi_0 \\ln(1 + H)` is the self-reflection potential
- :math:`\\Gamma(C,R,E,P)` is the CREP coupling term (see :mod:`genesis_os.core.crep`)

The entropy evolves according to the UTAC-Logistic equation:

.. math::
    \\frac{dH}{dt} = r H \\left(1 - \\frac{H}{K}\\right) \\tanh(\\sigma \\Gamma)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from pydantic import BaseModel

from genesis_os.core.crep import CREPEvaluator, CREPScore
from genesis_os.runtime.utac import UTACLogistic

logger = logging.getLogger(__name__)


class LagrangianResult(BaseModel):
    """Result container for a single Lagrangian computation step.

    Attributes:
        lagrangian: Total Lagrangian value L.
        kinetic: Kinetic term T.
        potential: Potential term V.
        phi: Self-reflection potential Φ(H).
        gamma: CREP coupling Γ.
        entropy: Updated entropy after UTAC step.
        crep: CREP score used in this computation.
        cycle: Cycle index.
    """

    lagrangian: float
    kinetic: float
    potential: float
    phi: float
    gamma: float
    entropy: float
    crep: CREPScore
    cycle: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary representation."""
        return {
            "lagrangian": self.lagrangian,
            "kinetic": self.kinetic,
            "potential": self.potential,
            "phi": self.phi,
            "gamma": self.gamma,
            "entropy": self.entropy,
            "cycle": self.cycle,
            "coherence": self.crep.coherence,
            "resonance": self.crep.resonance,
            "emergence": self.crep.emergence,
            "poetics": self.crep.poetics,
        }


@dataclass
class RuntimeEngine:
    """Unified Lagrangian runtime engine.

    Computes the Lagrangian at each cycle and evolves entropy via the
    UTAC-Logistic ODE. Designed to be driven by :class:`genesis_os.core.orchestrator.GenesisOS`.

    Args:
        config: GenesisConfig for initial parameters.
        kappa: Resonance kinetic coupling constant (default 0.8).
        eta: Entropic resistance coefficient (default 0.5).
        phi0: Base self-reflection potential amplitude (default 1.0).
        utac_r: UTAC logistic growth rate (default 0.3).
        utac_K: UTAC carrying capacity (default 1.0).
        utac_sigma: UTAC Γ sensitivity (default 2.0).
    """

    config: Any = None  # GenesisConfig – avoids circular import at module level
    kappa: float = 0.8
    eta: float = 0.5
    phi0: float = 1.0
    utac_r: float = 0.3
    utac_K: float = 1.0
    utac_sigma: float = 2.0
    _crep: CREPEvaluator = field(init=False)
    _utac: UTACLogistic = field(init=False)
    _cycle: int = field(default=0, init=False)
    _history: list[LagrangianResult] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self._crep = CREPEvaluator()
        self._utac = UTACLogistic(r=self.utac_r, K=self.utac_K, sigma=self.utac_sigma)

    # ------------------------------------------------------------------
    # Lagrangian components
    # ------------------------------------------------------------------

    def _kinetic(self, resonance: float) -> float:
        """T = ½κR²."""
        return 0.5 * self.kappa * resonance**2

    def _potential(self, entropy: float) -> float:
        """V = ½ηH²."""
        return 0.5 * self.eta * entropy**2

    def _phi(self, entropy: float, phi_ext: float = 1.0) -> float:
        """Φ(H) = φ₀ · ln(1 + H) · φ_ext."""
        return self.phi0 * float(np.log1p(max(entropy, 0.0))) * phi_ext

    def _lagrangian(
        self, resonance: float, entropy: float, phi: float, gamma: float
    ) -> tuple[float, float, float, float]:
        """Compute full Lagrangian L = T - V + Φ(H) + Γ.

        Returns:
            Tuple of (L, T, V, Φ).
        """
        t = self._kinetic(resonance)
        v = self._potential(entropy)
        p = self._phi(entropy, phi_ext=phi)
        lagrangian = t - v + p + gamma
        return lagrangian, t, v, p

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Perform one Lagrangian + UTAC step.

        Args:
            state: State dictionary with keys: ``entropy``, ``phi``,
                ``resonance``, ``coupling``, ``cycle``, and optionally
                ``coherence``, ``emergence``, ``poetics``.

        Returns:
            Dictionary with ``lagrangian``, ``entropy``, ``kinetic``,
            ``potential``, ``phi``, ``gamma``, ``coherence``, ``resonance``,
            ``emergence``, ``poetics``.
        """
        entropy = float(state.get("entropy", 0.5))
        phi_ext = float(state.get("phi", 1.0))
        resonance = float(state.get("resonance", state.get("coupling", 0.5)))
        cycle = int(state.get("cycle", self._cycle))

        crep = self._crep.evaluate(state)
        gamma = crep.gamma

        lagrangian, kinetic, potential, phi = self._lagrangian(resonance, entropy, phi_ext, gamma)

        # Evolve entropy via UTAC-Logistic
        new_entropy = self._utac.step(entropy, gamma)

        result = LagrangianResult(
            lagrangian=lagrangian,
            kinetic=kinetic,
            potential=potential,
            phi=phi,
            gamma=gamma,
            entropy=new_entropy,
            crep=crep,
            cycle=cycle,
        )
        self._history.append(result)
        if len(self._history) > 1000:
            self._history.pop(0)

        self._cycle += 1
        return result.to_dict()

    @property
    def history(self) -> list[LagrangianResult]:
        """Read-only history of Lagrangian results."""
        return list(self._history)

    def reset(self) -> None:
        """Reset internal state."""
        self._crep.reset()
        self._utac.reset()
        self._cycle = 0
        self._history.clear()
