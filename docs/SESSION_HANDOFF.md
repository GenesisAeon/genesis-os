# Session Handoff — GenesisAeon · 2026-07-01 (Update 3)

> Copy-paste den Block **„Neue Session — Startprompt“** unten in die nächste Cursor/Grok-Session.

---

## Was in dieser Session erledigt wurde

### Releases (PyPI)

| Paket | Version | Kanal | Notizen |
|-------|---------|-------|---------|
| **diamond-setup** | 2.1.0 | PyPI + GH `v2.1.0` | DiamondPackage ABC, Trusted Publishing |
| **genesis-os** | 1.0.2 | PyPI LATEST + GH `v1.0.2` | `diamond-setup>=2.1.0`; Wheel-Nachzug nach dist-Mix |
| **amoc-utac** | 1.1.0 | PyPI + GH `v1.1.0` | Erste Diamond-Referenz-UTAC |

### Lokales Publish-Infrastruktur

| Artefakt | Status |
|----------|--------|
| `.env.example` | committet |
| `.env` | **gitignored**, Token gesetzt (`PYPI_API_TOKEN` = `UV_PUBLISH_TOKEN`) |
| `scripts/publish_pypi.ps1` / `.sh` | `dist/` clean → build → **explizite** Artefakte |

```powershell
pwsh D:\mandala\genesis-os\scripts\publish_pypi.ps1 -RepoPath D:\mandala\<repo>
pwsh D:\mandala\genesis-os\scripts\publish_pypi.ps1 -RepoPath D:\mandala\<repo> -DryRun
```

**Publish-Falle (gelöst):** Alte `dist/*` (z. B. 1.0.1 + 1.0.2 gemischt) → fehlendes Wheel.
Skript leert `dist/` vor Build. Bei Speicherplatz-Mangel: `python -m build --wheel --outdir dist`.

**Token-Ort:** `.env` in genesis-os — **nicht** in `.venv` / `.audit_venv`.

### amoc-utac v1.1.0 — Referenz-Migration

- `AmocUTAC(DiamondPackage)`, Vendoring `src/diamond_setup/` entfernt
- `diamond-setup>=2.1.0`, `NotConvergedError`, `validate_diamond_instance()` grün
- Vorlage: `amoc_utac/system.py`, `tests/test_diamond_interface.py`

### genesis-os Kleinigkeiten (main, noch nicht 1.0.3 auf PyPI)

- **P2 teilweise:** `AgentMemory` FIFO-Fix (`sequence` in Sigillin-Content)
- **P2 teilweise:** Mandala-Plugin-Test mit `patch.dict` (mock statt installiertem Paket)
- README + `.zenodo.json` → v1.0.2

### Aus früherer Session (weiterhin gültig)

- Audit: `AUDIT_REPORT_v1.0.1.md`, `docs/AuditErgebnisse.txt`
- `[full-stack]` = 48 Pakete

---

## Offene Punkte (priorisiert)

### P0 — genesis-os 1.0.3 patch (optional)
- FIFO + Test-Fixes auf `main` → Version bump + `publish_pypi.ps1`
- `release.yml` reparieren (schlägt fehl, 0 Jobs) oder nur lokales Publish nutzen

### P1 — UTAC-Batch (amoc-utac = Referenz)

**Vendoring zuerst:**
1. `beta-clustering-utac`
2. `implosive-origin-utac`
3. `phi-scaling-validator`

**Checkliste pro Paket:**
1. `class X(DiamondPackage)` + `_run_cycle` / `_build_*`
2. `NotConvergedError` — kein Auto-Run in `get_*`
3. `diamond-setup>=2.1.0`; `src/diamond_setup/` löschen
4. `validate_diamond_instance()` Test
5. minor bump, CHANGELOG, tag, `publish_pypi.ps1`

### P2 — genesis-os (rest)
- Weitere Test-/CI-Themen aus Audit

### P3 — Architektur
- `contracts/` + CI Diamond-Validation
- `unified-mandala-demo` reparieren oder aus `full-stack` entfernen

### P4 — Metadata
- `CITATION.cff` ergänzen

---

## Arbeitsmodus

| Aufgabe | Wo |
|---------|-----|
| Publish / Propagate | `publish_pypi.ps1` + `.env` |
| UTAC migrieren | Subrepo, Vorlage `amoc-utac` |
| Ökosystem / Audit | `genesis-os` |

---

## Wichtige Pfade

```
D:\mandala\genesis-os\          # Kommandozentrale, .env, publish-Skripte
D:\mandala\diamond-setup\       # Diamond Protocol v2.1.0
D:\mandala\amoc-utac\           # Referenz-UTAC v1.1.0
D:\mandala\                     # 48+ Repos
```

## Import ≠ PyPI

| pip install | import |
|-------------|--------|
| `diamond-setup` | `diamond_setup` |
| `amoc-utac` | `amoc_utac` |
| `mandala-visualizer` | `mandala_visualizer` |
| `genesisaeon-hexaagent` | `hexa_agent` |
| `beta-clustering-utac` | `beta_clustering` |
| `implosive-origin-utac` | `implosive_origin` |
| `phi-scaling-validator` | `phi_scaling` |

---

## Neue Session — Startprompt

```
Kontext: GenesisAeon. Lies docs/SESSION_HANDOFF.md in genesis-os.

Stand (2026-07-01, Update 3):
- PyPI: diamond-setup 2.1.0, genesis-os 1.0.2, amoc-utac 1.1.0
- Lokales Publish: genesis-os/.env + scripts/publish_pypi.ps1 (dist clean!)
- Referenz-UTAC: amoc-utac 1.1.0 (DiamondPackage)
- main: FIFO + Test-Fixes (unreleased → 1.0.3)

Nächster Fokus: [WÄHLEN]
A) genesis-os 1.0.3 publish (FIFO-Fixes)
B) UTAC-Batch: beta-clustering-utac
C) release.yml reparieren
D) contracts/ + CI Diamond-Validation

Publish:
  pwsh D:\mandala\genesis-os\scripts\publish_pypi.ps1 -RepoPath D:\mandala\<repo>

Arbeitsordner: D:\mandala\ — Workspace genesis-os.
```

---

*„Tiefe ist Bedingung. CREP ist Bewegung. Das Sigillin ist das Tor.“*