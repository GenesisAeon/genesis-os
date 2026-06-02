"""SemanticAnchor — information-theoretic formalisation of Sigillin.

A semantic anchor is a compressed state representation that reduces
meaning-drift between asynchronous processes.

Formally:
    anchor = argmin_{A} H(State | A)  subject to |A| <= max_bits

The Sigillin in GenesisAeon ARE semantic anchors:
"CREP", "v_RIG", "Q4", "sigma_Phi" — each a compressed state.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SemanticAnchor:
    """A named, compressed representation of a collaboration state.

    Args:
        name:         Sigillin or concept name, e.g. "CREP", "v_RIG".
        state_bits:   Estimated entropy of the full state in bits.
        anchor_bits:  Compressed size of this anchor in bits.
        context:      Optional dict of associated metadata.
    """

    name: str
    state_bits: float
    anchor_bits: float
    context: dict[str, Any] = field(default_factory=dict)

    def recall_entropy(self) -> float:
        """H(State | Anchor) in bits — residual uncertainty after recall."""
        # Conditional entropy = state entropy minus information provided by anchor.
        # Anchor provides at most anchor_bits of information.
        provided = min(self.anchor_bits, self.state_bits)
        return max(0.0, self.state_bits - provided)

    def compression_ratio(self) -> float:
        """state_bits / anchor_bits — higher is better."""
        if self.anchor_bits <= 0:
            return float("inf")
        return self.state_bits / self.anchor_bits

    def drift_reduction(self, kappa: float, lambda_: float) -> float:
        """Stable drift D* = (lambda_ / kappa) * anchor_strength.

        anchor_strength = compression_ratio normalised to [0, 1]
        via tanh so that very high ratios converge smoothly.
        """
        anchor_strength = math.tanh(self.compression_ratio() / 10.0)
        return (lambda_ / kappa) * anchor_strength if kappa > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state_bits": self.state_bits,
            "anchor_bits": self.anchor_bits,
            "recall_entropy": self.recall_entropy(),
            "compression_ratio": self.compression_ratio(),
            "context": self.context,
        }


# Pre-defined anchors for the GenesisAeon core concepts
GENESIS_ANCHORS: list[SemanticAnchor] = [
    SemanticAnchor("CREP", state_bits=128.0, anchor_bits=12.0,
                   context={"domain": "tensor", "components": ["C", "R", "E", "P"]}),
    SemanticAnchor("UTAC", state_bits=96.0, anchor_bits=10.0,
                   context={"domain": "ODE", "params": ["r", "K", "sigma", "Gamma"]}),
    SemanticAnchor("v_RIG", state_bits=64.0, anchor_bits=8.0,
                   context={"value_km_s": 1352.12, "domain": "information-geometry"}),
    SemanticAnchor("sigma_Phi", state_bits=48.0, anchor_bits=6.0,
                   context={"value": 1 / 16, "domain": "frame-principle"}),
    SemanticAnchor("Q4", state_bits=80.0, anchor_bits=4.0,
                   context={"states": 16, "domain": "information-theory"}),
    SemanticAnchor("Phi_cbrt", state_bits=40.0, anchor_bits=5.0,
                   context={"value": 1.17480, "domain": "scaling"}),
]
