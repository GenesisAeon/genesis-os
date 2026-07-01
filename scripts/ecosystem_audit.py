#!/usr/bin/env python3
"""GenesisAeon Ecosystem Deep Audit — runs Blocks 2, 3, 5, 6, 9, 10 programmatically."""

from __future__ import annotations

import importlib
import inspect
import json
import random
import sys
import traceback
from pathlib import Path
from typing import Any

# ── Block 2: Import health ───────────────────────────────────────────────────

IMPORT_PACKAGES = [
    "genesis_os",
    "entropy_table",
    "utac_core",
    "fieldtheory",
    "sigillin",
    "medium_modulation",
    "cosmic_moment",
    "mandala_visualize",
    "implosive_genesis",
    "entropy_governance",
    "mirror_machine",
    "climate_dashboard",
    "cosmic_web",
    "aeon_ai",
    "amoc_utac",
    "amazon_utac",
    "neural_avalanche_utac",
    "solar_flare_utac",
    "sandpile_utac",
    "seismic_utac",
    "cygnus_jet_utac",
    "quantum_genesis",
    "cellular_genesis",
    "spiking_aeon",
    "theta_resonance",
    "epi_sigillin",
    "hikari_ledger",
    "diffusive_routing",
    "vrig_cosmological",
    "sa_sv_duality",
    "phaethon_chimera",
    "afet_tensions",
    "beta_clustering_utac",
    "eml_utac_bridge",
    "phi_scaling_validator",
    "implosive_origin_utac",
    "genesis_q4_core",
    "genesis_scope",
    "advanced_weighting_systems",
    "universums_sim",
    "worldview",
    "gemeinwohl",
    "diamond_setup",
    "unified_mandala",
    "unified_mandala_demo",
    "genesisaeon_hexaagent",
    "genesisaeon_sonification",
    "feldtheorie",
]

# Known distribution → import name overrides
IMPORT_ALIASES: dict[str, list[str]] = {
    "genesisaeon_hexaagent": ["hexa_agent"],
    "genesisaeon_sonification": ["genesisaeon_sonification", "sonification"],
    "beta_clustering_utac": ["beta_clustering"],
    "eml_utac_bridge": ["eml_utac_bridge"],
    "phi_scaling_validator": ["phi_scaling"],
    "implosive_origin_utac": ["implosive_origin"],
}

DIAMOND_PACKAGES: list[tuple[str, str | None]] = [
    ("amoc_utac", "AmocUTAC"),
    ("amazon_utac", "AmazonUTAC"),
    ("neural_avalanche_utac", "NeuralAvalancheUTAC"),
    ("solar_flare_utac", "SolarFlareUTAC"),
    ("sandpile_utac", "SandpileUTAC"),
    ("seismic_utac", "SeismicUTAC"),
    ("cygnus_jet_utac", "CygnusJetUTAC"),
    ("quantum_genesis", "QuantumGenesis"),
    ("cellular_genesis", "CellularGenesis"),
    ("spiking_aeon", "SpikingAeon"),
    ("theta_resonance", "ThetaResonance"),
    ("epi_sigillin", "EpiSigillin"),
    ("vrig_cosmological", "VRIGCosmological"),
    ("sa_sv_duality", "SAVDuality"),
    ("phaethon_chimera", "PhaethonChimera"),
    ("afet_tensions", "AFETTensions"),
    ("beta_clustering_utac", "BetaClusteringUTAC"),
    ("eml_utac_bridge", "EMLUTACBridge"),
    ("phi_scaling_validator", "PhiScalingValidator"),
    ("implosive_origin_utac", "ImplosiveOriginUTAC"),
    ("genesis_scope", "GenesisScope"),
    ("genesis_q4_core", "Q4StateMachine"),
    ("utac_core", "UTACCore"),
    ("unified_mandala", "UnifiedMandala"),
]

REQUIRED_METHODS = [
    "run_cycle",
    "get_crep_state",
    "get_utac_state",
    "get_phase_events",
    "to_zenodo_record",
]

CREP_KEYS = {"C", "R", "E", "P", "Gamma"}
UTAC_KEYS = {"H", "H_star", "K_eff"}
ZENODO_KEYS = {"title", "description", "creators"}

EXPECTED_GAMMA: dict[str, float] = {
    "amoc_utac": 0.251,
    "amazon_utac": 0.116,
    "neural_avalanche_utac": 0.251,
    "solar_flare_utac": 0.014,
    "sandpile_utac": 0.296,
    "seismic_utac": 0.200,
    "cygnus_jet_utac": 0.046,
    "quantum_genesis": 0.050,
    "cellular_genesis": 0.090,
    "spiking_aeon": 0.150,
    "theta_resonance": 0.251,
    "phaethon_chimera": 0.165,
    "hikari_ledger": 0.367,
    "diffusive_routing": 0.443,
}

TOLERANCE = 0.05
DIAMOND_TIMEOUT_S = 15


