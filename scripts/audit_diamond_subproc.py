#!/usr/bin/env python3
"""Per-package diamond audit in isolated subprocess with hard timeout."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

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

SNIPPET = r'''
import importlib, json, random
import numpy as np
mod_name, cls_name = {pair!r}
METHODS = ["run_cycle","get_crep_state","get_utac_state","get_phase_events","to_zenodo_record"]
CREP={{"C","R","E","P","Gamma"}}
UTAC={{"H","H_star","K_eff"}}
ZEN={{"title","description","creators"}}
out={{"module":mod_name,"class":cls_name}}
try:
    mod=importlib.import_module(mod_name)
except Exception as e:
    print(json.dumps({{"status":"IMPORT_FAIL","error":str(e)}})); raise SystemExit
cls=getattr(mod,cls_name,None)
if cls is None:
    for sub in (mod_name+".system",):
        try:
            sm=importlib.import_module(sub)
            for n in dir(sm):
                o=getattr(sm,n)
                if isinstance(o,type) and all(hasattr(o,m) for m in METHODS):
                    cls=o; break
        except Exception:
            pass
if cls is None:
    for n in dir(mod):
        o=getattr(mod,n)
        if isinstance(o,type) and all(hasattr(o,m) for m in METHODS):
            cls=o; break
if cls is None:
    print(json.dumps({{"status":"NO_CLASS"}})); raise SystemExit
out["class"]=cls.__name__
inst=cls()
methods={{}}
for m in METHODS:
    try:
        r=getattr(inst,m)()
        if m=="run_cycle":
            methods[m]="OK" if isinstance(r,dict) else f"BAD {{type(r)}}"
        elif m=="get_crep_state":
            miss=CREP-set(r.keys()) if isinstance(r,dict) else CREP
            methods[m]=f"OK Gamma={{r.get('Gamma')}}" if not miss else f"WARN missing={{sorted(miss)}} Gamma={{r.get('Gamma')}}"
        elif m=="get_utac_state":
            miss=UTAC-set(r.keys()) if isinstance(r,dict) else UTAC
            methods[m]="OK" if not miss else f"WARN missing={{sorted(miss)}}"
        elif m=="get_phase_events":
            methods[m]="OK" if isinstance(r,list) else f"BAD {{type(r)}}"
        else:
            miss=ZEN-set(r.keys()) if isinstance(r,dict) else ZEN
            methods[m]="OK" if not miss else f"WARN missing={{sorted(miss)}}"
    except Exception as e:
        methods[m]=f"FAIL {{e}}"
out["methods"]=methods
random.seed(42); np.random.seed(42); r1=cls().run_cycle()
random.seed(42); np.random.seed(42); r2=cls().run_cycle()
out["repro"]="OK" if r1==r2 else "FAIL"
out["status"]="CHECKED"
print(json.dumps(out))
'''

TIMEOUT = 25


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    results: dict[str, object] = {}
    py = sys.executable
    for mod_name, cls_name in DIAMOND:
        code = SNIPPET.format(pair=(mod_name, cls_name))
        try:
            proc = subprocess.run(
                [py, "-c", code],
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )
            line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
            if line.startswith("{"):
                results[mod_name] = json.loads(line)
            else:
                results[mod_name] = {
                    "status": "ERROR",
                    "stdout": proc.stdout[-300:],
                    "stderr": proc.stderr[-300:],
                }
        except subprocess.TimeoutExpired:
            results[mod_name] = {"status": "TIMEOUT"}
    out = root / "test-results" / "audit_diamond.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {out} ({len(results)} packages)")


if __name__ == "__main__":
    main()