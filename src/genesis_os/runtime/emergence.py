"""Live cosmic-web emergence simulation with CREP-driven node emergence.

The :class:`CosmicWebSimulator` integrates the Unified Lagrangian with a
field-theoretic cosmological potential and tracks node emergence events in
real time via the CREP + UTAC-Logistic feedback loop.

The emergence rate is defined as:

.. math::

    \\lambda_e = f(\\mathcal{L}, \\Gamma) =
    \\frac{|\\mathcal{L}|}{1 + |\\mathcal{L}|} \\cdot \\tanh(\\sigma_e \\cdot \\Gamma)

where :math:`\\mathcal{L}` is the current Unified Lagrangian value,
:math:`\\Gamma` is the CREP coupling term, and :math:`\\sigma_e` is the
emergence sensitivity constant.

A new :class:`EmergenceEvent` is emitted whenever :math:`\\lambda_e` exceeds
the configured ``emergence_threshold``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from genesis_os.core.crep import CREPScore


@dataclass(frozen=True)
class EmergenceEvent:
    """Immutable record of a single node-emergence event.

    Attributes:
        cycle: Orchestrator cycle index at which the event occurred.
        node_count: Number of newly emerged cosmic-web nodes.
        emergence_rate: Computed :math:`\\lambda_e` value.
        lagrangian: Lagrangian value :math:`\\mathcal{L}` at the event.
        gamma: CREP coupling value :math:`\\Gamma` at the event.
        density_delta: Change in mean node density triggered by emergence.
        crep: CREPScore snapshot at the event.
    """

    cycle: int
    node_count: int
    emergence_rate: float
    lagrangian: float
    gamma: float
    density_delta: float
    crep: CREPScore

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict representation suitable for JSON serialization."""
        return {
            "cycle": self.cycle,
            "node_count": self.node_count,
            "emergence_rate": self.emergence_rate,
            "lagrangian": self.lagrangian,
            "gamma": self.gamma,
            "density_delta": self.density_delta,
            "coherence": self.crep.coherence,
            "resonance": self.crep.resonance,
            "emergence": self.crep.emergence,
            "poetics": self.crep.poetics,
        }


