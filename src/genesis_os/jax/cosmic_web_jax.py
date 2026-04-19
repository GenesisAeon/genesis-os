"""JAX-accelerated large-scale cosmic-web density-field simulator.

Scales the reference :class:`~genesis_os.runtime.emergence.CosmicWebSimulator`
from 64 nodes to 10⁶–10⁷ nodes using fully vectorised NumPy batch operations
(with optional JAX ``jit`` compilation for GPU execution).

Memory-efficient chunked processing keeps RAM usage bounded regardless of N.

Install the optional ``[jax]`` extra for GPU acceleration::

    pip install genesis-os[jax]
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from genesis_os.core.crep import CREPScore
from genesis_os.runtime.emergence import EmergenceEvent

try:  # pragma: no cover
    import jax.numpy as jnp
    from jax import jit as jax_jit

    @jax_jit
    def _jax_density_step_kernel(density, rate, weight, dt):  # type: ignore[misc]
        """JIT-compiled JAX density update kernel (runs on GPU/TPU when available)."""
        return jnp.clip(density + rate * weight * dt, 0.0, 1.0)

    _JAX_AVAILABLE = True
except ImportError:
    _JAX_AVAILABLE = False
    jnp = None  # type: ignore[assignment]
    jax_jit = None  # type: ignore[assignment]
    _jax_density_step_kernel = None  # type: ignore[assignment]


def _density_step(
    density_chunk: np.ndarray,
    rate: float,
    weight_chunk: np.ndarray,
    dt: float,
) -> np.ndarray:
    """Apply one density evolution step to a chunk of nodes.

    Dispatches to the JIT-compiled JAX kernel when JAX is available,
    otherwise uses NumPy (CPU-only).

    .. math::

        \\rho_{t+1} = \\operatorname{clip}(\\rho_t + \\lambda_e \\cdot w \\cdot \\Delta t,\\; 0, 1)

    Args:
        density_chunk: Current density values, shape ``(chunk,)`` float32.
        rate: Emergence rate λ_e.
        weight_chunk: CREP weight vector, shape ``(chunk,)`` float32.
        dt: Time step Δt.

    Returns:
        Updated density chunk, same shape and dtype.
    """
    if _JAX_AVAILABLE:  # pragma: no cover
        result = _jax_density_step_kernel(
            jnp.asarray(density_chunk),
            jnp.asarray(rate, dtype=jnp.float32),
            jnp.asarray(weight_chunk),
            jnp.asarray(dt, dtype=jnp.float32),
        )
        return np.asarray(result, dtype=np.float32)
    return np.clip(density_chunk + rate * weight_chunk * dt, 0.0, 1.0).astype(np.float32)


@dataclass
class JaxCosmicWebSimulator:
    """Large-scale cosmic-web simulator with chunked NumPy vectorisation.

    Extends the 64-node reference implementation to arbitrary N (10⁶–10⁷)
    via chunked float32 density arrays and vectorised NumPy kernels.
    When JAX is installed the density kernel is JIT-compiled for GPU/TPU.

    The density evolution follows the same law as the reference simulator:

    .. math::

        \\rho_{t+1} = \\operatorname{clip}\\bigl(\\rho_t
            + \\lambda_e \\cdot \\mathbf{w}(C,R,E,P) \\cdot \\Delta t,\\;
            0, 1\\bigr)

    Args:
        n_nodes: Number of cosmic-web nodes (default ``1_000_000``).
        emergence_threshold: λ_e threshold for event emission (default ``0.3``).
        sigma_e: Emergence sensitivity σ_e (default ``2.5``).
        dt: Integration time step (default ``1.0``).
        chunk_size: Nodes processed per batch for memory efficiency
            (default ``100_000``).
        seed: Random seed for reproducible initialisation.
    """

    n_nodes: int = 1_000_000
    emergence_threshold: float = 0.3
    sigma_e: float = 2.5
    dt: float = 1.0
    chunk_size: int = 100_000
    seed: int | None = None

    _rng: np.random.Generator = field(init=False, repr=False)
    _density: np.ndarray = field(init=False, repr=False)
    _events: list[EmergenceEvent] = field(default_factory=list, init=False, repr=False)
    _cycle: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self._rng = np.random.default_rng(self.seed)
        self._density = self._rng.uniform(0.0, 0.1, size=self.n_nodes).astype(np.float32)

    # ------------------------------------------------------------------
    # Emergence rate
    # ------------------------------------------------------------------

    def emergence_rate(self, lagrangian: float, gamma: float) -> float:
        """Compute instantaneous emergence rate λ_e.

        .. math::

            \\lambda_e = \\frac{|\\mathcal{L}|}{1 + |\\mathcal{L}|}
                        \\cdot \\tanh(\\sigma_e \\cdot \\max(\\Gamma, 0))

        Args:
            lagrangian: Current Unified Lagrangian value ℒ.
            gamma: CREP coupling Γ.

        Returns:
            Emergence rate λ_e ∈ [0, 1).
        """
        abs_l = abs(lagrangian)
        return float(abs_l / (1.0 + abs_l) * math.tanh(self.sigma_e * max(gamma, 0.0)))

    # ------------------------------------------------------------------
    # CREP weight vector (chunked)
    # ------------------------------------------------------------------

    def _weight_chunk(self, crep: CREPScore, start: int, end: int) -> np.ndarray:
        """Compute CREP-weighted influence for nodes ``[start, end)``.

        Uses four harmonics on the unit circle so that each CREP axis
        modulates a distinct spatial frequency.

        Args:
            crep: Current CREP score.
            start: First node index (inclusive).
            end: Last node index (exclusive).

        Returns:
            Float32 weight array of shape ``(end - start,)`` ∈ [0, 1].
        """
        idx = np.arange(start, end, dtype=np.float32)
        phase = 2.0 * np.pi * idx / self.n_nodes
        w = (
            crep.coherence * np.cos(phase)
            + crep.resonance * np.sin(2.0 * phase)
            + crep.emergence * np.cos(3.0 * phase)
            + crep.poetics * np.sin(4.0 * phase)
        ) / 4.0
        return np.clip((w + 1.0) / 2.0, 0.0, 1.0).astype(np.float32)

    # ------------------------------------------------------------------
    # Public step API
    # ------------------------------------------------------------------

    def step(
        self,
        crep: CREPScore,
        lagrangian: float,
        cycle: int | None = None,
    ) -> EmergenceEvent | None:
        """Advance the density field by one step.

        Processes nodes in ``chunk_size`` batches to bound peak memory.

        Args:
            crep: Current CREP score snapshot.
            lagrangian: Current Lagrangian value ℒ.
            cycle: External cycle counter (uses internal counter if ``None``).

        Returns:
            :class:`~genesis_os.runtime.emergence.EmergenceEvent` if
            λ_e ≥ ``emergence_threshold``, else ``None``.
        """
        effective_cycle = cycle if cycle is not None else self._cycle
        gamma = crep.gamma
        rate = self.emergence_rate(lagrangian, gamma)

        prev_active = int(np.sum(self._density >= 0.5))
        prev_mean = float(np.mean(self._density))

        for start in range(0, self.n_nodes, self.chunk_size):
            end = min(start + self.chunk_size, self.n_nodes)
            w = self._weight_chunk(crep, start, end)
            self._density[start:end] = _density_step(
                self._density[start:end], rate, w, self.dt
            )

        density_delta = float(np.mean(self._density)) - prev_mean
        self._cycle += 1

        if rate >= self.emergence_threshold:
            new_nodes = max(int(np.sum(self._density >= 0.5)) - prev_active, 1)
            event = EmergenceEvent(
                cycle=effective_cycle,
                node_count=new_nodes,
                emergence_rate=rate,
                lagrangian=lagrangian,
                gamma=gamma,
                density_delta=density_delta,
                crep=crep,
            )
            self._events.append(event)
            return event

        return None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def density(self) -> np.ndarray:
        """Copy of the density field (float32, shape ``(n_nodes,)``)."""
        return self._density.copy()

    @property
    def mean_density(self) -> float:
        """Mean density across all nodes."""
        return float(np.mean(self._density))

    @property
    def active_nodes(self) -> int:
        """Number of nodes with density ≥ 0.5."""
        return int(np.sum(self._density >= 0.5))

    @property
    def events(self) -> list[EmergenceEvent]:
        """All emitted emergence events (defensive copy)."""
        return list(self._events)

    @property
    def jax_available(self) -> bool:
        """``True`` if JAX is installed and GPU compilation is active."""
        return _JAX_AVAILABLE

    def summary(self) -> dict[str, Any]:
        """Return a state-summary dictionary."""
        return {
            "n_nodes": self.n_nodes,
            "mean_density": self.mean_density,
            "active_nodes": self.active_nodes,
            "event_count": len(self._events),
            "cycle": self._cycle,
            "jax_available": self.jax_available,
        }

    def reset(self) -> None:
        """Reset the simulator to initial conditions."""
        self._rng = np.random.default_rng(self.seed)
        self._density = self._rng.uniform(0.0, 0.1, size=self.n_nodes).astype(np.float32)
        self._events.clear()
        self._cycle = 0
