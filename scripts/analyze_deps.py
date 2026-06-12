#!/usr/bin/env python3
"""
Dependency analysis across the GenesisAeon ecosystem (48 repositories).

Clones (or reuses) each repo with `git clone --depth=1`, parses pyproject.toml
for metadata/dependencies, greps source for Diamond-Interface method
definitions, builds an intra-org dependency graph, detects circular
dependencies via DFS, flags version constraint conflicts against
release_map.yml, and lists unresolved (external) dependencies.

Usage:
    python scripts/analyze_deps.py --repos all --output DEPENDENCY_REPORT.md
    python scripts/analyze_deps.py --repos utac-core,genesis-os --workdir /tmp/genesisaeon
"""

import argparse
import re
import subprocess
from pathlib import Path

try:
    import toml
except ImportError:
    print("ERROR: toml module required. Install with: pip install toml")
    raise SystemExit(1)

try:
    import yaml
except ImportError:
    yaml = None

ORG = "GenesisAeon"

ALL_REPOS = [
    "AdvancedWeightingSystems", "aeon-ai", "afet-tensions", "amazon-utac", "amoc-utac",
    "beta-clustering-utac", "cellular-genesis", "climate-dashboard", "cosmic-moment",
    "cosmic-web", "cygnus-jet-utac", "diamond-setup", "diffusive-routing", "eml-utac-bridge",
    "entropy-governance", "entropy-table", "epi-sigillin", "Feldtheorie", "fieldtheory",
    "gemeinwohl", "genesis-os", "genesis-q4-core", "genesis-scope", "HexaAgent", "hikari-ledger",
    "implosive-genesis", "implosive-origin-utac", "mandala-visualize", "medium-modulation",
    "mirror-machine", "neural-avalanche-utac", "phaethon-chimera", "phi-scaling-validator",
    "quantum-genesis", "sa-sv-duality", "sandpile-utac", "seismic-utac", "sigillin",
    "solar-flare-utac", "sonification", "spiking-aeon", "theta-resonance", "unified-mandala",
    "unified-mandala-Demo", "universums-sim", "utac-core", "vrig-cosmological", "worldview",
]

DIAMOND_METHODS = [
    "run_cycle",
    "get_crep_state",
    "get_utac_state",
    "get_phase_events",
    "to_zenodo_record",
]

# Heuristic: package-name normalization (PEP 503-ish, hyphen<->underscore agnostic)
def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower().strip()


def clone_repo(repo: str, workdir: Path) -> Path | None:
    dest = workdir / repo
    if dest.exists():
        return dest
    url = f"https://github.com/{ORG}/{repo}.git"
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", "--quiet", url, str(dest)],
            check=True, timeout=120,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        return dest
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"  [WARN] clone failed for {repo}: {e}")
        return None


def parse_pyproject(repo_path: Path) -> dict:
    pyproject_file = repo_path / "pyproject.toml"
    if not pyproject_file.exists():
        return {}
    try:
        data = toml.load(pyproject_file)
    except Exception:
        return {}
    project = data.get("project", {})
    deps = list(project.get("dependencies", []))
    for extra_deps in project.get("optional-dependencies", {}).values():
        deps.extend(extra_deps)
    return {
        "name": project.get("name", ""),
        "version": project.get("version", ""),
        "dependencies": deps,
    }


def split_requirement(req: str) -> tuple[str, str]:
    """Split a PEP 508-ish requirement string into (name, constraint)."""
    match = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)$", req.strip())
    if not match:
        return req.strip(), ""
    return match.group(1), match.group(2).split(";")[0].strip()


def find_diamond_methods(repo_path: Path) -> set[str]:
    found = set()
    src_dir = repo_path
    for py_file in src_dir.rglob("*.py"):
        if ".git" in py_file.parts:
            continue
        try:
            text = py_file.read_text(errors="ignore")
        except OSError:
            continue
        for method in DIAMOND_METHODS:
            if re.search(rf"def\s+{method}\s*\(", text):
                found.add(method)
    return found


def load_release_map(path: Path) -> dict:
    if yaml is None or not path.exists():
        return {}
    with open(path) as f:
        data = yaml.safe_load(f)
    return data or {}


