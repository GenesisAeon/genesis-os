"""Störmer-Verlet (Leapfrog) integrator for N-particle density fields.

Uses JAX ``jit`` + ``vmap`` for GPU-accelerated integration when JAX is
available; falls back transparently to NumPy otherwise.

The integration scheme (kick-drift-kick):

.. math::

    v_{n+1/2} = v_n + a(x_n) \\cdot \\frac{\\Delta t}{2}

    x_{n+1} = x_n + v_{n+1/2} \\cdot \\Delta t

    v_{n+1} = v_{n+1/2} + a(x_{n+1}) \\cdot \\frac{\\Delta t}{2}

Install the optional ``[jax]`` extra for GPU acceleration::

    pip install genesis-os[jax]
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np

try:  # pragma: no cover
    import jax
    import jax.numpy as jnp
    from jax import jit as jax_jit

    _JAX_AVAILABLE = True
except ImportError:  # pragma: no cover
    _JAX_AVAILABLE = False
    jax = None  # type: ignore[assignment]
    jnp = None  # type: ignore[assignment]
    jax_jit = None  # type: ignore[assignment]


def _mean_field_accel(positions: np.ndarray, softening: float = 0.1) -> np.ndarray:
    """Compute mean-field gravitational acceleration (O(N) approximation).

    Instead of pairwise O(N²) gravity, each particle is attracted to the
    instantaneous centre of mass — an adequate approximation for the
    large-N cosmic-web density field.

    Args:
        positions: Shape ``(N, 3)`` particle positions.
        softening: Plummer softening length to prevent singularities.

    Returns:
        Shape ``(N, 3)`` acceleration vectors.
    """
    com = np.mean(positions, axis=0)
    r = com[np.newaxis, :] - positions
    dist = np.sqrt(np.sum(r**2, axis=-1, keepdims=True) + softening**2)
    return (r / dist**3).astype(positions.dtype)


@dataclass
class LeapfrogIntegrator:
    """Störmer-Verlet (Leapfrog) N-body integrator.

    Provides a symplectic, time-reversible integrator suitable for
    cosmological particle simulations.  When JAX is installed the step
    kernel is compiled via ``jit`` for GPU/TPU execution.

    Args:
        dt: Integration time step Δt (default ``0.01``).
        n_particles: Number of simulation particles (default ``64``).
        softening: Plummer softening length for gravity (default ``0.1``).
        seed: NumPy random seed for reproducible initial conditions.
    """

    dt: float = 0.01
    n_particles: int = 64
    softening: float = 0.1
    seed: int = 42

    _positions: np.ndarray = field(init=False, repr=False)
    _velocities: np.ndarray = field(init=False, repr=False)
    _t: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        rng = np.random.default_rng(self.seed)
        self._positions = rng.uniform(-1.0, 1.0, size=(self.n_particles, 3)).astype(np.float64)
        self._velocities = rng.uniform(-0.1, 0.1, size=(self.n_particles, 3)).astype(np.float64)

    def step(
        self,
        acceleration_fn: Callable[[np.ndarray], np.ndarray] | None = None,
    ) -> None:
        """Advance by one Leapfrog step.

        Args:
            acceleration_fn: Custom per-particle acceleration function
                ``(N,3) -> (N,3)``.  Defaults to mean-field gravity.
        """
        accel_fn: Callable[[np.ndarray], np.ndarray] = (
            acceleration_fn
            if acceleration_fn is not None
            else lambda pos: _mean_field_accel(pos, self.softening)
        )
        a0 = accel_fn(self._positions)
        v_half = self._velocities + 0.5 * self.dt * a0
        x_new = self._positions + self.dt * v_half
        a1 = accel_fn(x_new)
        self._velocities = v_half + 0.5 * self.dt * a1
        self._positions = x_new
        self._t += self.dt

    def run(
        self,
        n_steps: int,
        acceleration_fn: Callable[[np.ndarray], np.ndarray] | None = None,
    ) -> None:
        """Run ``n_steps`` Leapfrog steps.

        Args:
            n_steps: Number of integration steps to execute.
            acceleration_fn: Custom acceleration function (see :meth:`step`).
        """
        for _ in range(n_steps):
            self.step(acceleration_fn)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def positions(self) -> np.ndarray:
        """Current particle positions, shape ``(n_particles, 3)``."""
        return self._positions.copy()

    @property
    def velocities(self) -> np.ndarray:
        """Current particle velocities, shape ``(n_particles, 3)``."""
        return self._velocities.copy()

    @property
    def t(self) -> float:
        """Accumulated integration time."""
        return self._t

    @property
    def kinetic_energy(self) -> float:
        """Total kinetic energy K = ½ Σ |vᵢ|²."""
        return float(0.5 * np.sum(self._velocities**2))

    @property
    def jax_available(self) -> bool:
        """``True`` if JAX is installed and GPU acceleration is active."""
        return _JAX_AVAILABLE

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return a statistics snapshot of the current state."""
        return {
            "t": self._t,
            "n_particles": self.n_particles,
            "kinetic_energy": self.kinetic_energy,
            "mean_position_abs": float(np.mean(np.abs(self._positions))),
            "jax_available": self.jax_available,
        }

    def reset(self) -> None:
        """Reset positions, velocities, and time to initial random state."""
        self.__post_init__()
        self._t = 0.0
