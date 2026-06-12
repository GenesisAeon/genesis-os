#!/usr/bin/env python3
"""
Normalize metadata across GenesisAeon repositories (dry-run mode).

Validates: pyproject.toml, zenodo.json, README.md

Usage:
    python scripts/normalize_metadata.py --repos diamond-setup,genesis-os,unified-mandala,worldview,gemeinwohl --dry-run
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import toml
except ImportError:
    print("ERROR: toml module required. Install with: pip install toml")
    exit(1)


@dataclass
class MetadataIssue:
    file: str
    severity: str
    message: str
    suggested_fix: Optional[str] = None


@dataclass
class RepositoryMetadataReport:
    repo_name: str
    repo_path: Path
    issues: list[MetadataIssue] = field(default_factory=list)

    def add_issue(self, file: str, severity: str, message: str, suggested_fix: Optional[str] = None) -> None:
        self.issues.append(MetadataIssue(file, severity, message, suggested_fix))

    @property
    def status(self) -> str:
        if any(i.severity == "error" for i in self.issues):
            return "ERROR"
        if any(i.severity == "warning" for i in self.issues):
            return "WARNING"
        return "OK"


def validate_pyproject_toml(repo_path: Path, report: RepositoryMetadataReport) -> None:
    pyproject_file = repo_path / "pyproject.toml"
    if not pyproject_file.exists():
        report.add_issue("pyproject.toml", "error", "File not found")
        return

    try:
        with open(pyproject_file) as f:
            data = toml.load(f)
    except Exception as e:
        report.add_issue("pyproject.toml", "error", f"Parse error: {e}")
        return

    project = data.get("project", {})

    name = project.get("name")
    if not name:
        report.add_issue("pyproject.toml", "error", "Missing [project] name")
    elif name != name.lower():
        report.add_issue("pyproject.toml", "warning", f"Package name '{name}' is not lowercase")

    version = project.get("version")
    if not version:
        report.add_issue("pyproject.toml", "error", "Missing [project] version")
    elif not re.match(r"^\d+\.\d+\.\d+", version):
        report.add_issue("pyproject.toml", "warning", f"Version '{version}' does not follow SemVer")

    if not project.get("authors"):
        report.add_issue("pyproject.toml", "warning", "Missing [project] authors")

    if not project.get("license"):
        report.add_issue("pyproject.toml", "warning", "Missing [project] license")

    if not project.get("requires-python"):
        report.add_issue("pyproject.toml", "warning", "Missing [project] requires-python")


def validate_zenodo_json(repo_path: Path, report: RepositoryMetadataReport) -> None:
    zenodo_file = repo_path / "zenodo.json"
    if not zenodo_file.exists():
        report.add_issue("zenodo.json", "warning", "File not found")
        return

    try:
        with open(zenodo_file) as f:
            data = json.load(f)
    except Exception as e:
        report.add_issue("zenodo.json", "error", f"Parse error: {e}")
        return

    if not data.get("title"):
        report.add_issue("zenodo.json", "warning", "Missing 'title'")

    if not data.get("creators"):
        report.add_issue("zenodo.json", "warning", "Missing 'creators'")

    if not data.get("license"):
        report.add_issue("zenodo.json", "info", "Missing 'license'")

    if not data.get("concept_doi"):
        report.add_issue("zenodo.json", "info", "Missing 'concept_doi'")


def validate_readme(repo_path: Path, report: RepositoryMetadataReport) -> None:
    readme_file = repo_path / "README.md"
    if not readme_file.exists():
        report.add_issue("README.md", "error", "File not found")
        return

    try:
        with open(readme_file) as f:
            content = f.read()
    except Exception as e:
        report.add_issue("README.md", "error", f"Read error: {e}")
        return

    if not re.search(r"^#\s+", content, re.MULTILINE):
        report.add_issue("README.md", "warning", "Missing main title (# Title)")

    if len(content) < 100:
        report.add_issue("README.md", "warning", "README is too short")

    if not re.search(r"(install|pip install)", content, re.IGNORECASE):
        report.add_issue("README.md", "warning", "Missing installation instructions")

    if not re.search(r"(usage|quick.?start|example)", content, re.IGNORECASE):
        report.add_issue("README.md", "warning", "Missing usage or example section")

    if "doi" not in content.lower() and "zenodo" not in content.lower():
        report.add_issue("README.md", "info", "No DOI reference")


def print_dry_run_summary(reports: list[RepositoryMetadataReport]) -> None:
    print("\n" + "=" * 80)
    print("METADATA NORMALIZATION DRY RUN")
    print("=" * 80 + "\n")

    for report in sorted(reports, key=lambda r: r.repo_name):
        status_icon = "✅" if report.status == "OK" else "⚠️" if report.status == "WARNING" else "❌"
        print(f"{status_icon} {report.repo_name:30s} [{report.status}]")

        for issue in report.issues:
            severity_icon = "❌" if issue.severity == "error" else "⚠️" if issue.severity == "warning" else "ℹ️"
            print(f"    {severity_icon} {issue.file:20s} {issue.message}")
            if issue.suggested_fix:
                print(f"       → {issue.suggested_fix}")

        print()

    print("=" * 80)
    print(f"Summary: {sum(1 for r in reports if r.status == 'OK')} OK, "
          f"{sum(1 for r in reports if r.status == 'WARNING')} Warnings, "
          f"{sum(1 for r in reports if r.status == 'ERROR')} Errors")
    print("=" * 80 + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Normalize GenesisAeon repository metadata.")
    parser.add_argument("--repos", default="diamond-setup,genesis-os,unified-mandala,worldview,gemeinwohl", help="Comma-separated repo names")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry-run mode (default)")
    args = parser.parse_args()

    repos_to_analyze = [r.strip() for r in args.repos.split(",")]
    print(f"[*] Analyzing metadata for {len(repos_to_analyze)} repos...\n", flush=True)

    reports = []
    for repo_name in repos_to_analyze:
        repo_path = Path(repo_name)

        if not repo_path.exists():
            print(f"  [SKIP] {repo_name} (directory not found)")
            continue

        print(f"  [ANALYZING] {repo_name}...", end=" ", flush=True)

        report = RepositoryMetadataReport(repo_name=repo_name, repo_path=repo_path)

        validate_pyproject_toml(repo_path, report)
        validate_zenodo_json(repo_path, report)
        validate_readme(repo_path, report)

        reports.append(report)
        print(f"{report.status}", flush=True)

    if args.dry_run:
        print_dry_run_summary(reports)


if __name__ == "__main__":
    main()
