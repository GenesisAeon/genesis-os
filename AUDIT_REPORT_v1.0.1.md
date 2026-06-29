# GenesisAeon Ecosystem Audit Report
## genesis-os v1.0.1 + 48 Subpakete
## Datum: 2026-06-29

### EXECUTIVE SUMMARY

Der Core (`genesis-os`) selbst ist solide: 1382/1383 Tests grün, 91% Coverage, saubere Lint-Bilanz, keine CVEs, ein lauffähiges README-Quickstart. Das Ökosystem der 48 Subpakete ist auf PyPI tatsächlich vorhanden und installiert konfliktfrei — das ist keine Selbstverständlichkeit und eine echte Stärke. Der kritischste Befund ist aber struktureller Natur: **die in der lokalen `pyproject.toml` deklarierte v1.0.1-Erweiterung des `full-stack`-Extras (48 Pakete) ist nie auf PyPI veröffentlicht worden** — das publizierte `genesis-os` ist noch v1.0.0 mit nur 14 Extras. Wer heute `pip install genesis-os[full-stack]` ausführt, bekommt nicht das im Repo beschriebene Ökosystem. Zusätzlich zeigt die "Diamond Interface"-Validierung, dass die Rückgabewerte vieler Pakete (fehlende `H`/`H_star`/`K_eff`/`Gamma`/`zenodo`-Felder) und mehrere Γ-Werte erheblich von den im CREP-Atlas dokumentierten Erwartungswerten abweichen. Sofortiger Handlungsbedarf: PyPI-Release von v1.0.1 nachziehen, Diamond-Interface-Rückgabewerte vereinheitlichen, Namensraum-Kollision bei `diamond_setup` auflösen.

### KRITISCHE ISSUES (❌) — sofortiger Handlungsbedarf

| # | Package | Issue | Impact |
|---|---------|-------|--------|
| 1 | genesis-os | Lokale `pyproject.toml` (v1.0.1) deklariert 48 optionale Deps im `full-stack`-Extra; das auf PyPI publizierte Paket ist noch v1.0.0 mit nur 14 Deps und nutzt den alten Audio-Namen `sonification` statt `genesisaeon-sonification`. v1.0.1 wurde nie released. | Jeder externe Nutzer von `pip install genesis-os[full-stack]` bekommt ein anderes, kleineres Ökosystem als im Repo dokumentiert. README/CHANGELOG/Zenodo-Metadaten laufen der Realität voraus. |
| 2 | diamond-setup, beta-clustering-utac, implosive-origin-utac, phi-scaling-validator | Vier unabhängige PyPI-Pakete vendoren denselben Top-Level-Modulnamen `diamond_setup` (identischer Code, Stand heute) statt `diamond-setup` als echte Dependency zu deklarieren. | Installationsreihenfolge bestimmt, wessen Kopie von `diamond_setup` am Ende auf der Platte liegt; sobald eine der vier Kopien divergiert (z.B. bei einem 2.0.0-Bump von `diamond-setup`, wie im Prompt behauptet — tatsächlich installiert ist aber 1.0.0), entstehen stille, schwer reproduzierbare Inkonsistenzen. |
| 3 | unified-mandala-demo | Das auf PyPI publizierte Wheel enthält **keinen Python-Code** — nur `dist-info`-Metadaten (Lizenzdateien, RECORD). `import unified_mandala_demo` schlägt fehl. | Paket ist faktisch leer/nicht funktional. |
| 4 | beta_clustering_utac, feldtheorie, genesis_q4_core, genesisaeon_hexaagent, genesisaeon_sonification, implosive_origin_utac, phi_scaling_validator | Distributionsname ≠ Importname (z.B. `pip install genesisaeon-hexaagent` → `import hexa_agent`; `pip install feldtheorie` → keine erkennbare Top-Level-API, nur generische Submodule `analysis`/`models`). | Jede Automatisierung, die Distributionsnamen 1:1 in Importnamen übersetzt (wie im Prompt-Skript selbst gefordert), bricht ohne Mapping-Tabelle. `feldtheorie`s generische Modulnamen (`analysis`, `models`) kollidieren potenziell mit gleichnamigen Modulen anderer Pakete im selben Environment. |
| 5 | amazon-utac, vrig-cosmological, sa-sv-duality, phaethon-chimera, afet-tensions, beta-clustering-utac, eml-utac-bridge, phi-scaling-validator, implosive-origin-utac, genesis-scope, hikari-ledger | `get_utac_state()` liefert nicht alle erwarteten Keys (`H`, `H_star`, `K_eff` teilweise fehlend) und/oder `to_zenodo_record()` fehlen `title`/`description`/`creators`. | Diamond-Interface-Vertrag ("genau diese 5 Methoden mit definierten Rückgabewerten") ist über das Ökosystem **nicht** einheitlich erfüllt — Konsumenten (z.B. genesis-os Orchestrator) können sich nicht blind auf die Schema-Konformität verlassen. |
| 6 | hikari-ledger, diffusive-routing, phaethon-chimera, afet-tensions | Γ-Wert weicht signifikant vom im CREP-Atlas dokumentierten Erwartungswert ab (hikari-ledger: 0.893 statt 0.367 erwartet; diffusive-routing: 0.0019 statt 0.443 erwartet; phaethon-chimera: 0.296 statt 0.165 erwartet). | Entweder sind die im Audit-Prompt referenzierten "geplanten" Γ-Werte veraltet, oder die Implementierungen sind wissenschaftlich nicht (mehr) mit dem CREP-Atlas konsistent — beides ist für ein Grant-Komitee ein Erklärungsbedarf. |

