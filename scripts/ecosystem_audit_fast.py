#!/usr/bin/env python3
"""Fast ecosystem audit with per-package timeout (Windows-safe)."""

from __future__ import annotations

import importlib
import json
import random
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from pathlib import Path
from typing import Any

TIMEOUT = 20

IMPORT_PACKAGES = [
    "genesis_os", "entropy_table", "utac_core", "fieldtheory", "sigillin",
    "medium_modulation", "cosmic_moment", "mandala_visualize", "implosive_genesis",
    "entropy_governance", "mirror_machine", "climate_dashboard", "cosmic_web", "aeon_ai",
    "amoc_utac", "amazon_utac", "neural_avalanche_utac", "solar_flare_utac",
    "sandpile_utac", "seismic_utac", "cygnus_jet_utac", "quantum_genesis",
    "cellular_genesis", "spiking_aeon", "theta_resonance", "epi_sigillin",
    "hikari_ledger", "diffusive_routing", "vrig_cosmological", "sa_sv_duality",
    "phaethon_chimera", "afet_tensions", "beta_clustering_utac", "eml_utac_bridge",
    "phi_scaling_validator", "implosive_origin_utac", "genesis_q4_core",
    "genesis_scope", "advanced_weighting_systems", "universums_sim", "worldview",
    "gemeinwohl", "diamond_setup", "unified_mandala", "unified_mandala_demo",
    "hexa_agent", "genesisaeon_sonification", "feldtheorie", "beta_clustering",
    "phi_scaling", "implosive_origin",
]

ALIASES: dict[str, list[str]] = {
    "mandala_visualize": ["mandala_visualize", "mandala_visualizer"],
    "genesisaeon_hexaagent": ["hexa_agent"],
    "beta_clustering_utac": ["beta_clustering_utac", "beta_clustering"],
    "phi_scaling_validator": ["phi_scaling_validator", "phi_scaling"],
    "implosive_origin_utac": ["implosive_origin_utac", "implosive_origin"],
}

