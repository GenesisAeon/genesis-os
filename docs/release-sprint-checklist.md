# GenesisAeon Release Sprint — Checkliste v1.0.0

> Generiert: 2026-06-03  
> Ziel: Alle 40 Pakete auf PyPI v1.0.0 (unified-mandala → v20.0.0)  
> Diamond Interface: `run_cycle()` · `get_crep_state()` · `get_utac_state()` · `get_phase_events()` · `to_zenodo_record()`  
> CREP-Formel: **Γ = (C·R·E·P)^(1/4)**

Pro Paket je eine Session. Checkliste pro Paket:
- [ ] `pyproject.toml` → version = "1.0.0", hatchling build-backend
- [ ] Diamond Interface vollständig implementiert
- [ ] `tests/` mit ≥ 5 Tests (Diamond-Interface + CREP-Wert)
- [ ] `.github/workflows/publish.yml` eingefügt (Template aus genesis-os)
- [ ] `PYPITOKEN` als **Repository Secret** gesetzt (Settings → Secrets → Actions)
- [ ] `.zenodo.json` aktualisiert
- [ ] Tag `v1.0.0` gesetzt → GitHub Release ausgelöst → PyPI publish

---

## 🟢 Tier 0 — genesis-os (Hub)

| Paket | Repo | Version | Diamond | CI | PyPI | Prio |
|---|---|---|---|---|---|---|
| genesis-os | `genesis-os` | ✅ 1.0.0 | ✅ | ✅ grün | ⏳ retry | — |

---

## 🔵 Tier 1 — Domain Science (P17–P40)

Priorität: Pakete ohne Gamma-Wert zuerst (noch nicht spezifiziert), dann aufsteigend nach Γ.

| ID | Repo | Domain | Γ | Diamond | v1.0.0 | publish.yml | Released | Session |
|---|---|---|---|---|---|---|---|---|
| P28 | `epi-sigillin` | Epigenetics | — | ❓ | ❓ | ❓ | ❌ | todo |
| P31 | `vrig-cosmological` | Cosmology | — | ❓ | ❓ | ❓ | ❌ | todo |
| P32 | `beta-clustering-utac` | Clustering | — | ❓ | ❓ | ❓ | ❌ | todo |
| P33 | `implosive-origin-utac` | Origins | — | ❓ | ❓ | ❓ | ❌ | todo |
| P34 | `afet-tensions` | Field Theory | — | ❓ | ❓ | ❓ | ❌ | todo |
| P36 | `sa-sv-duality` | Math-Physics | — | ❓ | ❓ | ❓ | ❌ | todo |
| P37 | `eml-utac-bridge` | Bridge | — | ❓ | ❓ | ❓ | ❌ | todo |
| P38 | `phi-scaling-validator` | Validation | — | ❓ | ❓ | ❓ | ❌ | todo |
| P39 | `genesis-scope` | Meta/Scope | — | ✅ | ✅ | ❓ | ❌ | **done** |
| P40 | `HexaAgent` | Agent Roles | — | ❓ | ❓ | ❓ | ❌ | todo |
| P21 | `solar-flare-utac` | Heliophysics | 0.014 | ❓ | ❓ | ❓ | ❌ | todo |
| P17 | `cygnus-jet-utac` | Astrophysics | 0.046 | ❓ | ❓ | ❓ | ❌ | todo |
| P24 | `quantum-genesis` | Quantum | 0.050 | ❓ | ❓ | ❓ | ❌ | todo |
| P25 | `cellular-genesis` | Cell Biology | 0.090 | ❓ | ❓ | ❓ | ❌ | todo |
| P19 | `amazon-utac` | Ecology | 0.116 | ❓ | ❓ | ❓ | ❌ | todo |
| P26 | `spiking-aeon` | Neuromorphic | 0.150 | ❓ | ❓ | ❓ | ❌ | todo |
| P35 | `phaethon-chimera` | Chimera | 0.165 | ❓ | ❓ | ❓ | ❌ | todo |
| P23 | `seismic-utac` | Geophysics | 0.200 | ❓ | ❓ | ❓ | ❌ | todo |
| P18 | `amoc-utac` | Oceanography | 0.251 | ❓ | ❓ | ❓ | ❌ | todo |
| P20 | `neural-avalanche-utac` | Neuroscience | 0.251 | ❓ | ❓ | ❓ | ❌ | todo |
| P27 | `theta-resonance` | Cog-Neuro | 0.251 | ❓ | ❓ | ❓ | ❌ | todo |
| P22 | `sandpile-utac` | Stat-Mech | 0.296 | ❓ | ❓ | ❓ | ❌ | todo |
| P29 | `hikari-ledger` | Distributed | 0.367 | ❓ | ❓ | ❓ | ❌ | todo |
| P30 | `diffusive-routing` | Networks | 0.443 | ❓ | ❓ | ❓ | ❌ | todo |

---

## 🟡 Tier 2 — Core Infrastructure (15 Pakete)

Abhängigkeiten der Domain-Pakete — sollten **vor** den Domain-Paketen released sein.

