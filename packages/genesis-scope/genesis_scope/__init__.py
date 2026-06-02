"""genesis-scope: Semantic coordinate system for Human-AI collaboration.

Two asynchronous process types need an explicit shared geometry to remain coherent:
  - Human:  integrates temporally — meaning emerges through ordered experience over time
  - LLM:    navigates atemporally — collapses probability space in a single step

The scope package externalises this geometry as executable code.

Core components:
  SemanticAnchor      — information-theoretic formalisation of Sigillin
  DriftModel          — ODE for semantic drift in collaboration space
  CollaborationCREP   — CREP tensor reinterpreted for session coherence
  SessionTracker      — trajectory through (tau_A, tau_H, Sigma) coordinates
  GenesisScope        — Diamond interface, orchestrates all components
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "GenesisAeon — Johann Römer × MOR Research Collective"
__license__ = "GPL-3.0-or-later"

from genesis_scope.semantic_anchor import SemanticAnchor
from genesis_scope.drift_model import DriftModel
from genesis_scope.crep_collaboration import CollaborationCREP
from genesis_scope.session_tracker import SessionTracker
from genesis_scope.system import GenesisScope

__all__ = [
    "DriftModel",
    "CollaborationCREP",
    "GenesisScope",
    "SemanticAnchor",
    "SessionTracker",
    "__version__",
]
