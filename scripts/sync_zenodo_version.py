#!/usr/bin/env python3
"""Sync .zenodo.json version (and title prefix) from pyproject.toml."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

from genesis_os.tools.release_version import parse_release_tag

ZENODO_VERSION_RE = re.compile(r'("version"\s*:\s*")[^"]+(")')
TITLE_VERSION_RE = re.compile(r"^(\S+\s+v)[\d.]+(:.*)$")


def read_pyproject_version(repo_path: Path) -> str:
    data = tomllib.loads((repo_path / "pyproject.toml").read_text(encoding="utf-8"))
    version = data.get("project", {}).get("version")
    if not version:
        raise ValueError(f"No [project].version in {repo_path / 'pyproject.toml'}")
    return str(version)


def sync_zenodo_file(zenodo_path: Path, version: str, *, dry_run: bool) -> bool:
    if not zenodo_path.is_file():
        return False
    raw = zenodo_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    changed = False

    if data.get("version") != version:
        data["version"] = version
        changed = True

    title = data.get("title")
    if isinstance(title, str):
        m = TITLE_VERSION_RE.match(title)
        if m:
            new_title = f"{m.group(1)}{version}{m.group(2)}"
            if new_title != title:
                data["title"] = new_title
                changed = True

    if not changed:
        return False

    new_raw = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if dry_run:
        print(f"[dry-run] would update {zenodo_path} → version {version}")
    else:
        zenodo_path.write_text(new_raw, encoding="utf-8")
        print(f"Updated {zenodo_path} → version {version}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: cwd)",
    )
    parser.add_argument(
        "--version",
        help="Explicit version (default: read pyproject.toml)",
    )
    parser.add_argument(
        "--tag",
        help="Git tag vX.Y.Z (alternative to --version)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    if args.tag:
        version = parse_release_tag(args.tag)
    elif args.version:
        version = args.version
    else:
        version = read_pyproject_version(repo)

    zenodo = repo / ".zenodo.json"
    if not sync_zenodo_file(zenodo, version, dry_run=args.dry_run):
        if zenodo.is_file():
            print(f"Already synced: {zenodo} ({version})")
        else:
            print(f"No .zenodo.json in {repo}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())