def detect_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """DFS-based cycle detection. Returns list of cycles (as node lists)."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    cycles = []

    def dfs(node, stack):
        color[node] = GRAY
        stack.append(node)
        for neighbor in graph.get(node, ()):
            if neighbor not in color:
                continue
            if color[neighbor] == GRAY:
                cycle_start = stack.index(neighbor)
                cycles.append(stack[cycle_start:] + [neighbor])
            elif color[neighbor] == WHITE:
                dfs(neighbor, stack)
        stack.pop()
        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            dfs(node, [])
    return cycles


def main():
    parser = argparse.ArgumentParser(description="Analyze GenesisAeon ecosystem dependencies.")
    parser.add_argument("--repos", default="all", help="'all' or comma-separated repo names")
    parser.add_argument("--output", default="DEPENDENCY_REPORT.md", help="Output Markdown report path")
    parser.add_argument("--workdir", default="/tmp/genesisaeon-clones", help="Directory to clone repos into")
    parser.add_argument("--no-clone", action="store_true", help="Skip cloning; use existing workdir contents only")
    args = parser.parse_args()

    repos = ALL_REPOS if args.repos == "all" else [r.strip() for r in args.repos.split(",")]
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    release_map = load_release_map(Path("release_map.yml"))
    release_map_keys = {norm(k) for k in release_map}

    repo_info = {}  # repo -> parsed pyproject info
    repo_diamond = {}  # repo -> set of found diamond methods
    name_to_repo = {}  # normalized pypi/package name -> repo

    print(f"[*] Analyzing {len(repos)} repositories...\n", flush=True)

    for repo in repos:
        print(f"  [{'SKIP-CLONE' if args.no_clone else 'CLONE'}] {repo}...", end=" ", flush=True)
        if args.no_clone:
            repo_path = workdir / repo
            if not repo_path.exists():
                print("not found, skipping")
                continue
        else:
            repo_path = clone_repo(repo, workdir)
            if repo_path is None:
                continue

        info = parse_pyproject(repo_path)
        repo_info[repo] = info
        repo_diamond[repo] = find_diamond_methods(repo_path)

        pkg_name = info.get("name") or repo
        name_to_repo[norm(pkg_name)] = repo
        name_to_repo[norm(repo)] = repo

        print("done")

    # Build intra-org dependency graph
    graph: dict[str, set[str]] = {repo: set() for repo in repo_info}
    version_conflicts = []  # (repo, dep_repo, constraint, current_version)
    unresolved = {}  # repo -> list of external deps

    for repo, info in repo_info.items():
        for dep in info.get("dependencies", []):
            dep_name, constraint = split_requirement(dep)
            dep_norm = norm(dep_name)

            if dep_norm in name_to_repo:
                dep_repo = name_to_repo[dep_norm]
                if dep_repo != repo:
                    graph[repo].add(dep_repo)

                # Compare constraint with current_version from release_map
                target = release_map.get(dep_repo, {})
                current_version = target.get("current_version")
                if current_version and constraint:
                    m = re.match(r">=\s*([\d.]+)", constraint)
                    if m:
                        try:
                            req_v = tuple(int(x) for x in m.group(1).split("."))
                            cur_v = tuple(int(x) for x in current_version.split("."))
                            if req_v > cur_v:
                                version_conflicts.append((repo, dep_repo, constraint, current_version))
                        except ValueError:
                            pass
            elif dep_norm in release_map_keys:
                # In release map but repo not analyzed/cloned this run
                pass
            else:
                unresolved.setdefault(repo, []).append(dep)

    cycles = detect_cycles(graph)

    # --- Write report ---
    lines = []
    lines.append("# GenesisAeon Ecosystem — Dependency Analysis Report")
    lines.append("")
    lines.append(f"Repositories analyzed: **{len(repo_info)} / {len(repos)}**")
    lines.append("")

    lines.append("## 1. Circular Dependencies")
    lines.append("")
    if cycles:
        for cycle in cycles:
            lines.append(f"- ⚠️ Cycle detected: `{' -> '.join(cycle)}`")
    else:
        lines.append("✅ No circular dependencies detected among analyzed repositories.")
    lines.append("")

    lines.append("## 2. Diamond-Interface Method Coverage")
    lines.append("")
    lines.append("Checks for definitions of: " + ", ".join(f"`{m}`" for m in DIAMOND_METHODS))
    lines.append("")
    lines.append("| Repository | " + " | ".join(DIAMOND_METHODS) + " | Coverage |")
    lines.append("|---|" + "---|" * len(DIAMOND_METHODS) + "---|")
    for repo in sorted(repo_diamond):
        found = repo_diamond[repo]
        cells = ["✅" if m in found else "—" for m in DIAMOND_METHODS]
        coverage = f"{len(found)}/{len(DIAMOND_METHODS)}"
        lines.append(f"| {repo} | " + " | ".join(cells) + f" | {coverage} |")
    lines.append("")

    lines.append("## 3. Version Constraint Conflicts")
    lines.append("")
    lines.append("Cases where a repo requires a higher version of a sibling package than its")
    lines.append("`current_version` listed in `release_map.yml`.")
    lines.append("")
    if version_conflicts:
        lines.append("| Repository | Dependency | Required | Current (release_map) |")
        lines.append("|---|---|---|---|")
        for repo, dep_repo, constraint, current_version in version_conflicts:
            lines.append(f"| {repo} | {dep_repo} | `{constraint}` | `{current_version}` |")
    else:
        lines.append("✅ No version constraint conflicts detected.")
    lines.append("")

    lines.append("## 4. Unresolved (External) Dependencies")
    lines.append("")
    lines.append("Dependencies that are not part of the GenesisAeon ecosystem (third-party PyPI packages).")
    lines.append("")
    if unresolved:
        for repo in sorted(unresolved):
            deps = sorted(set(unresolved[repo]))
            lines.append(f"<details><summary><b>{repo}</b> ({len(deps)} external deps)</summary>\n")
            for dep in deps:
                lines.append(f"- `{dep}`")
            lines.append("\n</details>")
    else:
        lines.append("None found.")
    lines.append("")

    lines.append("## 5. Intra-Org Dependency Graph")
    lines.append("")
    lines.append("| Repository | Depends on (GenesisAeon) |")
    lines.append("|---|---|")
    for repo in sorted(graph):
        deps = ", ".join(sorted(graph[repo])) if graph[repo] else "—"
        lines.append(f"| {repo} | {deps} |")
    lines.append("")

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[*] Report written to {args.output}")


if __name__ == "__main__":
    main()
