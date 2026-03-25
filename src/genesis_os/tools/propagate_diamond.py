#!/usr/bin/env python3
"""GenesisAeon Diamond-Propagation.

Propagates CI/Release/Quickstart templates to all GenesisAeon repositories.

Usage::

    uv run python -m genesis_os.tools.propagate_diamond
"""
from __future__ import annotations

import subprocess
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

TEMPLATE_FILES: dict[str, str] = {
    ".github/workflows/ci.yml": "ci.yml",
    ".github/workflows/release.yml": "release.yml",
    "README_QUICKSTART.md": "README_QUICKSTART.md",
}

TEMPLATES_DIR: Path = Path(__file__).parent / "templates"
ORG: str = "GenesisAeon"
BRANCH: str = "feat/diamond-propagation"
COMMIT_MSG: str = (
    "chore(diamond): propagate CI/Release/Quickstart templates "
    "from diamond-setup v0.3.0"
)


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    """Run a shell command, raising CalledProcessError on non-zero exit."""
    subprocess.run(cmd, cwd=cwd, check=True, text=True)  # noqa: S603


def _copy_templates(repo_path: Path) -> None:
    """Copy all template files into *repo_path*, creating parent dirs as needed."""
    for target, source in TEMPLATE_FILES.items():
        dst = repo_path / target
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text((TEMPLATES_DIR / source).read_text())


def _merge_pyproject(repo_path: Path, repo: str) -> None:
    """Append ``[project.urls]`` + Zenodo placeholder to pyproject.toml if absent."""
    pyproject = repo_path / "pyproject.toml"
    if not pyproject.exists():
        return
    content = pyproject.read_text()
    if "project.urls" in content:
        return
    addition = (
        "\n# === Diamond-Propagation: added project.urls & Zenodo ===\n"
        "[project.urls]\n"
        f'Homepage = "https://github.com/{ORG}/{repo}"\n'
        f'Documentation = "https://genesisaeon.github.io/{repo}"\n'
        'Zenodo = "https://doi.org/10.5281/zenodo.XXXXXXXX"  # <- enter your DOI\n'
    )
    pyproject.write_text(content + addition)


def propagate(repo: str, base_dir: Path) -> None:
    """Clone/pull *repo*, copy templates, commit, and push to ``feat/diamond-propagation``."""
    print(f"Propagating to {repo}...")
    repo_path = base_dir / repo

    if repo_path.exists():
        _run(["git", "pull"], cwd=repo_path)
    else:
        _run(["git", "clone", f"https://github.com/{ORG}/{repo}.git", str(repo_path)])

    _copy_templates(repo_path)
    _merge_pyproject(repo_path, repo)

    _run(["git", "add", "."], cwd=repo_path)
    _run(["git", "commit", "-m", COMMIT_MSG], cwd=repo_path)
    _run(["git", "push", "origin", f"HEAD:{BRANCH}"], cwd=repo_path)
    print(f"PR ready: https://github.com/{ORG}/{repo}/pull/new/{BRANCH}")


def main() -> None:
    """Propagate diamond templates to all 23 GenesisAeon repositories."""
    base_dir = Path(__file__).parents[4]
    errors: list[str] = []

    for repo in REPOS:
        try:
            propagate(repo, base_dir)
        except Exception as exc:
            print(f"Error in {repo}: {exc}")
            errors.append(repo)

    total = len(REPOS)
    ok = total - len(errors)
    print(f"\nDiamond propagation complete – {ok}/{total} repos updated!")
    if errors:
        print(f"Failed: {errors}")


if __name__ == "__main__":  # pragma: no cover
    main()
