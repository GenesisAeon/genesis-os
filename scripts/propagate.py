#!/usr/bin/env python3
"""GenesisAeon Propagation Script — Full Ecosystem Health Check.

Verifies that all GenesisAeon ecosystem packages are importable,
expose the Diamond interface, and return valid CREP/UTAC state dicts.

Package tiers:
  CORE  — runtime infrastructure (genesis-q4-core, utac-core, sigillin, …)
  P17+  — domain science packages (Sprint 2, P17–P40)
  LEGACY — Sprint 1 packages (P1–P16, medium-modulation, etc.)

Usage:
    python scripts/propagate.py                # full check
    python scripts/propagate.py --json         # machine-readable output
    python scripts/propagate.py --install      # pip install missing packages
    python scripts/propagate.py --package P32  # single package check
    python scripts/propagate.py --tier core    # only core packages
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Any

# ─── Package Registry P17–P39 ─────────────────────────────────────────────────
#
# Each entry:  package_id → {name, pypi_name, import_name, class_name, gamma, domain}

PACKAGE_REGISTRY: dict[int, dict[str, Any]] = {
    17: {
        "name": "cygnus-jet-utac",
        "pypi_name": "cygnus-jet-utac",
        "import_name": "cygnus_jet_utac",
        "class_name": "CygnusJetUTAC",
        "gamma": 0.046,
        "domain": "astrophysics",
        "zenodo": "10.5281/zenodo.17472834",
    },
    18: {
        "name": "amoc-utac",
        "pypi_name": "amoc-utac",
        "import_name": "amoc_utac",
        "class_name": "AMOCUTAC",
        "gamma": 0.251,
        "domain": "oceanography",
        "zenodo": "10.5281/zenodo.17472834",
    },
    19: {
        "name": "amazon-utac",
        "pypi_name": "amazon-utac",
        "import_name": "amazon_utac",
        "class_name": "AmazonUTAC",
        "gamma": 0.116,
        "domain": "ecology",
        "zenodo": "10.5281/zenodo.17472834",
    },
    20: {
        "name": "neural-avalanche-utac",
        "pypi_name": "neural-avalanche-utac",
        "import_name": "neural_avalanche_utac",
        "class_name": "NeuralAvalancheUTAC",
        "gamma": 0.251,
        "domain": "neuroscience",
        "zenodo": "10.5281/zenodo.17472834",
    },
    21: {
        "name": "solar-flare-utac",
        "pypi_name": "solar-flare-utac",
        "import_name": "solar_flare_utac",
        "class_name": "SolarFlareUTAC",
        "gamma": 0.014,
        "domain": "heliophysics",
        "zenodo": "10.5281/zenodo.17472834",
    },
    22: {
        "name": "sandpile-utac",
        "pypi_name": "sandpile-utac",
        "import_name": "sandpile_utac",
        "class_name": "SandpileUTAC",
        "gamma": 0.296,
        "domain": "statistical-mechanics",
        "zenodo": "10.5281/zenodo.17472834",
    },
    23: {
        "name": "seismic-utac",
        "pypi_name": "seismic-utac",
        "import_name": "seismic_utac",
        "class_name": "SeismicUTAC",
        "gamma": 0.200,
        "domain": "geophysics",
        "zenodo": "10.5281/zenodo.17472834",
    },
    24: {
        "name": "quantum-genesis",
        "pypi_name": "quantum-genesis",
        "import_name": "quantum_genesis",
        "class_name": "QuantumGenesis",
        "gamma": 0.050,
        "domain": "quantum-physics",
        "zenodo": "10.5281/zenodo.17472834",
    },
    25: {
        "name": "cellular-genesis",
        "pypi_name": "cellular-genesis",
        "import_name": "cellular_genesis",
        "class_name": "CellularGenesis",
        "gamma": 0.090,
        "domain": "cell-biology",
        "zenodo": "10.5281/zenodo.17472834",
    },
    26: {
        "name": "spiking-aeon",
        "pypi_name": "spiking-aeon",
        "import_name": "spiking_aeon",
        "class_name": "SpikingAeon",
        "gamma": 0.150,
        "domain": "neuromorphic",
        "zenodo": "10.5281/zenodo.17472834",
    },
    27: {
        "name": "theta-resonance",
        "pypi_name": "theta-resonance",
        "import_name": "theta_resonance",
        "class_name": "ThetaResonance",
        "gamma": 0.251,
        "domain": "cognitive-neuroscience",
        "zenodo": "10.5281/zenodo.17472834",
    },
    28: {
        "name": "epi-sigillin",
        "pypi_name": "epi-sigillin",
        "import_name": "epi_sigillin",
        "class_name": "EpiSigillin",
        "gamma": None,
        "domain": "epigenetics",
        "zenodo": "10.5281/zenodo.17472834",
    },
    29: {
        "name": "hikari-ledger",
        "pypi_name": "hikari-ledger",
        "import_name": "hikari_ledger",
        "class_name": "HikariLedger",
        "gamma": 0.367,
        "domain": "distributed-systems",
        "zenodo": "10.5281/zenodo.17472834",
    },
    30: {
        "name": "diffusive-routing",
        "pypi_name": "diffusive-routing",
        "import_name": "diffusive_routing",
        "class_name": "DiffusiveRouting",
        "gamma": 0.443,
        "domain": "network-science",
        "zenodo": "10.5281/zenodo.17472834",
    },
    31: {
        "name": "vrig-cosmological",
        "pypi_name": "vrig-cosmological",
        "import_name": "vrig_cosmological",
        "class_name": "VRIGCosmological",
        "gamma": None,
        "domain": "information-geometry",
        "zenodo": "10.5281/zenodo.17472834",
    },
    32: {
        "name": "beta-clustering-utac",
        "pypi_name": "beta-clustering-utac",
        "import_name": "beta_clustering",
        "class_name": "BetaClusteringUTAC",
        "gamma": None,
        "domain": "cross-domain",
        "zenodo": "10.5281/zenodo.17472834",
    },
    33: {
        "name": "implosive-origin-utac",
        "pypi_name": "implosive-origin-utac",
        "import_name": "implosive_origin",
        "class_name": "ImplosiveOriginUTAC",
        "gamma": None,
        "domain": "cosmology",
        "zenodo": "10.5281/zenodo.17472834",
    },
    34: {
        "name": "afet-tensions",
        "pypi_name": "afet-tensions",
        "import_name": "afet_tensions",
        "class_name": "AFETTensions",
        "gamma": None,
        "domain": "cosmology",
        "zenodo": "10.5281/zenodo.17472834",
    },
    35: {
        "name": "phaethon-chimera",
        "pypi_name": "phaethon-chimera",
        "import_name": "phaethon_chimera",
        "class_name": "PhaethonChimera",
        "gamma": 0.165,
        "domain": "asteroid-dynamics",
        "zenodo": "10.5281/zenodo.17472834",
    },
    36: {
        "name": "sa-sv-duality",
        "pypi_name": "sa-sv-duality",
        "import_name": "sa_sv_duality",
        "class_name": "SAVDuality",
        "gamma": None,
        "domain": "mathematical-physics",
        "zenodo": "10.5281/zenodo.17472834",
    },
    37: {
        "name": "eml-utac-bridge",
        "pypi_name": "eml-utac-bridge",
        "import_name": "eml_utac_bridge",
        "class_name": "GenesisAeonReduction",
        "gamma": None,
        "domain": "mathematical-foundations",
        "zenodo": "10.5281/zenodo.17472834",
    },
    38: {
        "name": "phi-scaling-validator",
        "pypi_name": "phi-scaling-validator",
        "import_name": "phi_scaling",
        "class_name": "PhiScalingValidator",
        "gamma": None,
        "domain": "meta-analysis",
        "zenodo": "10.5281/zenodo.17472834",
    },
    39: {
        "name": "genesis-scope",
        "pypi_name": "genesis-scope",
        "import_name": "genesis_scope",
        "class_name": "GenesisScope",
        "gamma": None,
        "domain": "meta-collaboration",
        "zenodo": "10.5281/zenodo.17472834",
    },
    40: {
        "name": "HexaAgent",
        "pypi_name": "hexaagent",
        "import_name": "hexaagent",
        "class_name": "HexaAgent",
        "gamma": None,
        "domain": "agent-roles",
        "zenodo": "10.5281/zenodo.17472834",
    },
}

# ─── Core Infrastructure Packages ─────────────────────────────────────────────
# Not domain packages — runtime/governance/visualization infrastructure.
# Built with diamond-setup template → have Diamond interface.

CORE_REGISTRY: dict[str, dict] = {
    "genesis-q4-core": {
        "pypi_name": "genesis-q4-core",
        "import_name": "genesis_q4_core",
        "class_name": "GenesisQ4Core",
        "gamma": None,
        "domain": "runtime-core",
        "note": "Central Q4 state machine — built with diamond-setup template",
    },
    "utac-core": {
        "pypi_name": "utac-core",
        "import_name": "utac_core",
        "class_name": "UTACEngine",
        "gamma": None,
        "domain": "runtime-core",
        "note": "UTAC ODE engine — used by all P17–P40 domain packages",
    },
    "sigillin": {
        "pypi_name": "sigillin",
        "import_name": "sigillin",
        "class_name": "Sigillin",
        "gamma": None,
        "domain": "semantic-core",
        "note": "Sigillin semantic anchor system",
    },
    "unified-mandala": {
        "pypi_name": "unified-mandala",
        "import_name": "unified_mandala",
        "class_name": "UnifiedMandala",
        "gamma": None,
        "domain": "visualization",
        "note": "Visual OS of consciousness — v20.0.0",
    },
    "worldview": {
        "pypi_name": "worldview",
        "import_name": "worldview",
        "class_name": "Worldview",
        "gamma": None,
        "domain": "governance",
        "note": "Normative CREP compass — philosophical-ethical layer",
    },
    "gemeinwohl": {
        "pypi_name": "gemeinwohl",
        "import_name": "gemeinwohl",
        "class_name": "Gemeinwohl",
        "gamma": None,
        "domain": "governance",
        "note": "Common-good score + PersonhoodLevel governance",
    },
    "universums-sim": {
        "pypi_name": "universums-sim",
        "import_name": "universums_sim",
        "class_name": "UniversumsSim",
        "gamma": None,
        "domain": "simulation",
        "note": "Cosmic emergence simulator (CosmicMoment, leapfrog)",
    },
    "cosmic-moment": {
        "pypi_name": "cosmic-moment",
        "import_name": "cosmic_moment",
        "class_name": "CosmicMoment",
        "gamma": None,
        "domain": "simulation",
        "note": "Single discrete cosmic moment — building block of universums-sim",
    },
    "Feldtheorie": {
        "pypi_name": "fieldtheory",
        "import_name": "fieldtheory",
        "class_name": "Feldtheorie",
        "gamma": None,
        "domain": "theory",
        "note": "Frame Principle, σ_Φ ≈ 1/16 — theoretical foundation repo",
    },
    "aeon-ai": {
        "pypi_name": "aeon-ai",
        "import_name": "aeon_ai",
        "class_name": "AeonAI",
        "gamma": None,
        "domain": "ai-core",
        "note": "Self-reflective engine + Mirror Machine phase-transition detection",
    },
    "mirror-machine": {
        "pypi_name": "mirror-machine",
        "import_name": "mirror_machine",
        "class_name": "MirrorMachine",
        "gamma": None,
        "domain": "ai-core",
        "note": "Tension metric, DualDetector, 87.2× damping",
    },
    "entropy-governance": {
        "pypi_name": "entropy-governance",
        "import_name": "entropy_governance",
        "class_name": "EntropyGovernance",
        "gamma": None,
        "domain": "governance",
        "note": "EthicsGate + entropy-based governance",
    },
    "entropy-table": {
        "pypi_name": "entropy-table",
        "import_name": "entropy_table",
        "class_name": "EntropyTable",
        "gamma": None,
        "domain": "data",
        "note": "Entropy lookup tables",
    },
    "sonification": {
        "pypi_name": "sonification",
        "import_name": "sonification",
        "class_name": "Sonification",
        "gamma": None,
        "domain": "audio",
        "note": "CREP sonification — optional [audio] extra",
    },
    "medium-modulation": {
        "pypi_name": "medium-modulation",
        "import_name": "medium_modulation",
        "class_name": "MediumModulation",
        "gamma": None,
        "domain": "mathematical-physics",
        "note": "Dynamic S_A/S_V coupling layer — fractal modulation operators, resonance spectra. Bridges sa-sv-duality (P36) with UTAC action-entropy.",
    },
}

# ─── Sprint 1 Legacy Packages (P1–P16) ────────────────────────────────────────
# First sprint packages — older architecture, not all have Diamond interface.

LEGACY_REGISTRY: dict[str, dict] = {
    "AdvancedWeightingSystems": {
        "pypi_name": "advanced-weighting-systems",
        "import_name": "advanced_weighting_systems",
        "class_name": "AdvancedWeightingSystems",
        "gamma": None,
        "domain": "legacy-sprint1",
        "note": "Sprint 1 — resonance engine for neural architectures",
    },
    "climate-dashboard": {
        "pypi_name": "climate-dashboard",
        "import_name": "climate_dashboard",
        "class_name": "ClimateDashboard",
        "gamma": None,
        "domain": "legacy-sprint1",
        "note": "Sprint 1 — ERA5 climate visualisation",
    },
    "implosive-genesis": {
        "pypi_name": "implosive-genesis",
        "import_name": "implosive_genesis",
        "class_name": "ImplosiveGenesis",
        "gamma": None,
        "domain": "legacy-sprint1",
        "note": "Sprint 1 — precursor to implosive-origin-utac (P33)",
    },
    "mandala-visualize": {
        "pypi_name": "mandala-visualize",
        "import_name": "mandala_visualize",
        "class_name": "MandalaVisualize",
        "gamma": None,
        "domain": "legacy-sprint1",
        "note": "Sprint 1 — precursor to unified-mandala",
    },
    "cosmic-web": {
        "pypi_name": "cosmic-web",
        "import_name": "cosmic_web",
        "class_name": "CosmicWeb",
        "gamma": None,
        "domain": "legacy-sprint1",
        "note": "Sprint 1 — CosmicWebSimulator (now in genesis-os core)",
    },
}

# Diamond interface methods every package must expose
DIAMOND_INTERFACE = [
    "run_cycle",
    "get_crep_state",
    "get_utac_state",
    "get_phase_events",
    "to_zenodo_record",
]


@dataclass
class PackageResult:
    package_id: int
    name: str
    importable: bool = False
    class_found: bool = False
    diamond_methods: list[str] = field(default_factory=list)
    missing_methods: list[str] = field(default_factory=list)
    crep_state_valid: bool = False
    gamma_expected: float | None = None
    error: str | None = None
    elapsed_ms: float = 0.0

    @property
    def status(self) -> str:
        if not self.importable:
            return "NOT_INSTALLED"
        if not self.class_found:
            return "IMPORT_OK_CLASS_MISSING"
        if self.missing_methods:
            return "PARTIAL_DIAMOND"
        return "OK"

    @property
    def icon(self) -> str:
        return {"OK": "✅", "PARTIAL_DIAMOND": "⚠️", "IMPORT_OK_CLASS_MISSING": "🔶", "NOT_INSTALLED": "❌"}[
            self.status
        ]


def check_package(pkg_id: int, meta: dict[str, Any]) -> PackageResult:
    result = PackageResult(
        package_id=pkg_id,
        name=meta["name"],
        gamma_expected=meta.get("gamma"),
    )
    t0 = time.perf_counter()
    try:
        mod = importlib.import_module(meta["import_name"])
        result.importable = True

        cls = getattr(mod, meta["class_name"], None)
        if cls is None:
            # Try system.py submodule pattern
            try:
                sys_mod = importlib.import_module(f"{meta['import_name']}.system")
                cls = getattr(sys_mod, meta["class_name"], None)
            except ImportError:
                pass

        if cls is None:
            result.error = f"Class '{meta['class_name']}' not found"
        else:
            result.class_found = True
            for method in DIAMOND_INTERFACE:
                if callable(getattr(cls, method, None)):
                    result.diamond_methods.append(method)
                else:
                    result.missing_methods.append(method)

            # Try instantiating and calling get_crep_state
            try:
                instance = cls()
                crep = instance.get_crep_state()
                result.crep_state_valid = isinstance(crep, dict) and "gamma" in crep
            except Exception as exc:
                result.crep_state_valid = False
                result.error = f"get_crep_state() raised: {exc}"

    except ImportError as exc:
        result.importable = False
        result.error = str(exc)
    except Exception as exc:
        result.error = f"Unexpected: {exc}"

    result.elapsed_ms = (time.perf_counter() - t0) * 1000
    return result


def install_package(pypi_name: str) -> bool:
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", pypi_name, "--quiet"],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0


def print_report(results: list[PackageResult]) -> None:
    ok = sum(1 for r in results if r.status == "OK")
    not_installed = sum(1 for r in results if r.status == "NOT_INSTALLED")
    partial = sum(1 for r in results if r.status in ("PARTIAL_DIAMOND", "IMPORT_OK_CLASS_MISSING"))

    print("\n" + "═" * 72)
    print("  GenesisAeon Propagation Report — Packages P17–P39")
    print("═" * 72)
    print(f"  {'ID':<4} {'Package':<28} {'Status':<22} {'γ':>6}  {'ms':>6}")
    print("─" * 72)

    for r in results:
        gamma_str = f"{r.gamma_expected:.3f}" if r.gamma_expected is not None else "  —  "
        print(f"  P{r.package_id:<3} {r.name:<28} {r.icon} {r.status:<18} {gamma_str:>6}  {r.elapsed_ms:>5.0f}")
        if r.missing_methods:
            print(f"       └─ missing: {', '.join(r.missing_methods)}")
        if r.error and r.status != "NOT_INSTALLED":
            print(f"       └─ {r.error}")

    print("─" * 72)
    print(f"  ✅ OK: {ok}   ⚠️  Partial: {partial}   ❌ Not installed: {not_installed}   Total: {len(results)}")
    print("═" * 72 + "\n")

    # CREP Spectrum summary for packages with known gamma
    gammas = [(r.name, r.gamma_expected) for r in results if r.gamma_expected is not None]
    if gammas:
        gammas.sort(key=lambda x: x[1])  # type: ignore[return-value]
        print("  CREP Spectrum (ascending Γ):")
        for name, g in gammas:
            bar = "█" * int(g * 40)
            print(f"  {name:<28} Γ={g:.3f}  {bar}")
        print()


def to_json(results: list[PackageResult]) -> str:
    return json.dumps(
        [
            {
                "id": r.package_id,
                "name": r.name,
                "status": r.status,
                "importable": r.importable,
                "class_found": r.class_found,
                "diamond_methods": r.diamond_methods,
                "missing_methods": r.missing_methods,
                "crep_state_valid": r.crep_state_valid,
                "gamma_expected": r.gamma_expected,
                "error": r.error,
                "elapsed_ms": round(r.elapsed_ms, 1),
            }
            for r in results
        ],
        indent=2,
    )


def check_named_registry(
    registry: dict[str, dict],
    label: str,
    install: bool,
) -> list[PackageResult]:
    """Check a name-keyed registry (CORE or LEGACY)."""
    results = []
    for name, meta in sorted(registry.items()):
        full_meta = {"name": name, **meta}
        r = check_package(0, full_meta)
        r.name = name
        if install and not r.importable:
            print(f"Installing {meta['pypi_name']}...")
            if install_package(meta["pypi_name"]):
                r = check_package(0, full_meta)
                r.name = name
            else:
                r.error = f"pip install {meta['pypi_name']} failed"
        results.append(r)
    return results


def print_named_report(results: list[PackageResult], title: str) -> None:
    if not results:
        return
    ok = sum(1 for r in results if r.status == "OK")
    print(f"\n  ── {title} ({ok}/{len(results)} OK) ──")
    for r in results:
        note = r.error or ""
        print(f"  {r.icon} {r.name:<32} {r.status:<22} {note[:40]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="GenesisAeon Full Ecosystem Propagation Check")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--install", action="store_true", help="pip install missing packages")
    parser.add_argument("--package", type=str, help="Check single domain package, e.g. P32 or 32")
    parser.add_argument("--tier", choices=["domain", "core", "legacy", "all"], default="all",
                        help="Which tier to check (default: all)")
    args = parser.parse_args()

    domain_results: list[PackageResult] = []
    core_results: list[PackageResult] = []
    legacy_results: list[PackageResult] = []

    # Domain packages P17–P40
    if args.tier in ("domain", "all"):
        registry = PACKAGE_REGISTRY
        if args.package:
            pid = int(args.package.lstrip("Pp"))
            if pid not in registry:
                print(f"Unknown package ID: {pid}", file=sys.stderr)
                sys.exit(1)
            registry = {pid: registry[pid]}

        for pkg_id, meta in sorted(registry.items()):
            if args.install:
                r = check_package(pkg_id, meta)
                if not r.importable:
                    print(f"Installing {meta['pypi_name']}...")
                    if install_package(meta["pypi_name"]):
                        r = check_package(pkg_id, meta)
                    else:
                        r.error = f"pip install {meta['pypi_name']} failed"
                domain_results.append(r)
            else:
                domain_results.append(check_package(pkg_id, meta))

    # Core infrastructure
    if args.tier in ("core", "all") and not args.package:
        core_results = check_named_registry(CORE_REGISTRY, "Core", args.install)

    # Legacy Sprint 1
    if args.tier in ("legacy", "all") and not args.package:
        legacy_results = check_named_registry(LEGACY_REGISTRY, "Legacy Sprint 1", args.install)

    all_results = domain_results + core_results + legacy_results

    if args.json:
        print(to_json(all_results))
    else:
        if domain_results:
            print_report(domain_results)
        if core_results:
            print_named_report(core_results, "Core Infrastructure")
        if legacy_results:
            print_named_report(legacy_results, "Legacy Sprint 1 (P1–P16)")

    # Exit non-zero if any domain package is not OK (core/legacy are optional)
    if any(r.status == "NOT_INSTALLED" for r in domain_results):
        sys.exit(2)
    if any(r.status in ("PARTIAL_DIAMOND", "IMPORT_OK_CLASS_MISSING") for r in domain_results):
        sys.exit(1)


if __name__ == "__main__":
    main()