def try_import(name: str) -> tuple[str, str | None]:
    """Return (status, detail)."""
    candidates = IMPORT_ALIASES.get(name, [name])
    last_err = ""
    for mod_name in candidates:
        try:
            importlib.import_module(mod_name)
            label = mod_name if mod_name != name else name
            return "OK", label
        except ImportError as e:
            last_err = str(e)
        except Exception as e:
            return f"{type(e).__name__}", str(e)
    return "ImportError", last_err


def find_class(mod: Any, class_name: str | None) -> type | None:
    if class_name and hasattr(mod, class_name):
        cls = getattr(mod, class_name)
        if isinstance(cls, type):
            return cls
    # cellular_genesis / spiking_aeon pattern
    for sub in ("system", ""):
        try:
            submod = importlib.import_module(f"{mod.__name__}.system") if sub else mod
            for name in dir(submod):
                if name.startswith("_"):
                    continue
                obj = getattr(submod, name)
                if isinstance(obj, type) and all(
                    hasattr(obj, m) for m in REQUIRED_METHODS
                ):
                    return obj
        except Exception:
            pass
    for name in dir(mod):
        if name.startswith("_"):
            continue
        obj = getattr(mod, name)
        if isinstance(obj, type) and all(hasattr(obj, m) for m in REQUIRED_METHODS):
            return obj
    return None


def validate_diamond(instance: Any, package_name: str) -> dict[str, str]:
    results: dict[str, str] = {}

    try:
        r = instance.run_cycle()
        if not isinstance(r, dict):
            results["run_cycle"] = f"FAIL type={type(r)}"
        else:
            results["run_cycle"] = f"OK keys={len(r)}"
    except Exception as e:
        results["run_cycle"] = f"FAIL {e}"

    try:
        r = instance.get_crep_state()
        if not isinstance(r, dict):
            results["get_crep_state"] = f"FAIL type={type(r)}"
        else:
            missing = CREP_KEYS - set(r.keys())
            gamma = r.get("Gamma")
            if missing:
                results["get_crep_state"] = f"WARN missing={missing} Gamma={gamma}"
            else:
                results["get_crep_state"] = f"OK Gamma={gamma}"
    except Exception as e:
        results["get_crep_state"] = f"FAIL {e}"

    try:
        r = instance.get_utac_state()
        if not isinstance(r, dict):
            results["get_utac_state"] = f"FAIL type={type(r)}"
        else:
            missing = UTAC_KEYS - set(r.keys())
            if missing:
                results["get_utac_state"] = f"WARN missing={missing}"
            else:
                results["get_utac_state"] = (
                    f"OK H={r.get('H')} H*={r.get('H_star')}"
                )
    except Exception as e:
        results["get_utac_state"] = f"FAIL {e}"

    try:
        r = instance.get_phase_events()
        if not isinstance(r, list):
            results["get_phase_events"] = f"FAIL type={type(r)}"
        else:
            results["get_phase_events"] = f"OK n={len(r)}"
    except Exception as e:
        results["get_phase_events"] = f"FAIL {e}"

    try:
        r = instance.to_zenodo_record()
        if not isinstance(r, dict):
            results["to_zenodo_record"] = f"FAIL type={type(r)}"
        else:
            missing = ZENODO_KEYS - set(r.keys())
            if missing:
                results["to_zenodo_record"] = f"WARN missing={missing}"
            else:
                title = str(r.get("title", ""))[:50]
                results["to_zenodo_record"] = f"OK title={title!r}"
    except Exception as e:
        results["to_zenodo_record"] = f"FAIL {e}"

    return results


def check_gamma(module_name: str, instance: Any) -> tuple[str, float | None, float | None]:
    expected = EXPECTED_GAMMA.get(module_name)
    try:
        crep = instance.get_crep_state()
        actual = crep.get("Gamma") if isinstance(crep, dict) else None
        if actual is None:
            return "WARN Gamma=None", actual, expected
        if expected is None:
            return "n/a", actual, expected
        if abs(float(actual) - expected) <= TOLERANCE:
            return "OK", actual, expected
        return "FAIL", actual, expected
    except Exception as e:
        return f"FAIL {e}", None, expected


def check_repro(module_name: str, cls: type) -> str:
    try:
        import numpy as np

        random.seed(42)
        np.random.seed(42)
        i1 = cls()
        r1 = i1.run_cycle()

        random.seed(42)
        np.random.seed(42)
        i2 = cls()
        r2 = i2.run_cycle()

        if r1 == r2:
            return "OK"
        diff = [k for k in set(list(r1.keys()) + list(r2.keys())) if r1.get(k) != r2.get(k)]
        return f"FAIL keys={diff[:5]}"
    except Exception as e:
        return f"WARN {type(e).__name__}: {e}"


def block_imports() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for pkg in IMPORT_PACKAGES:
        status, detail = try_import(pkg)
        out[pkg] = {"status": status, "detail": detail or ""}
    return out


