"""scope-resilience: Hallucination resilience mapping for LLM semantic paths.

Package 41 of the GenesisAeon ecosystem.
"""

from __future__ import annotations

from scope_resilience.domain_profile import DomainProfile, KNOWN_DOMAIN_PROFILES
from scope_resilience.hallucination_risk import HallucinationRisk
from scope_resilience.llms_txt import LLMSTxtExporter
from scope_resilience.path_monitor import PathDriftMonitor
from scope_resilience.semantic_crep import SemanticCREP, DOMAIN_CONFIG, get_domain_r
from scope_resilience.semantic_path import SemanticPath
from scope_resilience.system import ScopeResilience

__version__ = "1.0.0"
__all__ = [
    "ScopeResilience",
    "SemanticPath",
    "SemanticCREP",
    "HallucinationRisk",
    "PathDriftMonitor",
    "LLMSTxtExporter",
    "DomainProfile",
    "KNOWN_DOMAIN_PROFILES",
    "DOMAIN_CONFIG",
    "get_domain_r",
]