DIAMOND = [
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

METHODS = ["run_cycle", "get_crep_state", "get_utac_state", "get_phase_events", "to_zenodo_record"]
CREP_KEYS = {"C", "R", "E", "P", "Gamma"}
UTAC_KEYS = {"H", "H_star", "K_eff"}
ZENODO_KEYS = {"title", "description", "creators"}
EXPECTED_GAMMA = {
    "amoc_utac": 0.251, "amazon_utac": 0.116, "neural_avalanche_utac": 0.251,
    "solar_flare_utac": 0.014, "sandpile_utac": 0.296, "seismic_utac": 0.200,
    "cygnus_jet_utac": 0.046, "quantum_genesis": 0.050, "cellular_genesis": 0.090,
    "spiking_aeon": 0.150, "theta_resonance": 0.251, "phaethon_chimera": 0.165,
    "hikari_ledger": 0.367, "diffusive_routing": 0.443,
}
TOL = 0.05


def try_import(name: str) -> dict[str, str]:
    for mod in ALIASES.get(name, [name]):
        try:
            importlib.import_module(mod)
            return {"status": "OK", "module": mod}
        except ImportError as e:
            err = str(e)
        except Exception as e:
            return {"status": type(e).__name__, "detail": str(e)}
    return {"status": "ImportError", "detail": err}


def find_class(mod_name: str, cls_name: str | None) -> type | None:
    mod = importlib.import_module(mod_name)
    if cls_name and hasattr(mod, cls_name):
        c = getattr(mod, cls_name)
        if isinstance(c, type):
            return c
    for sub in (f"{mod_name}.system", mod_name):
        try:
            m = importlib.import_module(sub) if "." in sub else mod
            for n in dir(m):
                if n.startswith("_"):
                    continue
                o = getattr(m, n)
                if isinstance(o, type) and all(hasattr(o, x) for x in METHODS):
                    return o
        except Exception:
            pass
    return None


def audit_diamond(mod_name: str, cls_name: str | None) -> dict[str, Any]:
    out: dict[str, Any] = {"module": mod_name, "class": cls_name}
    cls = find_class(mod_name, cls_name)
    if cls is None:
        out["status"] = "NO_CLASS"
        return out
    out["class"] = cls.__name__
    inst = cls()
    methods: dict[str, str] = {}
    for m in METHODS:
        fn = getattr(inst, m)
        try:
            r = fn()
            if m == "run_cycle":
                methods[m] = "OK" if isinstance(r, dict) else f"BAD_TYPE {type(r)}"
            elif m == "get_crep_state":
                if not isinstance(r, dict):
                    methods[m] = f"BAD_TYPE {type(r)}"
                else:
                    miss = CREP_KEYS - set(r.keys())
                    methods[m] = f"OK Gamma={r.get('Gamma')}" if not miss else f"WARN missing={sorted(miss)} Gamma={r.get('Gamma')}"
            elif m == "get_utac_state":
                if not isinstance(r, dict):
                    methods[m] = f"BAD_TYPE {type(r)}"
                else:
                    miss = UTAC_KEYS - set(r.keys())
                    methods[m] = "OK" if not miss else f"WARN missing={sorted(miss)}"
            elif m == "get_phase_events":
                methods[m] = "OK" if isinstance(r, list) else f"BAD_TYPE {type(r)}"
            elif m == "to_zenodo_record":
                if not isinstance(r, dict):
                    methods[m] = f"BAD_TYPE {type(r)}"
                else:
                    miss = ZENODO_KEYS - set(r.keys())
                    methods[m] = "OK" if not miss else f"WARN missing={sorted(miss)}"
        except Exception as e:
            methods[m] = f"FAIL {e}"
    out["methods"] = methods
    exp = EXPECTED_GAMMA.get(mod_name)
    if exp is not None:
        try:
            g = inst.get_crep_state().get("Gamma")
            if g is None:
                out["gamma"] = "WARN None"
            elif abs(float(g) - exp) <= TOL:
                out["gamma"] = f"OK {g}"
            else:
                out["gamma"] = f"FAIL actual={g} expected={exp}"
        except Exception as e:
            out["gamma"] = f"FAIL {e}"
    try:
        import numpy as np
        random.seed(42); np.random.seed(42)
        r1 = cls().run_cycle()
        random.seed(42); np.random.seed(42)
        r2 = cls().run_cycle()
        out["repro"] = "OK" if r1 == r2 else "FAIL"
    except Exception as e:
        out["repro"] = f"WARN {e}"
    out["status"] = "CHECKED"
    return out


def run_with_timeout(fn: Any, *args: Any) -> dict[str, Any]:
    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(fn, *args)
        try:
            return fut.result(timeout=TIMEOUT)
        except FuturesTimeout:
            return {"status": "TIMEOUT", "module": args[0] if args else "?"}
        except Exception as e:
            return {"status": f"ERROR {e}", "traceback": traceback.format_exc()}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    imports = {p: try_import(p) for p in IMPORT_PACKAGES}
    diamond = {m: run_with_timeout(audit_diamond, m, c) for m, c in DIAMOND}

    scope: dict[str, Any] = {}
    try:
        import genesis_scope
        cls = getattr(genesis_scope, "GenesisScope", None)
        if cls:
            s = cls()
            scope = {
                "run_cycle": bool(s.run_cycle()),
                "crep": s.get_crep_state(),
                "has_semantic_path": hasattr(s, "get_semantic_path"),
                "has_llms_txt": hasattr(s, "to_llms_txt") or hasattr(s, "export_llms_txt"),
            }
    except Exception as e:
        scope = {"error": str(e)}

    report = {"imports": imports, "diamond": diamond, "genesis_scope": scope}
    out = root / "test-results" / "audit_raw.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()