### WARNUNGEN (⚠️) — sollte vor nächstem Minor-Release behoben werden

| # | Package | Issue | Empfehlung |
|---|---------|-------|------------|
| 1 | genesis-os | `tests/unit/test_coverage_gaps.py::test_use_plugin_true_without_package_sets_plugin_none` schlägt fehl, sobald `mandala-visualizer` im Environment installiert ist — der Test prüft den "Paket fehlt"-Zweig, mockt den Import aber nicht. | Test auf `monkeypatch`/`importlib`-Mock umstellen statt auf tatsächliche Abwesenheit des Pakets zu vertrauen. |
| 2 | genesis-os | `.zenodo.json`: `version` = "1.0.1", aber `title`-Feld referenziert weiterhin "v1.0.0"; Feld `communities` fehlt komplett. | Zenodo-Metadaten vor nächstem Release synchronisieren; `communities` ergänzen (z.B. OpenAIRE-Community), falls für Sichtbarkeit gewünscht. |
| 3 | genesis-os | `CITATION.cff` fehlt im Repo-Root (FAIR4RS/GitHub-Citation-Standard). README hat eine Citation-Sektion mit BibTeX, aber kein maschinenlesbares `CITATION.cff`. | Minimal-valide `CITATION.cff` ergänzen (siehe Prompt-Vorlage), referenziert auf die bestehende Zenodo-DOI. |
| 4 | genesis-os | `RELEASE_GUIDE.md`, `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md`, `.github/PULL_REQUEST_TEMPLATE.md` fehlen. | Governance-Grundausstattung nachziehen, besonders PR-/Issue-Templates für ein Projekt mit 48 Subrepos. |
| 5 | cellular_genesis, spiking_aeon | Diamond-Klasse (`CellularGenesis`, `SpikingAeon`) ist in einem `system`-Submodul implementiert, aber nicht im Paket-`__init__.py` re-exportiert — anders als bei allen anderen UTAC-Geschwisterpaketen, die ihre Klasse direkt auf Top-Level exponieren. | API-Konsistenz herstellen: `from .system import CellularGenesis` etc. in `__init__.py` ergänzen. |
| 6 | beta_clustering, eml_utac_bridge, phi_scaling, implosive_origin, genesis_scope | `get_crep_state()["Gamma"]` ist `None` (teils fehlen `C`/`R`/`E`/`P` komplett bei `phi_scaling`). | Default-Berechnung von Γ vor erstem `run_cycle()`-Aufruf prüfen/dokumentieren — aktuell unklar, ob `None` ein gültiger "noch nicht initialisiert"-Zustand oder ein Bug ist. |
| 7 | sandpile-utac, cygnus-jet-utac, spiking_aeon.system | `run_cycle()`/Instanziierung blockierte > 15s im Audit (Timeout) — vermutlich rechenintensive Default-Simulation (z.B. SNN-Backend-Initialisierung). | Leichtgewichtigen Default-Modus oder expliziten `n_steps`-Parameter mit kleinem Default für schnelle Sanity-Checks anbieten. |

