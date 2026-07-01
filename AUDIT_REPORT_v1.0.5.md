# GenesisAeon Ecosystem Audit Report
## genesis-os v1.0.5 + 48 Subpakete
## Datum: 2026-07-01

### EXECUTIVE SUMMARY

Seit dem Audit vom **2026-06-30** (v1.0.1) hat sich das Ökosystem **deutlich verbessert**: **genesis-os 1.0.5** ist auf PyPI, das **`[full-stack]`-Extra listet 48 Pakete** (PyPI-Install verifiziert, `pip check` clean), **1399/1399 Tests grün** (91 % Coverage), **`CITATION.cff`** valide, **Diamond-Contract-CI** für vier Referenz-UTACs, **`diamond-setup` 2.1.0** auf PyPI, **`unified-mandala-demo` 1.0.1** importierbar. Der **kritischste neue Befund**: Bei `pip install "genesis-os[full-stack]"` **überschreibt `cosmic-web`** das Top-Level-Paket `genesis_os/__init__.py` — `from genesis_os import GenesisOS` **schlägt fehl** (`__version__` wird `0.1.0`, nur `universums_sim` exportiert). Das widerspricht README/Quickstart und ist für externe Nutzer ein **Showstopper** im Full-Stack-Modus. Weiterhin offen: **Γ-Divergenzen** (theta, phaethon, hikari, diffusive), **Diamond-Timeouts** (sandpile, cygnus, neural-avalanche, spiking), **amazon-utac Repro-Bug**, **genesis-scope P39** unvollständig, **`.zenodo.json` `communities`**.

---

### DELTA vs. Audit v1.0.1 (2026-06-30)

| Bereich | v1.0.1 (alt) | v1.0.5 (neu) | Bewertung |
|---------|--------------|--------------|-----------|
| PyPI genesis-os | v1.0.0, 14 Extras | **v1.0.5**, 48 `full-stack` | ✅ Behoben |
| `mandala-visualize` | Falscher Name | **`mandala-visualizer`** | ✅ Behoben |
| `unified-mandala-demo` | Leeres Wheel | **1.0.1 importierbar** | ✅ Behoben |
| Tests genesis-os | 1381 pass / **2 fail** | **1399 pass / 0 fail** | ✅ Behoben |
| AgentMemory FIFO | Bug | Fix in 1.0.3+ | ✅ Behoben |
| Mandala-Plugin-Test | Umgebungsabhängig | `patch.dict`-Fix | ✅ Behoben |
| `diamond-setup` | v1.0.0, Vendoring | **v2.1.0**, 4 UTACs migriert | ✅ Behoben |
| Diamond Contract CI | Fehlte | **`contracts/` + CI-Job** | ✅ Neu |
| Zenodo-Versionen | `0.2.0`-Bug | **`parse_release_tag` + sync** | ✅ Behoben (Tooling) |
| `CITATION.cff` | Fehlte | **Vorhanden, cffconvert OK** | ✅ Behoben |
| `release.yml` | 0 Jobs (`v*.*.*`) | **`v*` + workflow_dispatch** | ✅ Behoben |
| Full-Stack `GenesisOS`-Import | Nicht geprüft / OK bei 14 Paketen | **`cosmic-web` kapert `genesis_os`** | ❌ **Regression** |
| Diamond-Schema-Quote | ~30 % vollständig | ~40 % + 3 migrierte UTACs 1.1.0 | ⚠️ Teilweise |
| Γ-Atlas-Konsistenz | 4 starke Divergenzen | **Weiterhin 4+ Divergenzen** | ❌ Unverändert |
| `.zenodo.json` communities | Fehlte | **Fehlt weiterhin** | ❌ Offen |
| Governance-Templates | Fehlten | **Fehlen weiterhin** | ❌ Offen |

---

### KRITISCHE ISSUES (❌) — sofortiger Handlungsbedarf

