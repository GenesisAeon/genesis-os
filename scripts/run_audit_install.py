#!/usr/bin/env python3
"""Block 1: pip install audit — records install results per package."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

OPTIONAL_PACKAGES = [
    "genesisaeon-hexaagent",
    "genesisaeon-sonification",
    "amoc-utac",
    "amazon-utac",
    "neural-avalanche-utac",
    "solar-flare-utac",
    "sandpile-utac",
    "seismic-utac",
    "cygnus-jet-utac",
    "quantum-genesis",
    "cellular-genesis",
    "spiking-aeon",
    "theta-resonance",
    "epi-sigillin",
    "hikari-ledger",
    "diffusive-routing",
    "vrig-cosmological",
    "sa-sv-duality",
    "phaethon-chimera",
    "afet-tensions",
    "beta-clustering-utac",
    "eml-utac-bridge",
    "phi-scaling-validator",
    "implosive-origin-utac",
    "genesis-q4-core",
    "genesis-scope",
    "aeon-ai",
    "advanced-weighting-systems",
    "fieldtheory",
    "feldtheorie",
    "mirror-machine",
    "cosmic-web",
    "sigillin",
    "epi-sigillin",
    "entropy-governance",
    "utac-core",
    "mandala-visualize",
    "unified-mandala",
    "unified-mandala-demo",
    "climate-dashboard",
    "implosive-genesis",
    "implosive-origin-utac",
    "entropy-table",
    "diamond-setup",
    "medium-modulation",
    "universums-sim",
    "cosmic-moment",
    "quantum-genesis",
    "worldview",
    "gemeinwohl",
    "spiking-aeon",
    "theta-resonance",
    "afet-tensions",
    "hikari-ledger",
    "diffusive-routing",
    "vrig-cosmological",
    "sa-sv-duality",
    "phaethon-chimera",
    "beta-clustering-utac",
    "eml-utac-bridge",
    "phi-scaling-validator",
    "genesis-scope",
    "genesis-q4-core",
]


def pip_install(pkg: str) -> dict[str, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", pkg, "-q"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    return {
        "package": pkg,
        "ok": r.returncode == 0,
        "stderr": (r.stderr or r.stdout)[-500:],
    }


def pip_check() -> dict[str, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        capture_output=True,
        text=True,
    )
    return {"ok": r.returncode == 0, "output": r.stdout + r.stderr}


def pip_list_filter() -> list[str]:
    r = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
        check=True,
    )
    import json as _json

    pkgs = _json.loads(r.stdout)
    keywords = (
        "genesis", "entropy", "utac", "crep", "afet", "mandala", "sigillin",
        "fieldtheory", "feldtheorie", "cosmic", "mirror", "climate", "aeon",
        "diamond", "implosive", "medium", "worldview", "gemeinwohl", "hexa",
        "sonification", "spiking", "theta", "hikari", "diffusive", "vrig",
        "phaethon", "beta", "eml", "phi", "sandpile", "seismic", "amoc",
        "amazon", "neural", "solar", "cygnus", "quantum", "cellular",
    )
    return [
        f"{p['name']}=={p['version']}"
        for p in pkgs
        if any(k in p["name"].lower() for k in keywords)
    ]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    results: dict[str, object] = {"per_package": [], "pip_check_after_each": []}

    # Core install
    core = subprocess.run(
        [sys.executable, "-m", "pip", "install", "genesis-os", "-q"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    results["core_install"] = {
        "ok": core.returncode == 0,
        "stderr": (core.stderr or core.stdout)[-800:],
    }
    results["pip_check_after_core"] = pip_check()
    results["installed_after_core"] = pip_list_filter()

    seen: set[str] = set()
    for pkg in OPTIONAL_PACKAGES:
        if pkg in seen:
            continue
        seen.add(pkg)
        entry = pip_install(pkg)
        results["per_package"].append(entry)
        if not entry["ok"]:
            results.setdefault("failures", []).append(entry)

    results["pip_check_final"] = pip_check()
    results["installed_final"] = pip_list_filter()

    # full-stack extra
    fs = subprocess.run(
        [sys.executable, "-m", "pip", "install", "genesis-os[full-stack]", "-q"],
        capture_output=True,
        text=True,
        timeout=600,
    )
    results["full_stack_install"] = {
        "ok": fs.returncode == 0,
        "stderr": (fs.stderr or fs.stdout)[-1000:],
    }
    results["pip_check_after_fullstack"] = pip_check()

    out = root / "test-results" / "audit_install.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {out}")
    print(f"Failures: {len(results.get('failures', []))}")


if __name__ == "__main__":
    main()