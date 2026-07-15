"""GenesisAeon package registry.

Maps package IDs to metadata.  Used by genesis-os to discover and
describe ecosystem packages.  Packages 40 and 41 introduce the 6th
Diamond method get_resilience_state().
"""

from __future__ import annotations

from typing import Any

PACKAGE_REGISTRY: dict[int, dict[str, Any]] = {
    40: {
        "name": "resilience-core",
        "module": "resilience_core",
        "class": "ResilienceCore",
        "domain": "meta-dynamics",
        "scale": "cross-domain",
        "introduces": "6th Diamond method: get_resilience_state()",
        "zenodo": "pending",
        "status": "beta",
    },
    41: {
        "name": "scope-resilience",
        "module": "scope_resilience",
        "class": "ScopeResilience",
        "domain": "semantic-ai",
        "scale": "llm-path",
        "depends_on": ["genesis-scope>=1.0.0", "resilience-core>=1.0.0"],
        "introduces": "Hallucination resilience Ρ_sem for LLM semantic paths",
        "zenodo": "pending",
        "status": "beta",
    },
}