| # | Package | Issue | Impact |
|---|---------|-------|--------|
| 1 | **cosmic-web** | Wheel enthält `genesis_os/__init__.py` + `genesis_os/universums_sim.py` und **überschreibt** genesis-os beim Full-Stack-Install. | `from genesis_os import GenesisOS` → **ImportError**; README-Quickstart bricht nach `pip install "genesis-os[full-stack]"`. |
| 2 | **amazon-utac** | `run_cycle()`-Reproduktion: `ValueError: truth value of an array is ambiguous`. | Diamond-Automation scheitert; instabile Runtime bei Array-Vergleich. |
| 3 | **Import-Namensraum** | Distribution ≠ Import: `beta-clustering-utac` → `beta_clustering`; `phi-scaling-validator` → `phi_scaling`; `implosive-origin-utac` → `implosive_origin`; `genesis-q4-core` → `genesis_q4`; `genesisaeon-hexaagent` → `hexa_agent`; `feldtheorie` → `analysis`/`models`. | Audit-Skripte, Plugin-Registry und CI müssen Mapping kennen — blindes `import <pip-name>` scheitert. |
| 4 | **Γ-Werte (CREP-Atlas)** | Nach `run_cycle()`: `theta-resonance` Γ=**0.106** (erw. 0.251); `phaethon-chimera` Γ=**0.296** (erw. 0.165); `hikari-ledger` Γ≈**0.0** (erw. 0.367); `diffusive-routing` Γ≈**3e-5** (erw. 0.443). | Wissenschaftliche Konsistenz mit dokumentiertem Atlas nicht nachweisbar. |
| 5 | **genesis-scope (P39)** | `get_utac_state()` ohne `H/H_star/K_eff`; `to_zenodo_record()` ohne Pflichtfelder; `Gamma=None` vor `run_cycle()`. | Strategisches Modul nicht Diamond-konform; Agent/MCP-Integration blockiert. |

---

### WARNUNGEN (⚠️) — vor nächstem Minor-Release

| # | Package | Issue | Empfehlung |
|---|---------|-------|------------|
| 1 | genesis-os | README Quickstart referenziert `final_state.phi_h` — API liefert **`final_state.phi`**. | README an `GenesisState`-Felder anpassen. |
| 2 | genesis-os | `.zenodo.json`: **`communities`** fehlt weiterhin. | Zenodo-Community-Identifier ergänzen. |
| 3 | genesis-os | `RELEASE_GUIDE.md`, Issue-/PR-Templates fehlen. | Templates aus `scripts/templates/` promoten. |
| 4 | sandpile, cygnus-jet, neural-avalanche, spiking-aeon | Diamond-Check **Timeout >25 s**. | CI-Default `n_steps=1` oder leichtgewichtiger Modus. |
| 5 | eml-utac-bridge, genesis-scope | `Gamma=None` bis `run_cycle()` (bei migrierten UTACs **by design**). | Verhalten dokumentieren; Orchestrator muss `run_cycle()` vor `get_crep_state()` aufrufen. |
| 6 | cellular-genesis, sa-sv-duality | `run_cycle()` **nicht reproduzierbar** (Seed 42). | Determinismus für Reproduzierbarkeit sicherstellen. |
| 7 | vrig, phaethon, afet, sa-sv-duality | `get_utac_state()` Schema lückenhaft (`H`/`H_star`/`K_eff`). | UTAC-Keys vervollständigen. |
| 8 | quantum-genesis, epi-sigillin, afet, sa-sv-duality | `to_zenodo_record()` fehlende `creators`/`description`/`title`. | Zenodo-Pflichtfelder ergänzen. |
| 9 | full-stack pins | `amoc-utac>=1.0.0` installiert **1.0.0**, nicht **1.1.0** (Diamond-Migration). | Floor-Pin auf `>=1.1.0` anheben. |
| 10 | genesis-os / ruff | 3 fixable `W292` (fehlende Newline am Dateiende). | `ruff check --fix`. |
| 11 | mypy (full-stack) | Weiterhin viele `import-untyped` in Adapters bei optionalen Paketen. | Stub-CI oder Adapter-Konsolidierung. |

---

### DIAMOND INTERFACE STATUS

Legende: ✅ = Methode OK & Schema vollständig | ⚠️ = vorhanden, Schema lückenhaft | ❌ = Fehler | — = Timeout | n/a = kein Diamond

