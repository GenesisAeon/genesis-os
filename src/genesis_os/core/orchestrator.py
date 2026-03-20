"""GenesisOS orchestrator: self-reflecting cycle engine.

The orchestrator ties together CREP evaluation, phase management, and the
Unified Lagrangian runtime into a single self-reflecting loop. The
self-reflection update uses the gradient of the Lagrangian with respect
to the self-reflection potential Φ(H):

.. math::
    \\Phi_{n+1}(H) = \\Phi_n(H) \\cdot \\left(1 + \\alpha \\cdot
    \\nabla_H \\mathcal{L}\\right)

where :math:`\\alpha` is the reflection learning rate and
:math:`\\nabla_H \\mathcal{L}` is computed from the CREP gradient.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from pydantic import BaseModel, Field

from genesis_os.core.crep import CREPEvaluator, CREPScore
from genesis_os.core.phase import Phase, PhaseMatrix, PhaseTransition
from genesis_os.runtime.emergence import CosmicWebSimulator, EmergenceEvent

logger = logging.getLogger(__name__)


class GenesisConfig(BaseModel):
    """Configuration for the GenesisOS orchestrator.

    Attributes:
        entropy: Initial entropy level ∈ [0.0, 1.0].
        alpha: Self-reflection learning rate.
        max_cycles: Maximum number of phase-transition cycles per run.
        transition_threshold: Default Γ threshold for phase transitions.
        resonance_coupling: Field coupling constant for resonance.
        phi_init: Initial value of the self-reflection potential Φ(H).
        seed: Random seed for reproducibility (None = non-deterministic).
    """

    entropy: float = Field(default=0.5, ge=0.0, le=1.0)
    alpha: float = Field(default=0.1, gt=0.0, le=1.0)
    max_cycles: int = Field(default=100, gt=0)
    transition_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    resonance_coupling: float = Field(default=0.5, ge=0.0, le=1.0)
    phi_init: float = Field(default=1.0, gt=0.0)
    seed: int | None = Field(default=None)


@dataclass
class GenesisState:
    """Mutable snapshot of the current GenesisOS system state.

    Attributes:
        cycle: Current cycle index.
        phase: Active phase.
        entropy: Current entropy level.
        phi: Self-reflection potential Φ(H).
        crep: Latest CREP score.
        lagrangian: Latest Lagrangian value L.
        transitions: All phase transitions recorded so far.
        metadata: Arbitrary plugin-provided data.
    """

    cycle: int = 0
    phase: Phase = Phase.INITIATION
    entropy: float = 0.5
    phi: float = 1.0
    crep: CREPScore | None = None
    lagrangian: float = 0.0
    transitions: list[PhaseTransition] = field(default_factory=list)
    emergence_events: list[EmergenceEvent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class GenesisOS:
    """Self-reflecting OS orchestrator for GenesisAeon.

    Implements the phase_transition_loop with integrated CREP evaluation,
    Unified Lagrangian computation, self-reflection updates, and live
    cosmic-web emergence simulation via :class:`CosmicWebSimulator`.

    Args:
        config: GenesisConfig instance (defaults to sane values).
        engine: Optional RuntimeEngine – created internally if not provided.
        plugins: Dictionary of named callables injected at each cycle.
        emergence_threshold: Threshold for :class:`CosmicWebSimulator` node
            emergence (default 0.3).
    """

    def __init__(
        self,
        config: GenesisConfig | None = None,
        engine: Any | None = None,
        plugins: dict[str, Callable[[GenesisState], dict[str, Any]]] | None = None,
        emergence_threshold: float = 0.3,
    ) -> None:
        self.config = config or GenesisConfig()
        self._plugins = plugins or {}
        self._crep = CREPEvaluator(learning_rate=self.config.alpha)
        self._phases = PhaseMatrix(
            thresholds=dict.fromkeys(Phase, self.config.transition_threshold)
        )
        self._state = GenesisState(
            entropy=self.config.entropy,
            phi=self.config.phi_init,
        )
        self._rng = np.random.default_rng(self.config.seed)
        self._simulator = CosmicWebSimulator(
            emergence_threshold=emergence_threshold,
            seed=self.config.seed,
        )
        # Lazy import to avoid circular dependency
        if engine is not None:
            self._engine: Any = engine
        else:
            from genesis_os.runtime.engine import RuntimeEngine

            self._engine = RuntimeEngine(config=self.config)

    @property
    def state(self) -> GenesisState:
        """Read-only access to the current system state."""
        return self._state

    @property
    def phase(self) -> Phase:
        """Currently active phase."""
        return self._phases.current_phase

    @property
    def phi(self) -> float:
        """Current self-reflection potential Φ(H)."""
        return self._state.phi

    def self_reflect(self) -> float:
        """Apply the self-reflection update to Φ(H).

        Uses the CREP gradient as a proxy for ∇_H L:

        .. math::
            \\Phi_{n+1}(H) = \\Phi_n(H) \\cdot (1 + \\alpha \\cdot \\nabla_H \\mathcal{L})

        Returns:
            Updated Φ(H) value.
        """
        grad = self._crep.gradient()
        if grad is None:
            return self._state.phi

        # Use the L2 norm of the CREP gradient as ∇_H L proxy
        grad_magnitude = float(np.linalg.norm(grad))
        phi_new = self._state.phi * (1.0 + self.config.alpha * grad_magnitude)
        # Clamp to avoid divergence
        phi_new = float(np.clip(phi_new, 0.01, 100.0))
        self._state.phi = phi_new
        logger.debug("self_reflect: Φ=%f (grad_mag=%f)", phi_new, grad_magnitude)
        return phi_new

    def _collect_plugin_state(self) -> dict[str, Any]:
        """Invoke all registered plugins and merge their state contributions."""
        merged: dict[str, Any] = {}
        for name, plugin_fn in self._plugins.items():
            try:
                result = plugin_fn(self._state)
                merged.update(result)
            except Exception:
                logger.warning("Plugin '%s' raised an exception; skipping.", name)
        return merged

    def step(self) -> GenesisState:
        """Execute a single orchestration step.

        1. Collect plugin state.
        2. Run the runtime engine.
        3. Evaluate CREP.
        4. Apply self-reflection.
        5. Attempt phase transition.
        6. Update state snapshot.

        Returns:
            Updated GenesisState.
        """
        plugin_state = self._collect_plugin_state()

        # Build composite state for engine
        composite: dict[str, Any] = {
            "entropy": self._state.entropy,
            "cycle": self._state.cycle,
            "phi": self._state.phi,
            "phase": self._state.phase.value,
            **plugin_state,
        }

        engine_result = self._engine.compute(composite)
        self._state.lagrangian = engine_result["lagrangian"]
        self._state.entropy = engine_result["entropy"]

        crep_state: dict[str, Any] = {**composite, **engine_result}
        crep = self._crep.evaluate(crep_state)
        self._state.crep = crep

        # Self-reflection
        self.self_reflect()

        # Cosmic-web emergence simulation step
        emergence_event = self._simulator.step(
            crep=crep,
            lagrangian=self._state.lagrangian,
            cycle=self._state.cycle,
        )
        if emergence_event is not None:
            self._state.emergence_events.append(emergence_event)
            logger.debug(
                "EmergenceEvent: cycle=%d nodes=%d rate=%.4f",
                emergence_event.cycle,
                emergence_event.node_count,
                emergence_event.emergence_rate,
            )

        # Phase transition attempt
        transition = self._phases.advance(crep.gamma, metadata={"cycle": self._state.cycle})
        if transition is not None:
            self._state.transitions.append(transition)
            self._state.phase = self._phases.current_phase
            logger.info(
                "Phase transition: %s → %s (Γ=%.4f, cycle=%d)",
                transition.from_phase.value,
                transition.to_phase.value,
                transition.trigger_gamma,
                transition.cycle,
            )

        self._state.cycle += 1
        self._state.metadata.update(engine_result)
        self._state.metadata.update(plugin_state)
        # Expose emergence summary in metadata
        self._state.metadata["emergence_summary"] = self._simulator.summary()
        return self._state

    def phase_transition_loop(
        self,
        max_cycles: int | None = None,
        callback: Callable[[GenesisState], bool | None] | None = None,
    ) -> Iterator[GenesisState]:
        """Run the full phase-transition loop as a generator.

        Yields the state after each step, allowing the caller to inspect or
        visualise progress in real time.

        Args:
            max_cycles: Override the config max_cycles for this run.
            callback: Optional function called with each state.  Return
                ``True`` to request early termination.

        Yields:
            GenesisState after every step.
        """
        limit = max_cycles if max_cycles is not None else self.config.max_cycles
        for _ in range(limit):
            state = self.step()
            if callback is not None:
                stop = callback(state)
                if stop is True:
                    logger.info(
                        "phase_transition_loop: early stop requested at cycle %d.",
                        state.cycle,
                    )
                    return
            yield state

    def run(
        self,
        max_cycles: int | None = None,
        callback: Callable[[GenesisState], bool | None] | None = None,
    ) -> GenesisState:
        """Run the full loop and return the final state.

        Args:
            max_cycles: Override the config max_cycles for this run.
            callback: Optional per-step callback.

        Returns:
            Final GenesisState after all cycles.
        """
        for _ in self.phase_transition_loop(max_cycles=max_cycles, callback=callback):
            pass
        return self._state

    @property
    def simulator(self) -> CosmicWebSimulator:
        """Read-only access to the internal :class:`CosmicWebSimulator`."""
        return self._simulator

    def reset(self) -> None:
        """Reset the orchestrator to its initial configuration."""
        self._crep.reset()
        self._phases.reset()
        self._simulator.reset()
        self._state = GenesisState(
            entropy=self.config.entropy,
            phi=self.config.phi_init,
        )
        if hasattr(self._engine, "reset"):
            self._engine.reset()