| Paket | Repo | Domain | Γ | Diamond | v1.0.0 | publish.yml | Released | Session |
|---|---|---|---|---|---|---|---|---|
| `utac-core` | `utac-core` | Runtime Core | — | ❓ | ❓ | ❓ | ❌ | todo |
| `genesis-q4-core` | `genesis-q4-core` | Runtime Core | — | ❓ | ❓ | ❓ | ❌ | todo |
| `Feldtheorie` | `Feldtheorie` | Theory | — | ❓ | ❓ | ❓ | ❌ | todo |
| `sigillin` | `sigillin` | Semantic | — | ❓ | ❓ | ❓ | ❌ | todo |
| `unified-mandala` | `unified-mandala` | Visualization | — | ❓ | ❓ | ❓ | ❌ | **v20.0.0** |
| `aeon-ai` | `aeon-ai` | AI Core | — | ❓ | ❓ | ❓ | ❌ | todo |
| `mirror-machine` | `mirror-machine` | AI Core | — | ❓ | ❓ | ❓ | ❌ | todo |
| `medium-modulation` | `medium-modulation` | Math-Physics | — | ❓ | ❓ | ❓ | ❌ | todo |
| `universums-sim` | `universums-sim` | Simulation | — | ❓ | ❓ | ❓ | ❌ | todo |
| `cosmic-moment` | `cosmic-moment` | Simulation | — | ❓ | ❓ | ❓ | ❌ | todo |
| `worldview` | `worldview` | Governance | — | ❓ | ❓ | ❓ | ❌ | todo |
| `gemeinwohl` | `gemeinwohl` | Governance | — | ❓ | ❓ | ❓ | ❌ | todo |
| `entropy-governance` | `entropy-governance` | Governance | — | ❓ | ❓ | ❓ | ❌ | todo |
| `entropy-table` | `entropy-table` | Data | — | ❓ | ❓ | ❓ | ❌ | todo |
| `sonification` | `sonification` | Audio | — | ❓ | ❓ | ❓ | ❌ | todo |

---

## 🟠 Tier 3 — Legacy Sprint 1 (P1–P16, 5 Pakete)

Bestehende Pakete, brauchen v1.0.0-Bump + Diamond Interface.

| Paket | Repo | Domain | Diamond | v1.0.0 | publish.yml | Released | Session |
|---|---|---|---|---|---|---|---|
| `AdvancedWeightingSystems` | `AdvancedWeightingSystems` | Legacy | ❓ | ❓ | ❓ | ❌ | todo |
| `climate-dashboard` | `climate-dashboard` | Legacy | ❓ | ❓ | ❓ | ❌ | todo |
| `implosive-genesis` | `implosive-genesis` | Legacy | ❓ | ❓ | ❓ | ❌ | todo |
| `mandala-visualize` | `mandala-visualize` | Legacy | ❓ | ❓ | ❓ | ❌ | todo |
| `cosmic-web` | `cosmic-web` | Legacy | ❓ | ❓ | ❓ | ❌ | todo |

---

## 📋 Session-Prompt-Template

Kopiere dies in eine neue Session für jedes Paket:

```
Wir arbeiten am GenesisAeon-Ökosystem (github.com/GenesisAeon).
Repo: <REPO-NAME>
Paket-ID: <P-ID>
Domain: <DOMAIN>
Ziel-Version: 1.0.0 (unified-mandala: 20.0.0)

Aufgaben:
1. Lese den aktuellen Stand des Repos (pyproject.toml, src/, tests/)
2. Prüfe ob das Diamond Interface vollständig ist:
   - run_cycle() → dict
   - get_crep_state() → dict mit 'gamma' Key (Γ = (C·R·E·P)^(1/4))
   - get_utac_state() → dict mit 'H', 'r', 'K'
   - get_phase_events() → list[dict]
   - to_zenodo_record() → dict
3. Implementiere fehlende Diamond-Methoden
4. Setze version = "1.0.0" in pyproject.toml
5. Füge .github/workflows/publish.yml ein (Template: scripts/templates/publish.yml aus genesis-os)
6. Aktualisiere .zenodo.json
7. Stelle sicher dass Tests grün sind
8. Committe + pushe auf main

CREP-Formel: Γ = (C·R·E·P)^(1/4) — geometrisches Mittel, KEIN altes Summen-Exponential!
UTAC-ODE: dH/dt = r·H·(1-H/K)·tanh(σ·Γ)
```

---

## 🗺️ Empfohlene Reihenfolge

```
Woche 1: Tier 2 Core (15 Pakete) — Fundament legen
  → utac-core, genesis-q4-core, Feldtheorie, sigillin
  → aeon-ai, mirror-machine, medium-modulation
  → universums-sim, cosmic-moment
  → worldview, gemeinwohl, entropy-governance, entropy-table
  → sonification, unified-mandala (v20.0.0)

Woche 2: Tier 1 Domain — P28–P40 (ohne Gamma, todo zuerst)
  → genesis-scope ✅ done
  → HexaAgent, epi-sigillin, vrig-cosmological
  → beta-clustering-utac, implosive-origin-utac
  → afet-tensions, sa-sv-duality, eml-utac-bridge
  → phi-scaling-validator

Woche 3: Tier 1 Domain — P17–P30 (mit Gamma)
  → aufsteigend nach Γ: solar-flare → ... → diffusive-routing

Woche 4: Tier 3 Legacy + genesis-os PyPI-Retry
  → 5 Legacy-Pakete
  → genesis-os full-stack deps auf >=1.0.0 bumpen
  → propagate.py live-run → alle grün
```

---

## 📊 Fortschritt

- **Total:** 41 Pakete (inkl. genesis-os Hub)
- **Fertig:** 1 (genesis-os ✅, genesis-scope ✅ aber noch kein Release)
- **Offen:** 39
- **Geschätzt:** ~2 Sessions/Tag → ~3-4 Wochen
