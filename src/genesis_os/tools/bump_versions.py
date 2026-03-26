#!/usr/bin/env python3
"""GenesisAeon Version Bump Tool.

Bumps version strings in pyproject.toml (and __init__.py where present)
across all GenesisAeon sibling repositories.

Usage::

    uv run python -m genesis_os.tools.bump_versions 0.3.0
    uv run python -m genesis_os.tools.bump_versions          # defaults to 0.2.0
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPOS: list[str] = [
    "genesis-os",
    "aeon-ai",
    "Feldtheorie",
    "unified-mandala",
    "gemeinwohl",
    "worldview",
    "universums-sim",
    "cosmic-web",
    "mirror-machine",
    "climate-dashboard",
    "sonification",
    "mandala-visualize",
    "utac-core",
    "sigillin",
    "fieldtheory",
    "cosmic-moment",
    "medium-modulation",
    "entropy-table",
    "entropy-governance",
    "implosive-genesis",
    "advanced-weighting-systems",
    "diamond-setup",
    "unified-mandala-Demo",
]

VERSION_RE = re.compile(r'(version\s*=\s*")[^"]+(")')
INIT_VERSION_RE = re.compile(r'(__version__\s*=\s*")[^"]+(")')


def bump_repo(repo_path: Path, new_version: str) -> bool:
    """Bump version in a single repository. Returns True if any file was changed."""
    changed = False

    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        new_content = VERSION_RE.sub(rf"\g<1>{new_version}\g<2>", content, count=1)
        if new_content != content:
            pyproject.write_text(new_content, encoding="utf-8")
            changed = True

    # Also update __version__ in src/<pkg>/__init__.py if present
    for init_py in repo_path.glob("src/**/__init__.py"):
        content = init_py.read_text(encoding="utf-8")
        new_content = INIT_VERSION_RE.sub(rf"\g<1>{new_version}\g<2>", content)
        if new_content != content:
            init_py.write_text(new_content, encoding="utf-8")
            changed = True

    return changed


def main() -> None:
    new_version = sys.argv[1] if len(sys.argv) > 1 else "0.2.0"

    if not re.fullmatch(r"\d+\.\d+\.\d+", new_version):
        print(f"ERROR: '{new_version}' is not a valid semver (e.g. 0.3.0)")
        sys.exit(1)

    base = Path(__file__).resolve().parents[5]  # …/genesis-os/../../ sibling root
    print(f"Bumping all GenesisAeon repos to v{new_version}")
    print(f"Searching under: {base}\n")

    updated: list[str] = []
    skipped: list[str] = []

    for repo_name in REPOS:
        repo_path = base / repo_name
        if not repo_path.is_dir():
            skipped.append(repo_name)
            continue
        if bump_repo(repo_path, new_version):
            print(f"  v{new_version}  {repo_name}")
            updated.append(repo_name)
        else:
            skipped.append(repo_name)

    print(f"\nUpdated : {len(updated)} repos")
    if skipped:
        print(f"Skipped : {len(skipped)} (not found or already at target version)")
    print("\nNext: commit each repo, push, and trigger releases via")
    print("  git tag vX.Y.Z && git push --tags")


if __name__ == "__main__":
    main()
