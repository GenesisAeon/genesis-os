# Session Handoff — GenesisAeon · 2026-07-01

> Copy-paste den Block **„Neue Session — Startprompt“** unten in die nächste Cursor/Grok-Session.

---

## Was in dieser Session erledigt wurde

### genesis-os v1.0.1 Release (abgeschlossen)

| Kanal | Status |
|-------|--------|
| **PyPI** | `genesis-os==1.0.1` (LATEST) — `uv publish` erfolgreich |
| **GitHub** | Tag `v1.0.1`, Commit `AuditundFix` |
| **Zenodo** | v1.0.1 — **Description/Notes manuell** aus `.zenodo.json` korrigiert (Texte sagten vorher noch „1.0.0“) |

**pyproject.toml-Fixes (v1.0.1):**
- `mandala-visualize` → `mandala-visualizer` (korrekter PyPI-Name)
- `entropy-table>=2.0.1` (nicht 2.0.2 — existiert nicht auf PyPI)
- `diamond-setup>=1.0.0` (nicht 2.0.0 auf PyPI zum Audit-Zeitpunkt)
- `[full-stack]` = **48** GenesisAeon-Pakete

**README + CHANGELOG** auf v1.0.1 / 48-Pakete-Sync aktualisiert.

### Ecosystem Deep Audit

- Report: `AUDIT_REPORT_v1.0.1.md` (Root)
- Diskussion: `docs/AuditErgebnisse.txt`
- Rohdaten: `test-results/audit_*.json`, `pytest_output.txt`
- **Issue #1 (PyPI hinter Repo)** → **geschlossen**

### Repo-Hygiene

- `.gitignore`: `.audit_venv/`, `terminals/`, `test-results/audit_*`
- `dist/`: alte Wheels (0.1.0, 0.4.2, 1.0.0) entfernt — nur 1.0.1 übrig

### diamond-setup v2.1.0 (lokal, noch nicht publiziert)

**Pfad:** `D:\mandala\diamond-setup`

| Neu | Zweck |
|-----|--------|
| `src/diamond_setup/protocol.py` | `DiamondPackage` ABC, Pydantic-Modelle |
| `src/diamond_setup/validation.py` | `validate_diamond_instance()` für CI |
| `contracts/diamond.interface.yaml` | Maschinenlesbarer Vertrag |
| `tests/test_protocol.py` | 5/5 grün |

**Γ-Regel:** `get_crep_state()` / `get_utac_state()` → `NotConvergedError` vor erstem `run_cycle()` (Γ = Attraktor, nicht Initialwert).

**Noch zu tun:** Commit + `uv build && uv publish` für `diamond-setup==2.1.0`.

---

## Offene Punkte (priorisiert)

### P0 — diamond-setup veröffentlichen
```bash
cd D:\mandala\diamond-setup
uv build && uv publish --token pypi-...
```

### P1 — UTAC-Pakete auf `DiamondPackage` migrieren
- Vendoring von `diamond_setup` in beta-clustering, implosive-origin, phi-scaling **auflösen**
- Echte Dependency: `diamond-setup>=2.1.0`
- Standard-Prompt (siehe `docs/AuditErgebnisse.txt`, Gemini-Abschnitt)

**Batch-Reihenfolge:** erst die 6–8 voll konformen Pakete als Referenz, dann Rest.

### P2 — genesis-os Test-Fixes
1. `test_use_plugin_true_without_package_sets_plugin_none` — mock statt Abwesenheit von `mandala-visualizer`
2. `test_max_depth_fifo` (AgentMemory) — echter FIFO-Bug

### P3 — Architektur (aus AuditErgebnisse.txt)
- `contracts/` Verzeichnis (software / scientific / epistemic)
- CI: Diamond-Validation als GitHub Action
- 3 Tiers: Core / Scientific / Experimental
- `unified-mandala-demo` reparieren oder aus `full-stack` entfernen

### P4 — genesis-os Metadata
- `.zenodo.json` im Repo committen (falls noch offen)
- `CITATION.cff` ergänzen
- `genesis-os` optional: `diamond-setup>=2.1.0` nach Publish

---

## Lokales PyPI-Token (für `uv publish` ohne GitHub Secret)

```bash
# Einmalig: copy .env.example → .env in genesis-os (gitignored)
# PYPI_API_TOKEN / UV_PUBLISH_TOKEN eintragen

pwsh D:\mandala\genesis-os\scripts\publish_pypi.ps1 -RepoPath D:\mandala\<paket>
```

Skript sucht Token in: Repo-`.env` → `genesis-os/.env` → `D:\mandala/.env`.

---

## Arbeitsmodus für nächste Sessions

| Aufgabe | Wo starten |
|---------|------------|
| Ökosystem, deps, CI-Templates | Workspace `genesis-os` |
| `DiamondPackage` vertiefen | `diamond-setup` (oder von genesis-os aus mit absoluten Pfaden) |
| Ein UTAC-Paket migrieren | Workspace → dieses Repo, kurzer Kontext |
| 48 Repos Batch | genesis-os + fester Migrations-Prompt |

**Delegations-Regel:** Agent meldet, wenn Workspace-Wechsel sinnvoller ist.

---

## Wichtige Pfade

```
D:\mandala\genesis-os\          # Kommandozentrale
D:\mandala\diamond-setup\       # Diamond Protocol (v2.1.0 lokal)
D:\mandala\                     # 48+ geklonte Repos
D:\mandala\genesis-os\.audit_venv\  # ~1.4 GB — NICHT committen, optional löschen
```

## Import-Namen ≠ PyPI-Namen (Mapping)

| pip install | import |
|-------------|--------|
| `genesisaeon-hexaagent` | `hexa_agent` |
| `genesisaeon-sonification` | `sonification` |
| `beta-clustering-utac` | `beta_clustering` |
| `phi-scaling-validator` | `phi_scaling` |
| `implosive-origin-utac` | `implosive_origin` |
| `genesis-q4-core` | `genesis_q4` |
| `mandala-visualizer` | `mandala_visualizer` |

---

## Neue Session — Startprompt

```
Kontext: GenesisAeon Ecosystem. Lies docs/SESSION_HANDOFF.md in genesis-os.

Stand:
- genesis-os v1.0.1 auf PyPI/GitHub/Zenodo (Texte sync)
- Audit: AUDIT_REPORT_v1.0.1.md + docs/AuditErgebnisse.txt
- diamond-setup v2.1.0 lokal: DiamondPackage ABC + NotConvergedError (Γ=Attraktor)
  → noch publish auf PyPI

Nächster Fokus: [WÄHLEN]
A) diamond-setup 2.1.0 publish + genesis-os pin bump
B) UTAC-Paket-Migration auf DiamondPackage (start: amoc-utac)
C) genesis-os Test-Fixes (AgentMemory FIFO, mandala plugin mock)
D) contracts/ + CI Diamond-Validation

Arbeitsordner: D:\mandala\ — Workspace genesis-os, Subrepos per Pfad.
```

---

*„Tiefe ist Bedingung. CREP ist Bewegung. Das Sigillin ist das Tor.“*