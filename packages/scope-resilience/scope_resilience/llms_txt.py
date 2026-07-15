"""llms.txt exporter — machine-readable semantic map for LLM context injection.

Analogous to robots.txt: a structured overview of a knowledge space
formatted for LLM consumption.
"""

from __future__ import annotations

from scope_resilience.semantic_path import SemanticPath


class LLMSTxtExporter:
    """Export a SemanticPath as an llms.txt-compatible string."""

    def export(self, path: SemanticPath) -> str:
        lines = [
            f"# GenesisAeon Semantic Map — {path.topic}",
            f"# Domain: {path.domain}",
            f"# Resilience: rho_sem={path.rho_sem:.3f} ({path.risk_level})",
            f"# CREP: Gamma={path.gamma_sem:.3f} "
            f"(C={path.crep_components.get('C', 0):.2f}, "
            f"R={path.crep_components.get('R', 0):.2f}, "
            f"E={path.crep_components.get('E', 0):.2f}, "
            f"P={path.crep_components.get('P', 0):.2f})",
            "",
            "## Core Semantic Path",
        ]
        for i, sig_id in enumerate(path.sigillin_ids, start=1):
            lines.append(f"  {i}. [Sigillin:{sig_id}]")
        lines += ["", "## Q4 Transitions"]
        for src, dst in path.q4_transitions:
            lines.append(f"  {src} -> {dst}")
        lines += ["", "## Grounding Recommendations"]
        for rec in path.grounding_recommendations:
            lines.append(f"  - {rec}")
        return "\n".join(lines)
