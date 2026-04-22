"""FraktalRun-Engine — Rekursive Zyklusausführung.

Implementiert den Fraktal-Zyklus-Gedanken aus fraktal-zyklus.md:
Ein Zyklus kann Sub-Zyklen erzeugen, wenn CREP-Γ > σ_Φ und die
Aktivierungsfunktion den Schwellwert überschreitet.

FraktalRun-Aktivierungsfunktion (aus unified-mandala fraktalrun/):
    σ(β·(R - Θ))  mit  β = CREP-Γ, R = H/K, Θ = 0.5

Tiefenbegrenzung durch Frame Principle:
    max_depth ≤ 1/σ_Φ = 16   (σ_Φ = 1/16)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

SIGMA_PHI: float = 1.0 / 16.0
MAX_FRACTAL_DEPTH: int = int(1.0 / SIGMA_PHI)  # = 16


def fractal_activation(
    gamma: float,
    H: float,
    K: float,
    theta: float = 0.5,
) -> float:
    """Fraktal-Aktivierungsfunktion σ(β·(R-Θ)) mit β=γ, R=H/K.

    Args:
        gamma: CREP-Gamma als Steigungsparameter β.
        H: Aktueller Entropiezustand.
        K: Kapazitätsgrenze.
        theta: Inflektionspunkt Θ (default 0.5).

    Returns:
        Sigmoid-Aktivierung ∈ (0, 1).
    """
    R = H / max(K, 1e-12)
    exponent = -gamma * (R - theta)
    return 1.0 / (1.0 + math.exp(min(max(exponent, -100.0), 100.0)))


@dataclass
class FraktalNode:
    """Knoten im FraktalRun-Baum.

    Attributes:
        depth: Rekursionstiefe.
        cycle_state: GenesisState dieses Knotens.
        gamma: CREP-Gamma dieses Knotens.
        activation: σ(β(R-Θ)) Aktivierungswert.
        children: Sub-Zyklen-Knoten.
    """

    depth: int
    cycle_state: Any
    gamma: float
    activation: float
    children: list[FraktalNode] = field(default_factory=list)


class FraktalRunEngine:
    """Rekursive Zyklus-Engine mit Frame-Principle-Tiefenbegrenzung.

    Args:
        max_depth: Maximale Rekursionstiefe (≤ 16 = 1/σ_Φ).
        sigma_phi: Frame-Principle-Stabilitätskonstante (default 1/16).
        activation_threshold: Mindest-Aktivierung für Sub-Zyklen.
    """

    def __init__(
        self,
        max_depth: int = MAX_FRACTAL_DEPTH,
        sigma_phi: float = SIGMA_PHI,
        activation_threshold: float = 0.7,
    ) -> None:
        self.max_depth = min(max_depth, MAX_FRACTAL_DEPTH)
        self.sigma_phi = sigma_phi
        self.threshold = activation_threshold
        self._tree: FraktalNode | None = None

    def run(self, genesis_os_instance: Any, initial_state: Any) -> FraktalNode:
        """Führt FraktalRun aus: Haupt-Zyklus + rekursive Sub-Zyklen.

        Args:
            genesis_os_instance: GenesisOS-Instanz für Sub-Zyklen.
            initial_state: GenesisState des Haupt-Zyklus.

        Returns:
            FraktalNode-Baum mit allen Sub-Zyklen.
        """
        root = self._build_node(genesis_os_instance, initial_state, depth=0)
        self._tree = root
        return root

    def _build_node(
        self,
        genesis_os: Any,
        state: Any,
        depth: int,
    ) -> FraktalNode:
        crep = getattr(state, "crep", None)
        gamma = float(getattr(crep, "gamma", 0.0)) if crep is not None else 0.0
        H = float(getattr(state, "entropy", 0.5))
        K = 1.0
        activation = fractal_activation(gamma, H, K)

        node = FraktalNode(
            depth=depth,
            cycle_state=state,
            gamma=gamma,
            activation=activation,
        )

        if (
            activation > self.threshold
            and gamma > self.sigma_phi
            and depth < self.max_depth
        ):
            child_state = self._run_child_cycle(genesis_os, state, depth)
            if child_state is not None:
                child_node = self._build_node(genesis_os, child_state, depth + 1)
                node.children.append(child_node)

        return node

    def _run_child_cycle(self, genesis_os: Any, parent_state: Any, depth: int) -> Any:
        """Führt einen einzelnen Sub-Zyklus aus."""
        try:
            from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

            child_config = GenesisConfig(
                entropy=float(getattr(parent_state, "entropy", 0.5))
                * (1.0 - self.sigma_phi),
                max_cycles=1,
                seed=depth,
            )
            child = GenesisOS(config=child_config)
            return child.run(max_cycles=1)
        except Exception:
            return None

    @property
    def tree(self) -> FraktalNode | None:
        """Der zuletzt berechnete FraktalRun-Baum."""
        return self._tree

    @property
    def tree_depth(self) -> int:
        """Maximale Tiefe des zuletzt berechneten Baums."""

        def _depth(node: FraktalNode) -> int:
            if not node.children:
                return node.depth
            return max(_depth(c) for c in node.children)

        return _depth(self._tree) if self._tree is not None else 0

    def collect_states(self) -> list[Any]:
        """Sammelt alle GenesisState-Objekte aus dem Baum."""

        def _collect(node: FraktalNode) -> list[Any]:
            result = [node.cycle_state]
            for child in node.children:
                result.extend(_collect(child))
            return result

        if self._tree is None:
            return []
        return _collect(self._tree)