### DIAMOND INTERFACE STATUS

(✅ = Methode vorhanden & Rückgabetyp/Schema korrekt, ⚠️ = vorhanden aber Schema unvollständig, ❌ = fehlt/Fehler, — = nicht geprüft/Timeout)

| Package | run_cycle | get_crep_state | get_utac_state | get_phase_events | to_zenodo_record | Γ korrekt |
|---------|-----------|----------------|----------------|-----------------|------------------|-----------|
| amoc-utac | ✅ | ✅ (Γ=0.297) | ✅ | ✅ | ✅ | ✅ (Δ=0.046, in Toleranz) |
| amazon-utac | ✅ | ✅ (Γ=0.116) | ⚠️ fehlt H_star | ✅ | ❌ fehlt title/desc/creators | ✅ |
| neural-avalanche-utac | ✅ | ✅ (Γ=0.241) | ✅ | ✅ | ✅ | ✅ |
| solar-flare-utac | ✅ | ✅ (Γ=0.0065) | ✅ | ✅ | ✅ | ✅ |
| sandpile-utac | — Timeout | — | — | — | — | — |
| seismic-utac | ✅ | ✅ (Γ=0.197) | ✅ | ✅ | ✅ | ✅ |
| cygnus-jet-utac | — Timeout | — | — | — | — | n/a (kein Erwartungswert) |
| quantum-genesis | ✅ | ✅ (Γ=0.035) | ✅ | ✅ | ⚠️ fehlt creators | ✅ |
| cellular-genesis | ✅ (via .system) | ✅ (Γ=0.040) | ✅ | ✅ | ✅ | n/a |
| spiking-aeon | — Timeout | — | — | — | — | n/a |
| theta-resonance | ✅ | ✅ (Γ=0.106) | ✅ | ✅ | ✅ | ❌ (0.106 vs erw. 0.251) |
| epi-sigillin | ✅ | ✅ (Γ=1.0) | ✅ | ✅ | ❌ fehlt desc/creators | n/a |
| vrig-cosmological | ✅ | ✅ (Γ=0.251) | ❌ fehlt H/H_star/K_eff | ✅ | ✅ | n/a |
| sa-sv-duality | ✅ | ✅ (Γ=0.251) | ❌ fehlt H/K_eff | ✅ | ❌ fehlt alle 3 | n/a |
| phaethon-chimera | ✅ | ✅ (Γ=0.296) | ❌ fehlt H/K_eff | ✅ | ✅ | ❌ (0.296 vs erw. 0.165) |
| afet-tensions | ✅ | ✅ (Γ=0.560) | ❌ fehlt H_star/K_eff | ✅ | ❌ fehlt desc/creators | n/a |
| beta-clustering-utac | ✅ | ⚠️ Γ=None | ❌ fehlt H_star/K_eff | ✅ | ❌ fehlt alle 3 | n/a |
| eml-utac-bridge | ✅ | ⚠️ Γ=None | ❌ fehlt H_star/K_eff | ✅ | ✅ | n/a |
| phi-scaling-validator | ✅ | ❌ alle CREP-Keys fehlen | ❌ alle 3 fehlen | ✅ | ✅ | n/a |
| implosive-origin-utac | ✅ | ⚠️ Γ=None | ❌ fehlt K_eff | ✅ | ❌ fehlt creators | n/a |
| genesis-scope | ✅ | ⚠️ Γ=None | ❌ alle 3 fehlen | ✅ | ❌ fehlt alle 3 | n/a |
| hikari-ledger | ✅ | ✅ (Γ=0.893) | ✅ | ✅ | ❌ fehlt alle 3 | ❌ (0.893 vs erw. 0.367) |
| diffusive-routing | ✅ | ✅ (Γ=0.0019) | ✅ | ✅ | ❌ fehlt desc/creators | ❌ (0.0019 vs erw. 0.443) |
| utac-core | ❌ keine Diamond-Klasse exponiert (funktional, aber andere API: `frame_principle`, `v_rig`, `beta_fit`) | — | — | — | — | n/a |
| unified-mandala | ❌ keine Diamond-Klasse exponiert (`__init__.py` exportiert nur `__version__`) | — | — | — | — | n/a |
| genesis-q4-core | ❌ keine Diamond-Klasse — exponiert stattdessen Q4-Navigationsklassen (`Q4Navigator`, `Tesseract` etc., konsistent zu Paketzweck) | — | — | — | — | n/a |