| Package | run_cycle | get_crep_state | get_utac_state | get_phase_events | to_zenodo_record | Γ korrekt |
|---------|-----------|----------------|----------------|-----------------|------------------|-----------|
| amoc-utac (1.0.0) | ✅ | ✅ Γ=0.297 | ✅ | ✅ | ✅ | ✅ (Δ≈0.046) |
| amazon-utac | ❌ Array-Bug | — | — | — | — | — |
| neural-avalanche-utac | — Timeout | — | — | — | — | — |
| solar-flare-utac | ✅ | ✅ Γ=0.0065 | ✅ | ✅ | ✅ | ✅ |
| sandpile-utac | — Timeout | — | — | — | — | — |
| seismic-utac | ✅ | ✅ Γ=0.197 | ✅ | ✅ | ✅ | ✅ |
| cygnus-jet-utac | — Timeout | — | — | — | — | n/a |
| quantum-genesis | ✅ | ✅ Γ=0.035 | ✅ | ✅ | ⚠️ creators | ✅ |
| cellular-genesis | ✅ | ✅ Γ=0.040 | ✅ | ✅ | ✅ | n/a |
| spiking-aeon | — Timeout | — | — | — | — | n/a |
| theta-resonance | ✅ | ✅ Γ=0.106 | ✅ | ✅ | ✅ | ❌ (0.106 vs 0.251) |
| epi-sigillin | ✅ | ✅ Γ=1.0 | ✅ | ✅ | ⚠️ desc/creators | n/a |
| vrig-cosmological | ✅ | ✅ Γ=0.251 | ⚠️ H/H*/K_eff | ✅ | ✅ | n/a |
| sa-sv-duality | ✅ | ✅ Γ=0.251 | ⚠️ H/K_eff | ✅ | ⚠️ alle 3 | n/a |
| phaethon-chimera | ✅ | ✅ Γ=0.296 | ⚠️ H/K_eff | ✅ | ✅ | ❌ (0.296 vs 0.165) |
| afet-tensions | ✅ | ✅ Γ=0.560 | ⚠️ H*/K_eff | ✅ | ⚠️ desc/creators | n/a |
| beta-clustering-utac **1.1.0** | ✅ | ✅ Γ=0.355* | ✅ | ✅ | ✅ | n/a |
| eml-utac-bridge | ✅ | ⚠️ Γ=None† | ⚠️ H*/K_eff | ✅ | ✅ | n/a |
| phi-scaling-validator **1.1.0** | ✅ | ⚠️ Γ=0.0* | ✅ | ✅ | ✅ | n/a |
| implosive-origin-utac **1.1.0** | ✅ | ✅ Γ=0.579* | ✅ | ✅ | ✅ | n/a |
| genesis-scope | ✅ | ⚠️ Γ=None† | ❌ alle 3 | ✅ | ❌ alle 3 | n/a |
| hikari-ledger | ✅ | ✅ Γ≈0.0 | ✅ | ✅ | ⚠️ | ❌ |
| diffusive-routing | ✅ | ✅ Γ≈3e-5 | ✅ | ✅ | ⚠️ | ❌ |
| utac-core | n/a | — | — | — | — | n/a |
| unified-mandala | n/a | — | — | — | — | n/a |
| genesis-q4-core | n/a | — | — | — | — | n/a |

\* Nach `run_cycle()` geprüft (DiamondPackage v2.1 — Γ ist Attractor, nicht Initialwert).  
† Vor `run_cycle()` erwartetes Verhalten bei DiamondPackage-Migration.

**Befund:** Vollständig schemakonform (ohne Γ-Korrektheit): **amoc, solar-flare, seismic, cellular** (+ migrierte **beta-clustering, implosive-origin** nach `run_cycle()`). **phi-scaling** liefert Γ=0.0 — Atlas-Abgleich offen.

---

### TEST COVERAGE SUMMARY (genesis-os Core, editable)

