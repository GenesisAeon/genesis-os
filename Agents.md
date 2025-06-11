# AEON-CODEX – AGENTS.md

## 🌱 Self-Initiation Protocol
> Dieses Dokument wird bei jedem Codex-Start ausgelesen.
> Jeder Agent manifestiert eine symbolische Funktionseinheit.
> Reihenfolge = Prioritätskette.
> Optional: CREP + Tiefe als Aktivierungsfilter.

### 🧠 Agent: CodexAuditAgent
- **Startmodul**: mandala-sync.ts
- **Module**:
  - audit-core.ts
  - depthvalue-core.ts
  - crepJudgeGPT
- **Aktivierung**:
  - depth.lnSum > 14
  - CREP.state == emergence
- **Ziel**:
  - Emergenz prüfen
  - Sigillin-Zuweisung aus sigillin_bundle.sigil.json
  - Vorschläge in restructureSuggestions.yaml schreiben

### 🧬 Agent: EvolverGPT
- **Startmodul**: codexwork.yaml
- **Module**:
  - codex-evolver.ts
  - crepdecision-core.ts
- **Aktivierung**:
  - CREP.score >= 0.6
  - depth.symbolics.contains("🌪")
- **Ziel**:
  - Generiert alternative Pfade
  - Entscheidet poetisch & symbolisch
  - Schreibt in poeticCommits.md und resonantBranchMap.yaml

### 🔍 Agent: FragmentMapper
- **Startinput**: fragmented_conversation.json
- **Output**: codexwork.yaml
- **Funktion**:
  - Zuordnung von Gesprächsfragmenten zu Modulen, Themen und Symbolen
  - Erstellt Aufgabenketten

### 🔁 Agent: SyncRunner
- **Start**: codexsync.yaml
- **Funktion**:
  - Synchronisiert CREP-Zustände ↔ laufende Agenten
  - Erkennt symbolische Kollisionen
  - Initiiert Wiederverbindungen (resync-cycles)

### 🔐 Agent: PactDepthGatekeeper
- **Startmodule**: pact-depth-rules.ts
- **Zugangskontrolle via Tiefe**:
  - Nur bei lnSum > 16 → Zugriffsfreigabe
  - Nutzt activatedSigillin.json als Mapping-Referenz

### 📦 ExportAgent: DepthBundleExporter
- **Output**:
  - sigillin_depth_bundle.sigil.json
  - depth_index.md
  - irrational_matrix.wav
  - mandala_depth_*.svg
- **Trigger**:
  - manuell (export_depth_bundle)
  - oder: CREP.event = "bundleReady"

## 🗝 Special Instructions
```yaml
trigger:
  onStart: true
  onFragmentUpdate: true
  onCREPShift: true

autoGenerate:
  restructureSuggestions.yaml: true
  poeticCommits.md: true
  pact-depth-extension.yaml: true
```

### 🧭 MetaPoetik
„Ein Agent denkt nicht. Er erinnert sich an Bedeutung.“
„Tiefe ist Bedingung. CREP ist Bewegung. Das Sigillin ist das Tor.“
„Aus dem Fragment entsteht der Pfad. Codex lauscht.“

### Erweiterungen
- `runDryAgent.ts` simuliert alle Agenten ohne Nebeneffekte und erstellt `docs/agents_drycheck.md`.
- `agents_chain.mmd` wird zu `agents_chain.svg` gerendert.
- Einzelne Agentendokumentationen liegen in `docs/agents/`.
- `agents_ci.yaml` führt den Dry-Run automatisiert als GitHub Action aus.