def block_diamond() -> dict[str, Any]:
    out: dict[str, Any] = {}
    import signal

    def _timeout_handler(signum: int, frame: Any) -> None:
        raise TimeoutError("diamond check timeout")

    has_alarm = hasattr(signal, "SIGALRM")
    for module_name, class_name in DIAMOND_PACKAGES:
        entry: dict[str, Any] = {"class": class_name, "methods": {}, "gamma": "n/a", "repro": "n/a"}
        try:
            mod = importlib.import_module(module_name)
            cls = find_class(mod, class_name)
            if cls is None:
                entry["status"] = "NO_CLASS"
                out[module_name] = entry
                continue

            entry["class"] = cls.__name__
            if has_alarm:
                signal.signal(signal.SIGALRM, _timeout_handler)
                signal.alarm(DIAMOND_TIMEOUT_S)
            try:
                instance = cls()
                entry["methods"] = validate_diamond(instance, module_name)
                g_status, actual, expected = check_gamma(module_name, instance)
                entry["gamma"] = {
                    "status": g_status,
                    "actual": actual,
                    "expected": expected,
                }
                entry["repro"] = check_repro(module_name, cls)
                entry["status"] = "CHECKED"
            finally:
                if has_alarm:
                    signal.alarm(0)
        except TimeoutError:
            entry["status"] = "TIMEOUT"
        except Exception as e:
            entry["status"] = f"ERROR: {type(e).__name__}: {e}"
            entry["traceback"] = traceback.format_exc()
        out[module_name] = entry
    return out


def block_metadata(root: Path) -> dict[str, Any]:
    import tomllib

    result: dict[str, Any] = {}
    with open(root / "pyproject.toml", "rb") as f:
        toml = tomllib.load(f)
    result["version_toml"] = toml.get("project", {}).get("version")
    result["direct_deps"] = toml.get("project", {}).get("dependencies", [])
    result["optional_deps"] = toml.get("project", {}).get("optional-dependencies", {})

    zenodo_path = root / ".zenodo.json"
    if zenodo_path.exists():
        with open(zenodo_path, encoding="utf-8") as f:
            zenodo = json.load(f)
        result["version_zenodo"] = zenodo.get("version")
        result["zenodo_fields"] = zenodo
    else:
        result["version_zenodo"] = "FILE NOT FOUND"

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8") if (root / "CHANGELOG.md").exists() else ""
    result["has_101_changelog"] = "[1.0.1]" in changelog

    all_deps = result["direct_deps"] + [
        d for deps in result["optional_deps"].values() for d in deps
    ]
    names = [d.split(">=")[0].split("==")[0].strip() for d in all_deps]
    result["naming_checks"] = {
        "genesisaeon-hexaagent": "genesisaeon-hexaagent" in names,
        "genesisaeon-sonification": "genesisaeon-sonification" in names,
        "entropy-table": "entropy-table" in names,
        "diamond-setup": "diamond-setup" in names,
        "NOT hexaagent": "hexaagent" not in names,
        "NOT sonification": "sonification" not in names,
    }
    return result


def block_genesis_scope() -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        import genesis_scope

        cls = getattr(genesis_scope, "GenesisScope", None)
        if cls is None:
            for name in dir(genesis_scope):
                obj = getattr(genesis_scope, name)
                if isinstance(obj, type) and hasattr(obj, "run_cycle"):
                    cls = obj
                    break
        if cls is None:
            out["status"] = "NO_CLASS"
            return out

        scope = cls()
        out["run_cycle"] = bool(scope.run_cycle())
        out["crep"] = scope.get_crep_state()
        out["has_semantic_path"] = hasattr(scope, "get_semantic_path")
        out["has_llms_txt"] = hasattr(scope, "to_llms_txt") or hasattr(scope, "export_llms_txt")
        out["status"] = "OK"
    except Exception as e:
        out["status"] = f"ERROR: {e}"
        out["traceback"] = traceback.format_exc()
    return out


def block_zenodo(root: Path) -> dict[str, Any]:
    required = [
        "title", "description", "creators", "license",
        "upload_type", "access_right", "keywords",
        "related_identifiers", "version", "communities",
    ]
    with open(root / ".zenodo.json", encoding="utf-8") as f:
        z = json.load(f)
    fields: dict[str, str] = {}
    for field in required:
        val = z.get(field)
        if val is None:
            fields[field] = "MISSING"
        else:
            fields[field] = "OK"
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    fields["readme_doi"] = "OK" if ("zenodo.org" in readme or "10.5281" in readme) else "MISSING"
    fields["citation_cff"] = "OK" if (root / "CITATION.cff").exists() else "MISSING"
    return fields


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    report = {
        "imports": block_imports(),
        "diamond": block_diamond(),
        "metadata": block_metadata(root),
        "genesis_scope": block_genesis_scope(),
        "zenodo": block_zenodo(root),
    }
    out_path = root / "test-results" / "audit_raw.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()