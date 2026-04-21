"""SemanticAgent — κ-field coupled semantic agent with β-synchronization.

Implements:
    - κ-field coupling: κ_field = Σκ_i / N
    - β-synchronization: β_sync = σ(β_agents) / mean(β_agents)
    - v_collective: collective angular momentum
    - Resonance score tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from genesis_os.core.utac_bridge import UTACBridge


@dataclass
class AgentState:
    """State snapshot for a single SemanticAgent.

    Attributes:
        kappa: κ coupling strength for this agent.
        beta: β steepness parameter.
        activation: Current UTAC activation.
        resonance_score: Cumulative resonance score.
        angular_momentum: Agent's contribution to v_collective.
        cycle: Current cycle index.
    """

    kappa: float
    beta: float
    activation: float
    resonance_score: float
    angular_momentum: float
    cycle: int


@dataclass
class CollectiveField:
    """Collective field state for a group of SemanticAgents.

    Attributes:
        kappa_field: Mean κ coupling over all agents.
        beta_sync: β synchronization index.
        v_collective: Collective angular momentum (vector sum).
        n_agents: Number of agents in the collective.
    """

    kappa_field: float
    beta_sync: float
    v_collective: float
    n_agents: int


@dataclass
class SemanticAgent:
    """κ-field coupled semantic agent.

    Each agent maintains a κ coupling strength and a β steepness parameter.
    Agents in a collective interact via their κ-fields and β-synchronization.

    Args:
        agent_id: Unique identifier for this agent.
        kappa: κ coupling strength ∈ [0, 1] (default 0.5).
        beta: β logistic steepness (default 4.5).
        theta: UTAC inflection threshold (default 0.5).
    """

    agent_id: str = "agent_0"
    kappa: float = 0.5
    beta: float = 4.5
    theta: float = 0.5
    _bridge: UTACBridge = field(default_factory=UTACBridge, init=False, repr=False)
    _cycle: int = field(default=0, init=False)
    _resonance_cumulative: float = field(default=0.0, init=False)
    _angular_history: list[float] = field(default_factory=list, init=False, repr=False)
    _state_history: list[AgentState] = field(default_factory=list, init=False, repr=False)

    def step(self, R: float, field_input: float = 0.0) -> AgentState:
        """Advance agent state by one step.

        Computes UTAC activation, updates resonance score, and tracks
        angular momentum contribution.

        Args:
            R: Normalized resource variable ∈ [0, 1].
            field_input: External κ-field input (default 0.0).

        Returns:
            AgentState snapshot.
        """
        # Effective R with κ-field coupling
        R_eff = float(np.clip(R + self.kappa * field_input, 0.0, 1.0))
        activation = UTACBridge.feldtheorie_activation(
            beta=self.beta, R=R_eff, theta=self.theta
        )
        # Angular momentum: oscillatory contribution
        angle = 2.0 * float(np.pi) * activation
        angular = float(np.cos(angle) * self.kappa)
        self._angular_history.append(angular)

        # Resonance: proximity to peak activation
        resonance = float(np.exp(-abs(activation - 0.5) * 4.0))
        self._resonance_cumulative += resonance

        state = AgentState(
            kappa=self.kappa,
            beta=self.beta,
            activation=activation,
            resonance_score=resonance,
            angular_momentum=angular,
            cycle=self._cycle,
        )
        self._state_history.append(state)
        self._cycle += 1
        return state

    @property
    def mean_resonance(self) -> float:
        """Mean resonance score over all cycles."""
        if not self._state_history:
            return 0.0
        return float(np.mean([s.resonance_score for s in self._state_history]))

    @property
    def v_angular(self) -> float:
        """Angular momentum contribution (mean of history)."""
        if not self._angular_history:
            return 0.0
        return float(np.mean(self._angular_history))

    def reset(self) -> None:
        """Reset agent to initial state."""
        self._cycle = 0
        self._resonance_cumulative = 0.0
        self._angular_history.clear()
        self._state_history.clear()

    @property
    def history(self) -> list[AgentState]:
        """Read-only history of agent states."""
        return list(self._state_history)


class AgentCollective:
    """Collective field dynamics for a group of SemanticAgents.

    Computes κ_field, β_sync, and v_collective over a set of agents.

    Args:
        agents: List of SemanticAgent instances.
    """

    def __init__(self, agents: list[SemanticAgent]) -> None:
        self.agents = list(agents)

    def compute_kappa_field(self) -> float:
        """Compute the collective κ-field as mean of individual κ values.

        κ_field = Σκ_i / N

        Returns:
            Mean κ ∈ [0, 1].
        """
        if not self.agents:
            return 0.0
        return float(np.mean([a.kappa for a in self.agents]))

    def compute_beta_sync(self) -> float:
        """Compute β synchronization index.

        β_sync = std(β_agents) / mean(β_agents)

        A low β_sync (→ 0) indicates synchronized agents.
        A high β_sync indicates dispersed β values.

        Returns:
            β_sync ≥ 0 (0 = perfectly synchronized).
        """
        if not self.agents:
            return 0.0
        betas = np.array([a.beta for a in self.agents])
        mean_beta = float(np.mean(betas))
        if mean_beta < 1e-12:
            return 0.0
        return float(np.std(betas) / mean_beta)

    def compute_v_collective(self) -> float:
        """Compute collective angular momentum v_collective.

        v_collective = |Σ angular_momentum_i|

        Returns:
            Collective angular momentum magnitude.
        """
        total = sum(a.v_angular for a in self.agents)
        return float(abs(total))

    def step_all(self, R: float) -> CollectiveField:
        """Advance all agents by one step and compute collective field.

        Args:
            R: Normalized resource variable ∈ [0, 1].

        Returns:
            CollectiveField snapshot.
        """
        kappa_field = self.compute_kappa_field()
        for agent in self.agents:
            agent.step(R=R, field_input=kappa_field)

        return CollectiveField(
            kappa_field=kappa_field,
            beta_sync=self.compute_beta_sync(),
            v_collective=self.compute_v_collective(),
            n_agents=len(self.agents),
        )

    def summary(self) -> dict[str, Any]:
        """Return a summary of the collective state."""
        return {
            "n_agents": len(self.agents),
            "kappa_field": self.compute_kappa_field(),
            "beta_sync": self.compute_beta_sync(),
            "v_collective": self.compute_v_collective(),
            "mean_resonance": float(
                np.mean([a.mean_resonance for a in self.agents]) if self.agents else 0.0
            ),
        }