| Metrik | v1.0.1 | v1.0.5 |
|--------|--------|--------|
| Gesamttests | 1383 | **1399** |
| Pass | 1381 | **1399** |
| Fail | 2 | **0** |
| Coverage | 91,4 % | **91,2 %** |
| Dauer | ~2 min 27 s | **~2 min 15 s** |
| Determinismus (2× Lauf) | Identisch (2 fail) | **Identisch (0 fail)** |

**Behobene Failures (v1.0.1):**
1. `test_use_plugin_true_without_package_sets_plugin_none` — Mandala-Mock
2. `test_max_depth_fifo` — AgentMemory FIFO

**Offline:** Alle Tests laufen ohne Netzwerk.

---

### INSTALLATION MATRIX

| Paket / Gruppe | Install | Import | Diamond | Anmerkung |
|----------------|---------|--------|---------|-----------|
| genesis-os (PyPI core) | ✅ **1.0.5** | ✅ | n/a | `pip check` clean |
| genesis-os[full-stack] (PyPI) | ✅ **48 Deps** | ⚠️ **47/48**‡ | gemischt | **`GenesisOS`-Import kaputt** (cosmic-web) |
| pip check (full-stack venv) | ✅ | — | — | Keine Konflikte |
| unified-mandala-demo | ✅ 1.0.1 | ✅ | n/a | Shim funktioniert |
| mandala-visualizer | ✅ | ✅ | n/a | Korrekter PyPI-Name |
| diamond-setup | ✅ **2.1.0** | ✅ | n/a | Nicht mehr 1.0.0 |
| beta-clustering / implosive-origin / phi-scaling | ✅ **1.1.0** | ✅ (Alias-Module) | ✅ nach run_cycle | DiamondPackage-Migration |
| genesisaeon-sonification | — | — | n/a | Nur in `[audio]`, nicht full-stack |
| feldtheorie | ✅ 6.0.0 | ✅ als `analysis` | n/a | Kein `feldtheorie`-Top-Level |

‡ 47/48 Module importierbar mit Alias-Mapping; `sonification` nur via `[audio]`.

**Import-Health (audit venv, Alias-korrigiert):** **47/48 OK**

---

### BLOCK 5 — METADATA

| Check | Ergebnis |
|-------|----------|
| `pyproject.toml` version | **1.0.5** ✅ |
| `.zenodo.json` version | **1.0.5** ✅ |
| `CHANGELOG.md` [1.0.5] | ✅ |
| Versionen konsistent (lokal) | ✅ |
| PyPI vs. lokal | ✅ **MATCH** (1.0.5) |
| Direkte Dependencies | **9** |
| `full-stack` optional deps | **48** |
| `mandala-visualizer` | ✅ |
| `diamond-setup>=2.1.0` | ✅ |
| `CITATION.cff` | ✅ valide (cffconvert 1.2.0) |

### README Blindtest

| Kriterium | Ergebnis |
|-----------|----------|
| Installation `pip install genesis-os`? | ✅ |
| Quickstart (editable, GenesisConfig)? | ⚠️ Läuft bis Phase/Entropy; **`phi_h` → `phi`** |
| Quickstart (full-stack PyPI)? | ❌ **`GenesisOS` nicht importierbar** |
| DOI / Zenodo | ✅ `10.5281/zenodo.19645351` |
| Citation | ✅ BibTeX + **CITATION.cff** |

---

### BLOCK 7 — CI/CD & RELEASE

| Check | Ergebnis |
|-------|----------|
| `release.yml` | ✅ valide; Trigger: **`v*`**, `workflow_dispatch` |
| Jobs | build, test, publish-pypi, publish-testpypi, github-release, publish-zenodo, publish-zenodo-sandbox |
| `ci.yml` | ✅ inkl. **`diamond-contract`**-Job |
| Secrets | `PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN`, `ZENODO_TOKEN`, `ZENODO_SANDBOX_TOKEN` |
| `RELEASE_GUIDE.md` | ❌ fehlt |
| Issue/PR-Templates | ❌ fehlen |

---

### BLOCK 8 — SICHERHEIT & QUALITÄT