@dataclass
class CosmicWebSimulator:
    """Live cosmic-web emergence simulator.

    Maintains an N-node density field that evolves according to the Unified
    Lagrangian and emits :class:`EmergenceEvent` objects when emergence
    threshold is crossed.

    The density field update rule is:

    .. math::

        \\rho_{t+1} = \\rho_t + \\lambda_e \\cdot
        \\mathbf{w}(C, R, E, P) \\cdot \\Delta t

    where :math:`\\mathbf{w}` is the CREP-weighted influence vector.

    Args:
        n_nodes: Number of cosmic-web nodes (default 64).
        emergence_threshold: :math:`\\lambda_e` threshold for event emission
            (default 0.3).
        sigma_e: Emergence sensitivity :math:`\\sigma_e` (default 2.5).
        dt: Integration time step (default 1.0).
        seed: Random seed for reproducibility.
    """

    n_nodes: int = 64
    emergence_threshold: float = 0.3
    sigma_e: float = 2.5
    dt: float = 1.0
    seed: int | None = None

    _rng: np.random.Generator = field(init=False, repr=False)
    _density: np.ndarray = field(init=False, repr=False)
    _events: list[EmergenceEvent] = field(default_factory=list, init=False, repr=False)
    _cycle: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self._rng = np.random.default_rng(self.seed)
        # Initialise node densities as small random values ~ U(0, 0.1)
        self._density = self._rng.uniform(0.0, 0.1, size=self.n_nodes)

    # ------------------------------------------------------------------
    # Emergence rate
    # ------------------------------------------------------------------

    def emergence_rate(self, lagrangian: float, gamma: float) -> float:
        """Compute the instantaneous emergence rate :math:`\\lambda_e`.

        .. math::

            \\lambda_e = \\frac{|\\mathcal{L}|}{1 + |\\mathcal{L}|}
                        \\cdot \\tanh(\\sigma_e \\cdot \\Gamma)

        Args:
            lagrangian: Current Unified Lagrangian value.
            gamma: CREP coupling value :math:`\\Gamma`.

        Returns:
            Emergence rate :math:`\\lambda_e \\in [0, 1)`.
        """
        abs_l = abs(lagrangian)
        lagrangian_factor = abs_l / (1.0 + abs_l)
        coupling_factor = math.tanh(self.sigma_e * max(gamma, 0.0))
        return float(lagrangian_factor * coupling_factor)

    # ------------------------------------------------------------------
    # Density update
    # ------------------------------------------------------------------

    def _crep_weight_vector(self, crep: CREPScore) -> np.ndarray:
        """Build the CREP-weighted influence vector for density updates.

        Maps the four CREP axes (C, R, E, P) onto an N-dimensional influence
        vector via a sinusoidal basis, ensuring smooth spatial variation.

        Args:
            crep: Current CREP score.

        Returns:
            Shape-(n_nodes,) influence vector with values in [0, 1].
        """
        idx = np.arange(self.n_nodes, dtype=float)
        # Each CREP axis modulates a different harmonic
        w = (
            crep.coherence * np.cos(2.0 * np.pi * idx / self.n_nodes)
            + crep.resonance * np.sin(4.0 * np.pi * idx / self.n_nodes)
            + crep.emergence * np.cos(6.0 * np.pi * idx / self.n_nodes)
            + crep.poetics * np.sin(8.0 * np.pi * idx / self.n_nodes)
        ) / 4.0
        # Normalise to [0, 1]
        w_shifted = (w + 1.0) / 2.0
        return np.clip(w_shifted, 0.0, 1.0).astype(float)

    def _count_new_nodes(self, prev_density: np.ndarray) -> int:
        """Count nodes that crossed the 0.5 emergence threshold in this step.

        Args:
            prev_density: Density values before the update.

        Returns:
            Number of newly active nodes.
        """
        return int(np.sum((self._density >= 0.5) & (prev_density < 0.5)))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def step(
        self,
        crep: CREPScore,
        lagrangian: float,
        cycle: int | None = None,
    ) -> EmergenceEvent | None:
        """Advance the cosmic-web simulation by one step.

        Updates the node density field and emits an :class:`EmergenceEvent`
        if the emergence rate exceeds the configured threshold.

        Args:
            crep: Current CREP score snapshot.
            lagrangian: Current Lagrangian value :math:`\\mathcal{L}`.
            cycle: External cycle counter (uses internal counter if None).

        Returns:
            :class:`EmergenceEvent` if emergence threshold is exceeded,
            else ``None``.
        """
        effective_cycle = cycle if cycle is not None else self._cycle
        gamma = crep.gamma
        rate = self.emergence_rate(lagrangian, gamma)

        prev_density = self._density.copy()
        weight_vector = self._crep_weight_vector(crep)

        # Density evolution: ρ_{t+1} = ρ_t + λ_e · w · Δt
        delta = rate * weight_vector * self.dt
        self._density = np.clip(self._density + delta, 0.0, 1.0)

        density_delta = float(np.mean(self._density) - np.mean(prev_density))
        self._cycle += 1

        if rate >= self.emergence_threshold:
            new_nodes = self._count_new_nodes(prev_density)
            event = EmergenceEvent(
                cycle=effective_cycle,
                node_count=max(new_nodes, 1),  # at least 1 node per event
                emergence_rate=rate,
                lagrangian=lagrangian,
                gamma=gamma,
                density_delta=density_delta,
                crep=crep,
            )
            self._events.append(event)
            return event

        return None

    @property
    def density(self) -> np.ndarray:
        """Read-only view of the current node density field."""
        return self._density.copy()  # type: ignore[no-any-return]

    @property
    def mean_density(self) -> float:
        """Mean node density across all cosmic-web nodes."""
        return float(np.mean(self._density))

    @property
    def active_nodes(self) -> int:
        """Number of nodes with density ≥ 0.5 (considered active/emerged)."""
        return int(np.sum(self._density >= 0.5))

    @property
    def events(self) -> list[EmergenceEvent]:
        """Read-only list of all emitted emergence events."""
        return list(self._events)

    @property
    def event_count(self) -> int:
        """Total number of emergence events emitted so far."""
        return len(self._events)

    def reset(self) -> None:
        """Reset the simulator to its initial state."""
        self._rng = np.random.default_rng(self.seed)
        self._density = self._rng.uniform(0.0, 0.1, size=self.n_nodes)
        self._events.clear()
        self._cycle = 0

    def summary(self) -> dict[str, Any]:
        """Return a summary dictionary of the current simulator state.

        Returns:
            Dictionary with keys: ``mean_density``, ``active_nodes``,
            ``event_count``, ``n_nodes``, ``emergence_threshold``.
        """
        return {
            "mean_density": self.mean_density,
            "active_nodes": self.active_nodes,
            "event_count": self.event_count,
            "n_nodes": self.n_nodes,
            "emergence_threshold": self.emergence_threshold,
            "cycle": self._cycle,
        }