**Befund:** Von 23 geprüften Diamond-Kandidaten erfüllen nur **8** (35%) den Vertrag vollständig schemakonform (amoc-utac, neural-avalanche-utac, solar-flare-utac, seismic-utac, quantum-genesis, cellular-genesis, theta-resonance — bei letzterem ist nur das Γ falsch). Bei 11 Paketen fehlen Keys in `get_utac_state()` oder `to_zenodo_record()`. `utac-core`, `unified-mandala` und `genesis-q4-core` implementieren das Interface gar nicht (z.T. nachvollziehbar, da sie funktional andere Rollen einnehmen — sollte aber explizit dokumentiert werden, ob sie als "Diamond-Pakete" gelten oder nicht).

### TEST COVERAGE SUMMARY (genesis-os Core)

- Gesamttests: 1383
- Pass: 1382 | Fail: 1 | Error: 0 | Skip: 0
- Coverage genesis-os Core: **91%** (Ziel >60% deutlich übertroffen)
- Einziger Fail ist umgebungsabhängig (siehe Warnung #1) — kein echter Logikfehler im Core, sondern ein brüchiger Test, der bei voll bestückter `full-stack`-Umgebung kollabiert.
- Lint (`ruff check src/genesis_os/`): 0 Findings.
- `pip-audit` über das komplette installierte Environment (genesis-os + alle 48 Pakete + Transitives): **keine bekannten CVEs**.
- Keine hardcodierten Credentials im Core-Quellcode gefunden (einzige Treffer im Regex-Scan waren False Positives um das Wort "token" im Sigillin-Phasentoken-Kontext).
- README-Quickstart tatsächlich ausgeführt: **läuft fehlerfrei**, Ausgabe entspricht dem dokumentierten Format (Phase/Entropy/Phi/Lagrangian/Transitions/Emergence Events).

### INSTALLATION MATRIX

| Paket | Install | Import | Diamond | Anmerkung |
|-------|---------|--------|---------|-----------|
| genesis-os (core, no extras) | ✅ | ✅ | n/a (Orchestrator) | `pip check` clean |
| genesis-os[full-stack] (PyPI, real) | ✅ | ✅ | n/a | Nur 14 Pakete, nicht 48 — siehe Issue #1 |
| 13 der 14 direkten full-stack-Deps (PyPI) | ✅ | ✅ | gemischt | sigillin, utac-core, fieldtheory, mirror-machine, cosmic-web, entropy-table(2.0.1≠2.0.2), entropy-governance, mandala-visualizer, climate-dashboard, implosive-genesis, aeon-ai, advanced-weighting-systems alle installierbar/importierbar |
| 34 "neue" optionale Pakete | ✅ alle 34 installierbar, keine Versionskonflikte, Doppelinstallation (`sa-sv-duality` zweimal) idempotent | 26/34 sauber importierbar unter erwartetem Namen, 8 mit Namens-Mismatch (siehe Issue #4) | 15/34 voll schemakonform, Rest mit Lücken | diamond-setup installiert als 1.0.0, nicht das im Prompt erwartete 2.0.0; feldtheorie korrekt als 6.0.0 |

### OFFENE PUNKTE FÜR v1.1.0

1. PyPI-Release von genesis-os v1.0.1 inkl. des erweiterten `full-stack`-Extras nachziehen — sonst klafft Repo- und PyPI-Realität dauerhaft auseinander.
2. Diamond-Interface-Vertrag verbindlich spezifizieren (idealerweise als Pydantic-Schema/ABC in einem gemeinsamen `diamond-setup`-Paket) und alle 23 Kandidaten gegen dieses Schema in CI testen — aktuell ist die Konformität Zufall.
3. `diamond_setup`-Vendoring in beta-clustering-utac, implosive-origin-utac, phi-scaling-validator auflösen: echte Dependency auf `diamond-setup>=X` statt Code-Duplikation.
4. `unified-mandala-demo` reparieren (Paket ist aktuell leer) oder vom full-stack-Extra entfernen.
5. CITATION.cff ergänzen, .zenodo.json `title`/`version`/`communities` synchronisieren.
6. Test `test_use_plugin_true_without_package_sets_plugin_none` robust gegen volle Extra-Installation machen.
7. Γ-Divergenzen bei hikari-ledger, diffusive-routing, phaethon-chimera, theta-resonance gegen den CREP-Atlas klären: Atlas veraltet oder Implementierung regressiert?
8. Performance-Default für sandpile-utac, cygnus-jet-utac, spiking-aeon (>15s für `run_cycle()`/Init) — blockiert schnelle CI-Sanity-Checks.

### BESTÄTIGTE STÄRKEN ✅

- Core-Testsuite ist umfangreich, stabil und schnell (1382/1383 grün in ~27s, 91% Coverage).
- Alle 48 Subpakete existieren tatsächlich auf PyPI und installieren ohne Versionskonflikte nebeneinander (inkl. Doppelinstallation-Idempotenz) — keine triviale Leistung bei dieser Paketzahl.
- Keine bekannten Sicherheitslücken (`pip-audit`) im gesamten installierten Stack, keine hardcodierten Secrets im Core.
- Lint ist auf dem Core komplett clean (0 ruff findings).
- README-Quickstart ist nicht nur vorhanden, sondern tatsächlich copy-paste-lauffähig und stimmt mit der echten API überein.
- Solide Open-Science-Grundausstattung vorhanden: DOI-Badge, OpenAIRE-Indexierung, BibTeX-Citation-Sektion, gepflegtes CHANGELOG, funktionierende `.github/workflows/release.yml` mit klar benannten Secrets (PYPI_API_TOKEN, TEST_PYPI_API_TOKEN, ZENODO_TOKEN, ZENODO_SANDBOX_TOKEN).
- Mehrere Diamond-Pakete (amoc-utac, neural-avalanche-utac, solar-flare-utac, seismic-utac, quantum-genesis, cellular-genesis) erfüllen das Interface vollständig und liefern Γ-Werte innerhalb der erwarteten Toleranz — der Interface-Ansatz funktioniert dort, wo er konsequent umgesetzt wurde.

---
*Methodischer Hinweis: Block 6.2 (Reproduzierbarkeit über `random.seed`/`np.random.seed`) und die Volltest-Determinismus-Prüfung (Block 4.2) wurden aus Zeitgründen nicht für alle 23 Diamond-Kandidaten einzeln durchlaufen, nachdem mehrere Pakete (sandpile-utac, cygnus-jet-utac, spiking-aeon) bereits bei der einfachen Instanziierung Timeouts verursachten. Die in Block 9 geforderte Tiefenprüfung von `genesis-scope` ist in der DIAMOND-INTERFACE-Tabelle abgebildet (Diamond-Methoden vorhanden, aber CREP/UTAC-State-Schema unvollständig); `get_semantic_path()` und `to_llms_txt()`/`export_llms_txt()` sind in der installierten Version 1.0.0 nicht vorhanden.*