| Check | Ergebnis |
|-------|----------|
| `ruff check src tests` | ⚠️ **3** fixable W292 (Newline) |
| `mypy src` (full-stack) | ⚠️ viele Adapter-`import-untyped` (unverändert) |
| Hardcodierte Credentials | ✅ Keine echten Secrets |
| pip-audit | Nicht vollständig neu ausgeführt (v1.0.1: 5 CVEs setuptools transitiv) |

---

### BLOCK 9 — GENESIS-SCOPE (P39)

| Check | Ergebnis |
|-------|----------|
| Offline `run_cycle()` | ✅ |
| `get_crep_state()` | ⚠️ `Gamma=None` (vor run_cycle) |
| `get_utac_state()` | ❌ `H`, `H_star`, `K_eff` fehlen |
| `to_zenodo_record()` | ❌ Pflichtfelder fehlen |
| `get_semantic_path()` | ⚠️ nicht implementiert |
| `to_llms_txt()` | ⚠️ nicht implementiert |

---

### BLOCK 10 — ZENODO & OPEN SCIENCE

| Feld | Status |
|------|--------|
| title, description, creators, license, keywords | ✅ |
| version | ✅ **1.0.5** |
| related_identifiers | ✅ (4) |
| **communities** | ❌ **MISSING** |
| README DOI | ✅ |
| **CITATION.cff** | ✅ **NEW** |

---

### OFFENE PUNKTE FÜR v1.1.0

1. **`cosmic-web`**: `genesis_os`-Namespace aus Wheel entfernen oder in Subpackage `cosmic_web` verschieben — **P0**.
2. **Full-Stack Smoke-Test**: CI-Job `pip install genesis-os[full-stack] && python -c "from genesis_os import GenesisOS"`.
3. **UTAC-Batch**: Verbleibende Pakete auf `DiamondPackage` migrieren; Floor-Pins `>=1.1.0` für migrierte UTACs.
4. **`DIST_TO_IMPORT.json`**: Zentrales Mapping Distribution → Import-Modul.
5. **Γ-Atlas**: Implementierungen oder Atlas-Dokumentation für theta/phaethon/hikari/diffusive harmonisieren.
6. **genesis-scope P39**: UTAC + Zenodo + semantische Pfad-API.
7. **`.zenodo.json` `communities`** + Governance-Templates.
8. **Performance-Defaults** für Timeout-UTACs.
9. **README**: `phi_h` → `phi`.

---

### BESTÄTIGTE STÄRKEN ✅

- **PyPI-Realität = Repo-Dokumentation** (1.0.5, 48 full-stack Pakete).
- **1399 Tests grün**, 91 % Coverage, deterministisch, offline-fähig.
- **Diamond Contract CI** + `contracts/diamond.interface.yaml`.
- **4 UTACs auf DiamondPackage 1.1.0** (beta-clustering, implosive-origin, phi-scaling, amoc-Referenz).
- **`diamond-setup` 2.1.0** ohne Vendoring in migrierten Paketen.
- **`CITATION.cff`** FAIR4RS-konform.
- **Zenodo-Version-Sync-Tooling** (`parse_release_tag`, `sync_zenodo_version.py`).
- **unified-mandala-demo** repariert.
- Solide UTAC-Kernpakete: amoc, solar-flare, seismic mit vollständigem Diamond-Schema.

---

### METHODISCHER HINWEIS

Audit durchgeführt am **2026-07-01** in:
- **Audit-venv**: `D:\mandala\.tmp\ga_audit` (Python 3.11, Windows 10)
- **Editable-Tests**: `D:\mandala\genesis-os` (lokales Repo, main @ v1.0.5)

Rohdaten:
- `test-results/audit_diamond.json` — Diamond Subprocess-Audit (25 s Timeout)
- `test-results/audit_raw.json` — Metadata/Import (System-Python, partiell)
- `test-results/pytest_output_v105.txt` — Pytest + Coverage
- `test-results/audit_fullstack_install_v105.txt` — Full-Stack pip-Log

Vergleichsbasis: `AUDIT_REPORT_v1.0.1.md` (2026-06-30).

*„Ein System, das lauscht — ein Muster, das lebt."*