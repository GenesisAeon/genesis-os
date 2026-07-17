"""SigillinSync — trilayer document synchronization checker.

Ports Feldtheorie/scripts/sigillin_sync.py.

The Sigillin protocol requires every theoretical concept to be documented
in three machine/human-readable formats:
    .yaml  — structured parameter definitions (machine-readable)
    .json  — API-serializable format
    .md    — human-readable narrative

A "gap" is a concept that is missing one or more of the three formats.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml

    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


class SigillinSync:
    """Checks and generates trilayer documentation for genesis-os concepts.

    The trilayer principle ensures every theoretical component has:
    - A YAML parameter file (machine-readable, version-controlled)
    - A JSON representation (API-accessible)
    - A Markdown description (human-readable narrative)

    Args:
        extensions: File extensions to check (default: yaml, json, md).
    """

    def __init__(
        self,
        extensions: tuple[str, ...] = ("yaml", "json", "md"),
    ) -> None:
        self.extensions = extensions

    def check_trilayer(self, base_path: Path) -> dict[str, Any]:
        """Check for trilayer completeness under base_path.

        Scans for all concept stems (files with any of the extensions)
        and reports which are missing their counterparts.

        Args:
            base_path: Root directory to scan.

        Returns:
            Dict with keys: ``gaps`` (int), ``missing`` (list[str]),
            ``complete`` (list[str]), ``total_concepts`` (int).
        """
        base = Path(base_path)
        if not base.exists():
            return {
                "gaps": 0,
                "missing": [],
                "complete": [],
                "total_concepts": 0,
                "checked_path": str(base),
            }

        # Find all stems with at least one of the required extensions
        all_files: dict[str, set[str]] = {}
        for ext in self.extensions:
            for fp in base.rglob(f"*.{ext}"):
                stem = fp.stem
                all_files.setdefault(stem, set()).add(ext)

        missing_list = []
        complete_list = []
        for stem, found_exts in all_files.items():
            missing_exts = [e for e in self.extensions if e not in found_exts]
            if missing_exts:
                missing_list.append(f"{stem}: missing {missing_exts}")
            else:
                complete_list.append(stem)

        return {
            "gaps": len(missing_list),
            "missing": missing_list,
            "complete": complete_list,
            "total_concepts": len(all_files),
            "checked_path": str(base),
        }

    def generate_trilayer(
        self,
        content: dict[str, Any],
        base_path: Path,
        concept_name: str,
    ) -> dict[str, Path]:
        """Write .yaml + .json + .md from a single content dict.

        The content dict must have a ``description`` key for the Markdown
        narrative. All other keys are written to YAML and JSON.

        Args:
            content: Dict of concept parameters and metadata.
            base_path: Directory to write the trilayer files.
            concept_name: Stem name for the output files.

        Returns:
            Dict mapping extension → Path of written file.
        """
        base = Path(base_path)
        base.mkdir(parents=True, exist_ok=True)

        written: dict[str, Path] = {}

        # YAML
        yaml_path = base / f"{concept_name}.yaml"
        if _YAML_AVAILABLE:
            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
        else:
            # Fallback: write as simple key: value text
            with open(yaml_path, "w", encoding="utf-8") as f:
                for k, v in content.items():
                    f.write(f"{k}: {v!r}\n")
        written["yaml"] = yaml_path

        # JSON
        json_path = base / f"{concept_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False, default=str)
        written["json"] = json_path

        # Markdown
        md_path = base / f"{concept_name}.md"
        description = content.get("description", f"# {concept_name}\n\nNo description provided.")
        title = concept_name.replace("_", " ").title()
        md_lines = [
            f"# {title}",
            "",
            str(description),
            "",
            "## Parameters",
            "",
        ]
        for k, v in content.items():
            if k != "description":
                md_lines.append(f"- **{k}**: `{v}`")
        md_lines.append("")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        written["md"] = md_path

        return written

    def validate_concept(
        self,
        concept_name: str,
        base_path: Path,
    ) -> dict[str, bool]:
        """Validate that all trilayer files exist for a concept.

        Args:
            concept_name: File stem to check.
            base_path: Directory to search.

        Returns:
            Dict mapping extension → exists (bool).
        """
        base = Path(base_path)
        return {
            ext: (base / f"{concept_name}.{ext}").exists()
            for ext in self.extensions
        }

    def is_complete(self, concept_name: str, base_path: Path) -> bool:
        """Return True if all trilayer files exist for the concept.

        Args:
            concept_name: File stem to check.
            base_path: Directory to search.

        Returns:
            True if all required extensions are present.
        """
        return all(self.validate_concept(concept_name, base_path).values())
