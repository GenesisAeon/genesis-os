# Session Handoff — GenesisAeon · 2026-07-01 (Update 2)

> Copy-paste den Block **„Neue Session — Startprompt“** unten in die nächste Cursor/Grok-Session.

---

## Was in dieser Session erledigt wurde

### A) diamond-setup 2.1.0 + genesis-os pin bump — **abgeschlossen**

| Paket | PyPI | GitHub | Notizen |
|-------|------|--------|---------|
| **diamond-setup** | `2.1.0` LATEST | Tag `v2.1.0`, [Release](https://github.com/GenesisAeon/diamond-setup/releases/tag/v2.1.0) | GH Actions + Trusted Publishing |
| **genesis-os** | `1.0.1` LATEST (1.0.2 **noch nicht** auf PyPI) | `main` + Tag `v1.0.2` | `diamond-setup>=2.1.0` in `pyproject.toml` |

**diamond-setup v2.1.0 — neu:**
- `DiamondPackage` ABC, `CREPState` / `UTACState` / `ZenodoRecord`
- `NotConvergedError` (Γ = Attraktor, nicht Initialwert)
- `validate_diamond_instance()` für CI
- `contracts/diamond.interface.yaml`
- Fix: `test_version` nutzt `__version__` statt hardcoded `1.0.0`

### B) amoc-utac — erste Diamond-Referenzmigration — **abgeschlossen**

| | |
|---|---|
| **Version** | `1.1.0` auf PyPI (manuell + GH Tag `v1.1.0`) |
| **Pfad** | `D:\mandala\amoc-utac` |
| **Änderung** | `AmocUTAC(DiamondPackage)`, Vendoring `src/diamond_setup/` entfernt |
| **Dep** | `diamond-setup>=2.1.0` |
| **Tests** | 57/58 grün; `validate_diamond_instance()` OK |
| **UTAC** | Kanonisch `{H, H_star, K_eff}`; AMOC-Felder in `run_cycle() → utac_extended` |

**Referenz für alle weiteren UTAC-Migrationen:** `amoc_utac/system.py` + `tests/test_diamond_interface.py`

### Lokales PyPI-Publish (neu) — **eingerichtet + Token gesetzt**

| Datei | Status |
|-------|--------|
| `.env.example` | committet (Vorlage) |
| `.env` | **gitignored**, Token eingetragen (`PYPI_API_TOKEN` = `UV_PUBLISH_TOKEN`) |
| `scripts/publish_pypi.ps1` | Windows |
| `scripts/publish_pypi.sh` | Bash |

**Propagieren von hier aus** — ohne GitHub Secret im Ziel-Repo:

```powershell
# Build + Publish beliebiges Paket
pwsh D:\mandala\genesis-os\scripts\publish_pypi.ps1 -RepoPath D:\mandala\<repo>

# Nur prüfen (kein Upload)
pwsh D:\mandala\genesis-os\scripts\publish_pypi.ps1 -RepoPath D:\mandala\<repo> -DryRun
```

Token-Lookup: Shell-Env → `<repo>/.env` → `genesis-os/.env` → `D:\mandala/.env`

**Hinweis:** venv-Ordner (`.venv`, `.audit_venv`) enthalten **kein** Token — nur `.env`.

### Aus vorheriger Session (weiterhin gültig)

- genesis-os v1.0.1 auf PyPI/GitHub/Zenodo
- Ecosystem-Audit: `AUDIT_REPORT_v1.0.1.md`, Issue #1 geschlossen
- `[full-stack]` = 48 Pakete, `mandala-visualizer`, `entropy-table>=2.0.1`

---

## Offene Punkte (priorisiert)

### P0 — genesis-os 1.0.2 auf PyPI nachziehen
- Repo/Tag stehen (`v1.0.2`); Release-Workflow schlägt fehl (0 Jobs — Validierung)
- **Workaround:** `publish_pypi.ps1 -RepoPath D:\mandala\genesis-os`
- Optional: `release.yml` reparieren (wie `diamond-setup` Trusted Publishing?)

### P1 — UTAC-Batch auf `DiamondPackage` (amoc-utac = Referenz)
**Vendoring zuerst** (haben `src/diamond_setup/`):
1. `beta-clustering-utac`
2. `implosive-origin-utac`
3. `phi-scaling-validator`

**Dann weitere UTACs:** `sandpile-utac`, `seismic-utac`, `neural-avalanche-utac`, …

**Migrations-Checkliste pro Paket:**
1. `class X(DiamondPackage)` + `_run_cycle` / `_build_*` Hooks
2. `NotConvergedError` vor erstem `run_cycle` (kein Auto-Run in `get_*`)
3. `diamond-setup>=2.1.0` in `pyproject.toml`; `src/diamond_setup/` löschen
4. `validate_diamond_instance()` Test
5. Version bump (minor), CHANGELOG, commit, tag, `publish_pypi.ps1`

Prompt-Details: `docs/AuditErgebnisse.txt` (Gemini-Abschnitt)

### P2 — genesis-os Test-Fixes
1. `test_use_plugin_true_without_package_sets_plugin_none` — mock statt fehlendem Paket
2. `test_max_depth_fifo` (AgentMemory) — FIFO-Bug

### P3 — Architektur
- `contracts/` (software / scientific / epistemic) in genesis-os
- CI: Diamond-Validation als GitHub Action (Template aus `diamond-setup/validation.py`)
- 3 Tiers: Core / Scientific / Experimental
- `unified-mandala-demo` reparieren oder aus `full-stack` entfernen

### P4 — Metadata
- `.zenodo.json` committen (falls noch offen)
- `CITATION.cff` ergänzen

---

## Arbeitsmodus für nächste Sessions

| Aufgabe | Wo starten |
|---------|------------|
| Ökosystem, deps, CI-Templates | Workspace `genesis-os` |
| Paket migrieren + publishen | Subrepo + `publish_pypi.ps1` |
| Diamond-Protokoll | `diamond-setup` / `contracts/diamond.interface.yaml` |
| Referenz-UTAC | `amoc-utac` v1.1.0 |
| 48 Repos Batch | genesis-os Handoff + Migrations-Checkliste oben |

**Delegations-Regel:** Agent meldet Workspace-Wechsel; Publish immer über lokales `.env`-Token möglich.

---

## Wichtige Pfade

```
D:\mandala\genesis-os\              # Kommandozentrale, .env (Token), publish-Skripte
D:\mandala\diamond-setup\           # Diamond Protocol v2.1.0 (PyPI)
D:\mandala\amoc-utac\               # Referenz-UTAC v1.1.0 (PyPI)
D:\mandala\                         # 48+ geklonte Repos
D:\mandala\genesis-os\.audit_venv\  # ~1.4 GB — NICHT committen
```

## Import-Namen ≠ PyPI-Namen

| pip install | import |
|-------------|--------|
| `genesisaeon-hexaagent` | `hexa_agent` |
| `genesisaeon-sonification` | `sonification` |
| `beta-clustering-utac` | `beta_clustering` |
| `phi-scaling-validator` | `phi_scaling` |
| `implosive-origin-utac` | `implosive_origin` |
| `genesis-q4-core` | `genesis_q4` |
| `mandala-visualizer` | `mandala_visualizer` |
| `diamond-setup` | `diamond_setup` |
| `amoc-utac` | `amoc_utac` |

---

## Neue Session — Startprompt

```
Kontext: GenesisAeon Ecosystem. Lies docs/SESSION_HANDOFF.md in genesis-os.

Stand (2026-07-01):
- diamond-setup 2.1.0 auf PyPI (DiamondPackage ABC)
- amoc-utac 1.1.0 auf PyPI — Referenz-Migration (erste UTAC)
- genesis-os: main v1.0.2 lokal, PyPI noch 1.0.1; diamond-setup>=2.1.0
- Lokales Publish: genesis-os/.env (Token gesetzt) + scripts/publish_pypi.ps1

Nächster Fokus: [WÄHLEN]
A) genesis-os 1.0.2 PyPI + release.yml fix
B) UTAC-Batch: beta-clustering-utac (Vendoring auflösen)
C) genesis-os Test-Fixes (AgentMemory FIFO, mandala plugin mock)
D) contracts/ + CI Diamond-Validation

Publish-Befehl:
  pwsh D:\mandala\genesis-os\scripts\publish_pypi.ps1 -RepoPath D:\mandala\<repo>

Arbeitsordner: D:\mandala\ — Workspace genesis-os, Subrepos per Pfad.
```

---

*„Tiefe ist Bedingung. CREP ist Bewegung. Das Sigillin ist das Tor.“*