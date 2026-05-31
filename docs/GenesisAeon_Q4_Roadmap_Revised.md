╔══════════════════════════════════════════════════════════════════════════════╗
║  GenesisAeon — Revidierte Integrations-Roadmap Q4-Zustandsraum            ║
║  Basierend auf: Kollaborations-Session (LeChat/Mistral + ChatGPT + Gemini) ║
║  Review & Korrektur: Claude Code · claude-sonnet-4-6                       ║
║  Johann Römer · MOR Research Collective · Mai 2026                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

══════════════════════════════════════════════════════════════════════════════
PRÄAMBEL — Was sich gegenüber dem Ursprungsdokument geändert hat
══════════════════════════════════════════════════════════════════════════════

HAUPTKORREKTUR:
  Der ursprüngliche Plan sah 7 neue Repos vor.
  Diese Roadmap reduziert auf 2 neue Repos + 1 Umbenennung.
  Alles andere wird in bestehende Repos integriert.

WARUM WENIGER REPOS:
  Die GenesisAeon-Organisation hat bereits ~30 Repos.
  Jedes neue Repo = eigene CI, Versionierung, pyproject.toml,
  Kompatibilitäts-Matrix. Das kostet mehr als es bringt.
  Weniger Repos → mehr Kohärenz. (Was CREP-technisch auch höheres C ergibt.)

WHAT ALREADY EXISTS (Ursprungsplan unterschätzt dies):
  genesis-os/src/genesis_os/core/crep.py          → CREPScore-Datenmodell
  genesis-os/src/genesis_os/core/crep_engine.py   → Empirische CREP-Metriken
  genesis-os/src/genesis_os/runtime/nats_publisher.py → NATS-Integration
  genesis-os/src/genesis_os/aeon/agents.py        → Agent-Basisarchitektur
  GenesisAeon/sigillin                            → Sigillin-Repo (existiert)
  GenesisAeon/unified-mandala                     → Mandala-UI (existiert)
  GenesisAeon/diamond-setup                       → Diamond-Basis (existiert)
  GenesisAeon/HexaAgent                           → Agent-Infrastruktur

══════════════════════════════════════════════════════════════════════════════
TEIL 1: MATHEMATISCHE KORREKTUREN — Alle bestätigt korrekt
══════════════════════════════════════════════════════════════════════════════

DIESE KORREKTUREN GELTEN IN ALLEN REPOS, DOCS UND KOMMENTAREN:

  FALSCH:  "16 Zustände = 16 Bit"
  RICHTIG: 16 Zustände = 4 Bit  (H = log₂(16) = 4 Bit)

  FALSCH:  "1/16 der Information = 1 Bit"
  RICHTIG: 1 Zustand mit p=1/16 trägt 4 Bit Selbst-Information

  FALSCH:  "Φ liegt zwischen √2 und π/2"
  RICHTIG: Φ ≈ 1.618 > π/2 ≈ 1.571 > √2 ≈ 1.414

  FALSCH:  Direkte Verbindung continuous CREP → Q4-Zustand
  RICHTIG: Immer via Threshold-Mapping (Q4Mapper)

  HINWEIS: In Code immer:
    PHI_APPROX = 1.6  # Engineering-Näherung, NICHT exakt Φ = 1.6180339...

  GRAU-CODE (korrekte Darstellung):
    g(n) = n XOR (n >> 1)
    Hamming-Distanz zwischen aufeinanderfolgenden Gray-Codes = 1
    Gray-Order: [0,1,3,2,6,7,5,4,12,13,15,14,10,11,9,8]

  TESSERAKT (korrekte Topologie, KEINE Bewusstseinsaussage):
    Ecken:  16  (= die 16 Q4-Zustände)
    Kanten: 32  (= gültige 1-Bit-Übergänge)
    Flächen: 24 (= 2-Bit-Ähnlichkeitsgruppen)
    Zellen:  8  (= 3-Bit-Teilräume)
    → Das ist eine mathematische Graph-Topologie. Punkt.

══════════════════════════════════════════════════════════════════════════════
TEIL 2: REPO-ENTSCHEIDUNGSMATRIX
══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────┬──────────────────┬──────────────────────────┐
│ Modul / Feature             │ Entscheidung     │ Ziel                     │
├─────────────────────────────┼──────────────────┼──────────────────────────┤
│ Q4State, GrayCode,          │ NEUES REPO ✓     │ genesis-q4-core          │
│ Tesserakt-Topologie,        │                  │ (leichtgewichtig,        │
│ Q4TransitionValidator       │                  │  keine GenesisAeon-Deps) │
├─────────────────────────────┼──────────────────┼──────────────────────────┤
│ EFC / Ephaptische           │ NEUES REPO ✓     │ efc-research-module      │
│ Frame-Kopplung (spekulativ) │                  │ (isoliert von Produktion)│
├─────────────────────────────┼──────────────────┼──────────────────────────┤
│ Sigillin-Schema             │ UMBENENNUNG ✓    │ sigillin → gleicher Repo,│
│ (deterministisch, SHA256,   │ (kein neues Repo)│ neue Untermodule         │
│  Lineage, Versionierung)    │                  │                          │
├─────────────────────────────┼──────────────────┼──────────────────────────┤
│ Q4Mapper (CREP → Q4)        │ IN genesis-os ✓  │ core/q4_mapper.py        │
│ ThresholdCrossingDetector   │ (kein neues Repo)│ core/q4_state.py         │
│ Q4State-Brücke              │                  │ core/gray_code.py        │
├─────────────────────────────┼──────────────────┼──────────────────────────┤
│ ga.frame.* NATS-Subjects    │ IN genesis-os ✓  │ runtime/nats_publisher.py│
│ (16 Frame-Subjects)         │ (Migration)      │ (erweitern, nicht neu)   │
│ PolicyGate (Gray-Code)      │                  │                          │
├─────────────────────────────┼──────────────────┼──────────────────────────┤
│ GrayGrid, HypercubeView,    │ IN unified-      │ Neue Komponenten in      │
│ CREPOverlay, NATSMonitor    │ mandala ✓        │ bestehendem Repo         │
├─────────────────────────────┼──────────────────┼──────────────────────────┤
│ Coordinator/Transform/      │ IN genesis-os +  │ aeon/agents.py erweitern │
│ Philosophy/UIAgent,         │ HexaAgent ✓      │ + HexaAgent-Integration  │
│ AgentLoop, AgentMemory      │ (kein neues Repo)│                          │
├─────────────────────────────┼──────────────────┼──────────────────────────┤
│ Diamond Runtime YAML-       │ IN diamond-setup │ contracts/ Verzeichnis   │
│ Contract, AdapterLoader     │ ✓ (kein neues    │ in bestehendem Repo      │
│ Layer-Registry              │  Repo)           │                          │
└─────────────────────────────┴──────────────────┴──────────────────────────┘

══════════════════════════════════════════════════════════════════════════════
TEIL 3: KORRIGIERTE IMPLEMENTIERUNGS-TIMELINE
══════════════════════════════════════════════════════════════════════════════

GEÄNDERTE REIHENFOLGE:
  Original: Phase 0 (diamond-runtime) zuerst
  Korrekt:  Phase 1 (genesis-q4-core) zuerst
  Begründung: Q4-Core hat null externe Abhängigkeiten und ist das
  mathematische Fundament — diamond-runtime YAML-Validator braucht
  alle anderen Layer fertig, bevor er sinnvoll validieren kann.

TIMELINE:
  WOCHE 1-2:  genesis-q4-core               [NEUES REPO]
  WOCHE 2-3:  genesis-os Q4-Module          [IN genesis-os]
  WOCHE 3-4:  genesis-os NATS-Migration     [IN genesis-os]
  WOCHE 4-5:  sigillin SHA256 + Schema      [IN sigillin-Repo]
  WOCHE 5-7:  unified-mandala GrayGrid      [IN unified-mandala]
  WOCHE 7-9:  genesis-os Agent-Rollen       [IN genesis-os + HexaAgent]
  WOCHE 9-10: diamond-setup contracts/      [IN diamond-setup]
  PARALLEL:   efc-research-module           [NEUES REPO, kein Deadline]

██████████████████████████████████████████████████████████████████████████████
PHASE 1 — genesis-q4-core
16-Zustandsraum + Gray-Code + Tesserakt-Topologie
NEUES REPO — HÖCHSTE PRIORITÄT
██████████████████████████████████████████████████████████████████████████████

PROMPT FÜR CLAUDE CODE (genesis-q4-core):

  MISSION
  Implementiere den mathematisch präzisen 16-Zustandsraum als eigenständiges,
  voll getestetes Modul. Keine Abhängigkeiten auf andere GenesisAeon-Repos.
  Der Tesserakt ist ein 4D-Hyperwürfel mit 16 Ecken — eine topologische
  Datenstruktur, keine metaphysische Aussage.

  MATHEMATISCHE GRUNDLAGEN (alle verifiziert):
    16 Zustände = 4 Bit (NICHT 16 Bit)
    Shannon-Entropie: H = log₂(16) = 4 Bit (Gleichverteilung)
    Gray-Code: g(n) = n XOR (n >> 1)
    Hamming-Distanz aufeinanderfolgender Gray-Codes: immer = 1
    Tesserakt: 16 Ecken, 32 Kanten, 24 Flächen, 8 Zellen

  CREATE REPOSITORY: genesis-q4-core

  STRUKTUR:
    genesis-q4-core/
    ├── README.md
    ├── pyproject.toml
    ├── package.json            # TypeScript types (dual)
    ├── CITATION.cff
    ├── genesis_q4/
    │   ├── __init__.py
    │   ├── state.py            # Q4State dataclass
    │   ├── gray_code.py        # Gray-Code Encoding/Decoding
    │   ├── tesseract.py        # 4D Hypercube als Graph-Topologie
    │   ├── transitions.py      # Übergangs-Validator
    │   ├── navigator.py        # Kürzester Gray-Pfad zwischen Zuständen
    │   ├── serializer.py       # JSON/YAML Export
    │   └── constants.py
    ├── typescript/
    │   └── src/
    │       ├── Q4State.ts
    │       ├── grayCode.ts
    │       └── hypercube.ts
    ├── notebooks/
    │   ├── 01_q4_overview.ipynb
    │   └── 02_gray_code_analysis.ipynb
    └── tests/
        ├── test_state.py
        ├── test_gray_code.py       # Hamming=1 Invariante
        ├── test_tesseract.py
        ├── test_transitions.py
        └── test_serializer.py

  SCHLÜSSELKLASSEN:

    @dataclass(frozen=True)
    class Q4State:
        """4-Bit Zustand im GenesisAeon Q4-Zustandsraum.

        Felder:
          C: int  # 0 oder 1 (Kohärenz-Flag)
          R: int  # 0 oder 1 (Resonanz-Flag)
          E: int  # 0 oder 1 (Emergenz-Flag)
          P: int  # 0 oder 1 (Poetik-Flag)

        Properties:
          id:          int   # 0..15, berechnet als 8*C + 4*R + 2*E + P
          binary:      str   # "0000" bis "1111"
          gray_id:     int   # Gray-kodierte ID
          entropy_bits: float # Immer 4.0 bei Gleichverteilung

        INVARIANTE: 16 Zustände = 4 Bit. Nicht 16 Bit.
        """
        C: int
        R: int
        E: int
        P: int

        @property
        def id(self) -> int:
            return 8 * self.C + 4 * self.R + 2 * self.E + self.P

        @property
        def binary(self) -> str:
            return f"{self.id:04b}"

        @property
        def gray_id(self) -> int:
            return self.id ^ (self.id >> 1)

        @property
        def entropy_bits(self) -> float:
            return 4.0  # log₂(16) = 4 Bit bei Gleichverteilung

    class GrayCode:
        """Gray-Code Encoding für Q4-Zustandsübergänge.

        KERN-INVARIANTE:
          hamming_distance(gray(n), gray(n+1)) == 1  für alle n in 0..14
          → Sichert Einzelbit-Übergänge zwischen benachbarten Q4-Zuständen.

        Tests MÜSSEN diese Invariante für alle 15 Paare prüfen.
        """
        @staticmethod
        def encode(n: int) -> int:
            return n ^ (n >> 1)

        @staticmethod
        def decode(g: int) -> int:
            # Inverse Gray-Code
            mask = g >> 1
            while mask:
                g ^= mask
                mask >>= 1
            return g

        @staticmethod
        def hamming_distance(a: int, b: int) -> int:
            return bin(a ^ b).count('1')

        @staticmethod
        def validate_sequence(states: list[int]) -> bool:
            """Alle aufeinanderfolgenden Zustände haben Hamming-Distanz = 1."""
            return all(
                GrayCode.hamming_distance(
                    GrayCode.encode(states[i]),
                    GrayCode.encode(states[i+1])
                ) == 1
                for i in range(len(states) - 1)
            )

    class Tesseract:
        """4D-Hyperwürfel als topologische Basis des Q4-Zustandsraums.

        Properties:
          vertices: 16  (= die 16 Q4-Zustände)
          edges:    32  (= gültige 1-Bit-Übergänge)
          faces:    24  (= 2-Bit-Ähnlichkeitsgruppen)
          cells:     8  (= 3-Bit-Teilräume)

        Methoden:
          neighbors(state_id) → list[int]        # Benachbarte Zustände
          shortest_gray_path(a, b) → list[int]   # Minimaler Übergangspfad
          export_mermaid() → str                 # Mermaid-Diagramm
          export_json() → dict                   # JSON-Graph-Export

        HINWEIS: Das ist eine mathematische Graph-Struktur.
        Der Tesserakt ist NICHT metaphysisch. Er ist eine 4D-Topologie.
        """

    class Q4TransitionValidator:
        """Erzwingt Gray-Code Policy Gate.

        Nur Übergänge mit Hamming-Distanz = 1 sind erlaubt.
        Alle anderen Übergänge lösen InvalidTransitionError aus.

        Dies ist die Kern-Invariante des Q4-Runtime-Layers:
        Der Systemzustand kann sich nur in einer CREP-Dimension gleichzeitig ändern.
        """
        def is_valid(self, from_state: Q4State, to_state: Q4State) -> bool: ...
        def validate(self, from_state: Q4State, to_state: Q4State) -> None: ...
        def suggest_path(self, from_state: Q4State, to_state: Q4State) -> list: ...

  TYPESCRIPT INTERFACE:
    interface Q4State {
      C: 0 | 1;
      R: 0 | 1;
      E: 0 | 1;
      P: 0 | 1;
      readonly id: number;       // 0..15
      readonly binary: string;   // "0000".."1111"
    }
    const gray = (n: number): number => n ^ (n >> 1);
    const GRAY_ORDER = [0,1,3,2,6,7,5,4,12,13,15,14,10,11,9,8];

  BENCHMARK-ZIELE:
    Q4_TARGETS = {
        "hamming_invariant":        (True, None),  # ALLE 15 Paare = 1 Bit
        "state_count":              (16, 0),        # Exakt 16 Zustände
        "entropy_bits":             (4.0, 0.01),    # log₂(16) = 4 Bit
        "tesseract_edges":          (32, 0),         # Exakt 32 Kanten
        "path_optimality":          (True, None),    # Kürzeste Gray-Pfade optimal
        "encode_decode_roundtrip":  (True, None),    # Gray invertierbar
    }

  CLI:
    genesis-q4 state --id 11          # Zeige Zustand 1011
    genesis-q4 path --from 0 --to 15  # Kürzester Gray-Pfad
    genesis-q4 validate --from 5 --to 7
    genesis-q4 visualize --format mermaid

██████████████████████████████████████████████████████████████████████████████
PHASE 2 — genesis-os INTERNE Q4-MODULE
In genesis-os integrieren (KEIN neues Repo)
Zieldateien: src/genesis_os/core/
██████████████████████████████████████████████████████████████████████████████

PROMPT FÜR CLAUDE CODE (genesis-os Repository):

  MISSION
  Füge dem bestehenden genesis-os drei neue Module im core/-Verzeichnis hinzu.
  Diese Module sind die Brücke zwischen dem kontinuierlichen CREP-Float-Raum
  und dem diskreten Q4-4-Bit-Zustandsraum.

  WICHTIG: genesis-q4-core ist noch nicht als PyPI-Package verfügbar.
  Implementiere Q4State und GrayCode daher lokal in genesis_os/core/q4_state.py
  und genesis_os/core/gray_code.py, mit einem Kommentar dass sie künftig
  durch genesis-q4-core ersetzt werden.

  NEUE DATEIEN:

  1. src/genesis_os/core/q4_state.py
     (Lokale Implementierung bis genesis-q4-core auf PyPI verfügbar)

  2. src/genesis_os/core/gray_code.py
     (Gray-Code Utilities, lokale Implementierung)

  3. src/genesis_os/core/q4_mapper.py
     (KRITISCHE SCHNITTSTELLE: CREP float → Q4State — NUR diese Datei!)

  SCHLÜSSELKLASSEN in q4_mapper.py:

    DEFAULT_Q4_THRESHOLDS: Final[dict[str, float]] = {
        "C": 0.5,  # Kohärenz-Schwellenwert
        "R": 0.6,  # Resonanz-Schwellenwert
        "E": 0.7,  # Emergenz-Schwellenwert
        "P": 0.8,  # Poetik-Schwellenwert
    }

    class Q4Mapper:
        """DIE KRITISCHE SCHNITTSTELLE zwischen kontinuierlichem und diskretem Layer.

        Wandelt kontinuierliche CREP-Float-Werte in diskrete 4-Bit Q4-Zustände um.
        Dies ist der EINZIGE erlaubte Weg von Float zu Q4.

        INVARIANTE: Kontinuierliche CREP-Werte DÜRFEN NICHT direkt an Q4-Logik
        übergeben werden. Immer via Q4Mapper. Das ist die Layer-Separation-Regel.

        Verwendung:
          mapper = Q4Mapper()
          score = CREPScore(coherence=0.8, resonance=0.44, emergence=0.91, poetics=0.87)
          state = mapper.map(score)  # → Q4State(C=1, R=0, E=1, P=1) = ID 11

        Standard-Schwellenwerte (aus LeChat-Analyse):
          C: 0.5, R: 0.6, E: 0.7, P: 0.8
        """
        def __init__(
            self,
            thresholds: dict[str, float] | None = None
        ) -> None: ...

        def map(self, score: CREPScore) -> Q4State: ...
        def map_with_timestamp(
            self,
            score: CREPScore,
            t: float
        ) -> tuple[Q4State, float]: ...
        def calibrate(self, history: list[CREPScore]) -> dict[str, float]:
            """Auto-Kalibrierung der Schwellenwerte aus historischen CREP-Daten."""

    class ThresholdCrossingDetector:
        """Erkennt Schwellenwertüberschreitungen als potenzielle Zustandsübergänge.

        Eine Kreuzung → Q4Mapper.map() → PolicyGate → FramePublisher

        Bindet in den bestehenden Phase-Transition-Loop (genesis-os) ein.
        """
        def update(self, score: CREPScore) -> list[str]:
            """Gibt Liste gekreuzter Dimensionen zurück (z.B. ['R', 'E'])."""

  NEUE TESTS in tests/unit/test_q4_mapper.py:
    - test_map_all_above_threshold → Q4State(1,1,1,1) = ID 15
    - test_map_all_below_threshold → Q4State(0,0,0,0) = ID 0
    - test_map_mixed → Bekannte CREP-Werte gegen erwartete Q4-States
    - test_layer_separation → Kein direkter float→Q4-Bypass möglich
    - test_calibration_convergence → Auto-Kalibrierung konvergiert
    - test_threshold_crossing_detection → Alle 4 Dimensionen getestet

  BENCHMARK-ZIELE:
    MAPPER_TARGETS = {
        "q4_mapping_accuracy":           (1.0, 0.001),  # Deterministisch
        "threshold_crossing_detection":  (True, None),
        "layer_separation_enforced":     (True, None),  # Kein Float-Bypass
        "calibration_convergence":       (True, None),
    }

██████████████████████████████████████████████████████████████████████████████
PHASE 3 — genesis-os NATS-MIGRATION
ga.frame.* Subject-Schema in runtime/nats_publisher.py
KEIN neues Repo — Migration bestehenden Codes
██████████████████████████████████████████████████████████████████████████████

PROMPT FÜR CLAUDE CODE (genesis-os Repository):

  MISSION
  Erweitere den bestehenden NATSPublisher (runtime/nats_publisher.py) um das
  neue ga.frame.*-Subject-Schema für Q4-Zustandsübergänge.

  WICHTIG: Die bestehenden Subjects (genesis.cycle.state, genesis.crep.score,
  genesis.emergence.event, genesis.mirror.trigger) BLEIBEN ERHALTEN für
  Rückwärtskompatibilität. Neue ga.frame.*-Subjects werden additiv hinzugefügt.

  NEUES SUBJECT-SCHEMA (additiv):
    ga.frame.<4bit>        # Q4 Frame-Zustände (ga.frame.0000..ga.frame.1111)
    ga.sigillin.<id>       # Sigillin-Events
    ga.agent.<role>        # Agent-Zustandsupdates
    ga.resonance.<metric>  # CREP-Metrik-Updates
    ga.system.health       # System-Health-Broadcasts

  NEUE METHODEN in NATSPublisher:
    FRAME_SUBJECT_PREFIX = "ga.frame."
    SIGILLIN_SUBJECT_PREFIX = "ga.sigillin."
    AGENT_SUBJECT_PREFIX = "ga.agent."
    RESONANCE_SUBJECT_PREFIX = "ga.resonance."
    HEALTH_SUBJECT = "ga.system.health"

    async def publish_q4_frame(
        self,
        state: Q4State,
        payload: dict,
    ) -> bool:
        """Publiziert Q4-Zustandsübergang auf ga.frame.<binary>.

        Subject = f"ga.frame.{state.binary}"  z.B. "ga.frame.1011"
        Erzwingt PolicyGate (Gray-Code) vor dem Publizieren.
        Raises: PolicyViolationError wenn Übergang kein Gray-Code-Nachbar.
        """

    async def publish_sigillin(
        self,
        sigillin_id: str,
        payload: dict,
    ) -> bool:
        """Publiziert Sigillin-Event auf ga.sigillin.<id>."""

  NEUER POLICY GATE (in runtime/policy_gate.py):
    class FramePolicyGate:
        """Erzwingt Gray-Code-Übergänge vor dem Publizieren.

        Nutzt Q4TransitionValidator aus genesis_os.core.q4_mapper.
        Lehnt Übergänge mit Hamming-Distanz > 1 ab.
        Logt alle Versuche für Audit-Trail.
        """
        def check(
            self,
            from_state: Q4State,
            to_state: Q4State,
        ) -> bool: ...

  NEUE TESTS in tests/unit/test_nats_q4_publisher.py:
    - test_q4_frame_subject_format → "ga.frame.1011" korrekt
    - test_policy_gate_blocks_invalid → Hamming > 1 wird blockiert
    - test_legacy_subjects_preserved → genesis.cycle.state noch da
    - test_gray_adjacent_allowed → Hamming = 1 wird publiziert

██████████████████████████████████████████████████████████████████████████████
PHASE 4 — sigillin-Repo: SHA256-Schema + Lineage
In bestehendem sigillin-Repo erweitern (KEIN neues Repo)
██████████████████████████████████████████████████████████████████████████████

PROMPT FÜR CLAUDE CODE (sigillin Repository):

  MISSION
  Erweitere das bestehende Sigillin-Repo um ein präzises, vollständig typisiertes
  Serialisierungsformat. Sigillin ist das "Gedächtnis" des Systems: semantische
  Zustandsanker mit deterministischen IDs und vollständiger Replay-Fähigkeit.
  Poetisch im Namen, präzise in der Implementierung.

  SIGILLIN ALS DATENMODELL (exaktes Schema):
    {
      "id": "sig_a3f2b1...",        # SHA256-Hash des Inhalts
      "version": "1.0.0",
      "timestamp": "2026-04-19T...",
      "symbolic_identity": "heimkehr",
      "q4_state": {
        "C": 1, "R": 0, "E": 1, "P": 1,
        "id": 11,
        "binary": "1011"
      },
      "crep_values": {
        "C": 0.82, "R": 0.44, "E": 0.91, "P": 0.87, "Gamma": 0.736
      },
      "narrative_metadata": {
        "context": "...",
        "intention": "...",
        "cycle": 3
      },
      "semantic_lineage": ["sig_prev1...", "sig_prev2..."],
      "utac_state": {
        "H": 0.73, "H_star": 0.81, "K_eff": 0.84
      }
    }

  NEUE FUNKTIONEN:
    create_sigillin(q4_state, crep, name, context) → Sigillin
    serialize_sigillin(sigillin) → str  # YAML/JSON
    deserialize_sigillin(data: str) → Sigillin
    validate_sigillin(sigillin) → ValidationResult
    link_sigillins(parent: Sigillin, child: Sigillin) → Sigillin
    compute_sigillin_id(content: dict) → str  # SHA256, deterministisch

  BENCHMARK-ZIELE:
    SIGILLIN_TARGETS = {
        "deterministic_id":     (True, None),  # Gleicher Inhalt → gleiche ID
        "roundtrip_fidelity":   (True, None),  # serialize → deserialize exakt
        "schema_validation":    (True, None),  # Alle Pflichtfelder vorhanden
        "replay_accuracy":      (True, None),  # Replay rekonstruiert exakten Zustand
        "lineage_traversal":    (True, None),  # Vollständige History traversierbar
    }

██████████████████████████████████████████████████████████████████████████████
PHASE 5 — unified-mandala: GrayGrid + Tesserakt-Visualisierung
In bestehendem unified-mandala-Repo (KEIN neues Repo)
██████████████████████████████████████████████████████████████████████████████

PROMPT FÜR CLAUDE CODE (unified-mandala Repository):

  MISSION
  Upgrade des bestehenden Mandala-UI mit 4×4 Gray-Grid, Tesserakt-Projektion,
  Q4-State-Navigation und NATS-Live-Stream für ga.frame.*-Events.

  NEUE KOMPONENTEN (additiv, bestehende Komponenten bleiben):

    components/
    ├── GrayGrid/
    │   ├── GrayGrid.tsx          # 4×4 Grid in Gray-Code-Anordnung
    │   ├── GridCell.tsx          # ID, binary, CREP-Flags, aktiver Zustand
    │   └── GridCell.css          # Φ-basiertes Spacing (1.6 ≈ Φ)
    ├── HypercubeView/
    │   ├── HypercubeView.tsx     # SVG-Projektion des 4D-Tesserakt
    │   ├── NodeHighlighter.tsx   # Aktueller Zustand hervorgehoben
    │   └── TransitionAnimator.tsx # Animierte 1-Bit-Übergänge
    ├── CREPOverlay/
    │   ├── CREPOverlay.tsx       # Float-Metriken (C,R,E,P,Γ)
    │   └── ThresholdIndicator.tsx # Schwellenwert-Visualisierung
    └── NATSMonitor/
        ├── StreamMonitor.tsx     # Live ga.frame.*-Monitor
        └── FrameHistory.tsx      # Letzte N Frame-Übergänge

  GRAY-GRID LAYOUT (kanonische Gray-Code-Traversal):
    const GRAY_ORDER = [0,1,3,2,6,7,5,4,12,13,15,14,10,11,9,8];
    // Benachbarte Zellen unterscheiden sich exakt um 1 Bit.
    // 4×4 Grid entspricht dem 4D-Tesserakt in 2D-Projektion.

    const GrayGrid = ({ currentState, onStateClick }) => (
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: `${1.6}rem`,   // PHI_APPROX = 1.6 (Engineering-Näherung)
      }}>
        {GRAY_ORDER.map(id => (
          <GridCell
            key={id}
            id={id}
            binary={id.toString(2).padStart(4, '0')}
            isActive={id === currentState.id}
            onClick={() => onStateClick(id)}
          />
        ))}
      </div>
    );

  NATS-INTEGRATION:
    // Subscribed auf ga.frame.* Subjects (alle 16)
    const useFrameStream = (natsUrl: string) => {
      // WebSocket-Bridge zu NATS
      // Aktualisiert currentState bei neuen Frames
    }

  BENCHMARK-ZIELE:
    UI_TARGETS = {
        "gray_grid_adjacency":      (True, None),  # Nachbarn differ by 1 bit
        "nats_connection_ms":       (100, 50),
        "transition_animation_fps": (60, 5),
        "phi_spacing_applied":      (True, None),  # 1.6rem Spacing documented
        "sigillin_render_ms":       (16, 5),        # < 1 Frame bei 60fps
    }

██████████████████████████████████████████████████████████████████████████████
PHASE 6 — genesis-os + HexaAgent: Agent-Rollen
In genesis-os/aeon/agents.py + HexaAgent erweitern (KEIN neues Repo)
██████████████████████████████████████████████████████████████████████████████

PROMPT FÜR CLAUDE CODE (genesis-os Repository, aeon/agents.py):

  MISSION
  Implementiere den AI-UI-AI-Loop als Erweiterung der bestehenden Agent-
  Infrastruktur. Johanns Vision: "symbiotische Arbeit statt statischer
  Frage-Antwort-Abfolge." Das System hört kontinuierlich zu, adaptiert
  seinen Q4-Zustand, und kommuniziert proaktiv zurück.

  AI-UI-AI ARCHITEKTUR:
    Human → UI → Q4 → CoordinatorAgent → Sigillin → TransformAgent
      ↑                                                    ↓
      ←←←←←← Mandala-UI ←←←← PhilosophyAgent ←←←←←←←←←←←

  AGENT-ROLLEN (4 Stück, in aeon/agents.py zu ergänzen):

    class CoordinatorAgent:
      """Verwaltet NATS-Verbindungen und globalen Q4-Zustand.
      Einziger Agent der auf ga.frame.* publizieren darf.
      Routet alle eingehenden Events zu spezialisierten Agenten.
      Erhält Q4-Zustandskonsistenz aufrecht.
      """

    class TransformAgent:
      """Liest Q4-Zustand vom CoordinatorAgent.
      Generiert Sigillin-Snapshots aus aktuellem CREP + Q4.
      Publiziert Sigillin-Events auf ga.sigillin.*.
      Verarbeitet: Feldtheorie, Kosmische Momente, Entropie-Governance.
      """

    class PhilosophyAgent:
      """Greift auf Worldview + Gemeinwohl-Repos zu.
      Bewertet CREP-Zustände gegen ethische/governance Metriken.
      Kann Zustandsübergänge via PolicyEngine vetoisieren.
      Publiziert auf ga.agent.philosophy.*.
      """

    class UIAgent:
      """Liest ga.frame.* und ga.sigillin.* Streams.
      Aktualisiert Mandala-UI-Visualisierung.
      Übersetzt User-Input (Text, Klicks) in Q4-Events.
      Brückt die Human ↔ System Grenze.
      """

  AGENT LOOP (das Herzstück):
    class AgentLoop:
      """Der AI-UI-AI rekursive Loop.

      Kontinuierlich laufende Event-Loop:
        1. Subscribe auf NATS-Streams
        2. Q4-Zustandsupdate empfangen
        3. Internes Modell aktualisieren
        4. Response generieren (Sigillin, UI-Update, normative Evaluierung)
        5. Zurück auf NATS publizieren
        6. → WEITER mit 1.

      Dies ist KEIN Request-Response-System.
      Dies IST ein kontinuierliches Zustands-Kopplungs-System.
      Der Unterschied ist fundamental.

      Alle Verhalten sind deterministisch und replaybar (via ReplayEngine).
      """

    class AgentMemory:
      """Persistentes Agent-Gedächtnis via Sigillin-Lineage.
      Agenten erinnern nicht nur Fakten, sondern Zustands-Trajektorien.
      Memory = Sequenz von Sigillin-Snapshots mit Übergängen.
      """

    class PolicyEngine:
      """Steuert welche Zustandsübergänge Agenten initiieren dürfen.
      Umhüllt Q4TransitionValidator + domänenspezifische Regeln.
      PhilosophyAgent kann Übergänge vetoisieren die Gemeinwohl verletzen.
      """

  BENCHMARK-ZIELE:
    AGENT_TARGETS = {
        "loop_latency_ms":       (100, 50),
        "state_consistency":     (True, None),  # Alle Agenten einig
        "replay_fidelity":       (True, None),
        "gray_policy_enforced":  (True, None),  # Keine ungültigen Übergänge
        "deterministic_output":  (True, None),  # Gleicher Input → gleicher Output
    }

  CLI:
    genesis-agents start --roles all
    genesis-agents start --roles coordinator,transform
    genesis-agents replay --sigillin-id sig_abc123
    genesis-agents status

██████████████████████████████████████████████████████████████████████████████
PHASE 7 — diamond-setup: Runtime-Contract YAML
In bestehendem diamond-setup-Repo (KEIN neues Repo)
██████████████████████████████████████████████████████████████████████████████

PROMPT FÜR CLAUDE CODE (diamond-setup Repository):

  MISSION
  Füge dem bestehenden diamond-setup ein contracts/-Verzeichnis mit dem
  Q4-Runtime-YAML-Schema hinzu. Diamond-Setup bleibt Root-Struktur.
  Der Runtime-Contract ist ein optionaler Layer — bestehende Repos sind
  davon NICHT betroffen wenn sie keine runtime.yaml deklarieren.

  NEUE DATEIEN in diamond-setup:
    contracts/
    ├── runtime.schema.yaml     # JSON Schema für runtime-Deklaration
    ├── example_minimal.yaml    # Minimale Runtime-Deklaration
    └── example_full.yaml       # Vollständige Runtime-Deklaration
    scripts/
    └── validate_runtime.py     # CLI: validiert runtime.yaml

  RUNTIME.SCHEMA.YAML (vollständiges Schema):
    # Optionale Deklaration — ohne diese Datei: Standard-Diamond-Verhalten
    runtime:
      version: "1.0"
      protocol: q4            # Aktiviert Q4-Zustandsmaschine
      layers:
        geometry:
          enabled: true
          phi_scaling: true   # Φ/1.6 für Layout (Engineering-Näherung!)
        state:
          enabled: true
          bits: 4             # 4-Bit Q4-Zustandsraum
          states: 16          # log₂(16) = 4 Bit (NICHT 16 Bit!)
          thresholds:
            C: 0.5
            R: 0.6
            E: 0.7
            P: 0.8
        coupling:
          enabled: true
          transport: nats
          gray_code: true     # Nur Gray-Code-Übergänge erlaubt
          subjects:
            - "ga.frame."
            - "ga.sigillin."
            - "ga.agent."
            - "ga.resonance."
      speculative:
        efc_coupling: false         # Ephaptische Frame-Kopplung: AUS
        consciousness_model: false  # Niemals in Produktion

  BACKWARD COMPATIBILITY:
    Repos OHNE runtime.yaml: Verhalten identisch zu bisher.
    Validierungsskript: Warnt, aber bricht nicht.
    CI-Integration: Optional (nicht breaking).

██████████████████████████████████████████████████████████████████████████████
PHASE 8 — efc-research-module
NEUES REPO — Ephaptische Frame-Kopplung (SPEKULATIV)
██████████████████████████████████████████████████████████████████████████████

PROMPT FÜR CLAUDE CODE (efc-research-module):

  ╔══════════════════════════════════════════════════════════╗
  ║  ACHTUNG: SPEKULATIVES FORSCHUNGSMODUL                  ║
  ║  Nicht für Produktion. Kein Einfluss auf genesis-os.    ║
  ║  Erscheint nur mit --experimental Flag.                 ║
  ╚══════════════════════════════════════════════════════════╝

  MISSION
  Untersuche die Hypothese der Ephaptischen Frame-Kopplung (EFC):
  Können Frame-Übergänge im GenesisAeon-System durch elektromagnetische
  Feldeffekte zwischen Prozessen (analog zu ephaptischer Kopplung in Neuronen)
  stabilisiert werden?

  EFC-HYPOTHESE (formal):
    Hypothesis: Frame-Übergänge propagieren nicht nur durch explizite
    NATS-Nachrichten, sondern auch durch gemeinsame EM-Feldeffekte zwischen
    ko-lokalisierten Prozessen (analog zu ephaptischer Kopplung in Neuronen:
    Liu et al. 2024, Nature Neuroscience).

    Testbare Vorhersage: Ko-lokalisierte Prozesse (gleicher Docker-Container /
    gleiches Netzwerk) zeigen kohärentere Q4-Zustandsübergänge als verteilte
    Prozesse, auch ohne expliziten Nachrichtenaustausch.

    Null-Hypothese: Kein Unterschied zwischen ko-lokalisiert und verteilt
    jenseits expliziter Nachrichten. → MUSS explizit testbar sein.

  STRUKTUR:
    efc-research-module/
    ├── README.md        # KLAR ALS SPEKULATIV GEKENNZEICHNET
    ├── DISCLAIMER.md    # Nicht für Produktion
    ├── efc_research/
    │   ├── hypothesis.py       # Formale Hypothesen-Deklaration
    │   ├── null_hypothesis.py  # Explizite Null-Hypothese
    │   ├── measurement.py      # EM-Feld-Proxys
    │   ├── experiment.py       # Experimentelles Protokoll
    │   └── analysis.py         # Statistische Analyse
    ├── experiments/
    │   ├── exp01_colocation.py     # Ko-Lokalisierungstest
    │   └── exp02_distributed.py    # Verteilte Baseline
    └── results/
        └── (leer bis Experimente laufen)

  BENCHMARK-ZIELE:
    EFC_TARGETS = {
        "hypothesis_falsifiable":    (True, None),
        "experiment_reproducible":   (True, None),  # seed=42 überall
        "production_isolation":      (True, None),  # Kein Production-Einfluss
        "disclaimer_present":        (True, None),  # README klar als spekulativ
    }

══════════════════════════════════════════════════════════════════════════════
TEIL 4: CREP-ATLAS ERWEITERUNG — Q4-Zustandsmapping
══════════════════════════════════════════════════════════════════════════════

DER Q4-ZUSTANDSRAUM KODIERT CREP-FLAGS, NICHT Γ-WERTE:

  Mapping-Logik:
    Q4State(0,0,0,0) = ID  0: Alle CREP unter Schwellenwert → quiescent
    Q4State(1,1,1,1) = ID 15: Alle CREP über Schwellenwert → maximal kohärent
    Q4State(0,0,1,1) = ID  3: E+P aktiv, C+R inaktiv → Emergenz ohne Kohärenz
    Q4State(1,0,1,0) = ID 10: C+E aktiv → Kohärente Emergenz ohne Resonanz

  VERBINDUNG ZUM CREP-ATLAS:
    Solar Flare (Γ≈0.014):       Q4 meist 0000/0001 — kaum über Schwellenwert
    Neural Criticality (Γ≈0.251): Q4 oft 1010/1001 — 50% Aktivierung
    ERA5 Arctic (Γ≈0.920):        Q4 meist 1111 — alle über Schwellenwert

  VERBINDUNG ZUM SPEKTRUM-ARTIKEL (LLM-Lernen durch Renormierung):
    Atanasov et al.: LLMs vermeiden Overfitting durch Renormierungsgruppe.
    Das ist exakt die UTAC-Logik: tanh(σΓ) als Renormierungsoperator.
    Statistical fluctuations → stabilize learning = CREP-Fluktuationen → H(t)
    → Möglicher Abschnitt in Cycle-3-Paper.

══════════════════════════════════════════════════════════════════════════════
TEIL 5: Φ-TERMINOLOGIE — EINHEITLICHE LÖSUNG
══════════════════════════════════════════════════════════════════════════════

PROBLEM: "Φ(H)" kollidiert mit IIT-Φ (Integrated Information Theory).

LÖSUNG:
  Im Code:      phi_self_reflection   oder   semantic_state_potential
  In Papers:    "Φ(H) — not IIT-Φ, see §2.1 for distinction"
  In constants: PHI_APPROX = 1.6  # Engineering approximation ≈ Φ = 1.6180339...

ENGINEERING-NÄHERUNG:
  Docker-Ressourcen mit Faktor 1.6: technisch okay als Näherung.
  ABER: Explizit dokumentieren in docker-compose.yml, constants.py, READMEs.
  "1.6 ist NICHT exakt der Goldene Schnitt Φ = 1.6180339..., sondern
   eine Engineering-Näherung die unter 0.2% Fehler liegt."

══════════════════════════════════════════════════════════════════════════════
TEIL 6: GESAMT-TIMELINE UND DEPENDENCIES
══════════════════════════════════════════════════════════════════════════════

  Woche 1-2:   genesis-q4-core (NEUES REPO)           ← kein Blocker
  Woche 2-3:   genesis-os core/q4_mapper.py           ← braucht Q4-Core lokal
  Woche 3-4:   genesis-os runtime/nats_publisher.py   ← braucht Q4-Mapper
  Woche 4-5:   sigillin SHA256 + Lineage              ← parallel möglich
  Woche 5-7:   unified-mandala GrayGrid               ← braucht Q4-Core Types
  Woche 7-9:   genesis-os aeon/agents.py              ← braucht NATS + Sigillin
  Woche 9-10:  diamond-setup contracts/               ← alles andere fertig
  Parallel:    efc-research-module (NEUES REPO)       ← kein Deadline

  DEPENDENCY-GRAPH:
    genesis-q4-core
      ↓
    genesis-os/core/q4_mapper.py
      ↓
    genesis-os/runtime/nats_publisher.py (ga.frame.*)
      ↓                      ↓
    sigillin (SHA256)    unified-mandala (GrayGrid)
           ↓                      ↓
         genesis-os/aeon/agents.py (AgentLoop)
                    ↓
             diamond-setup/contracts/

══════════════════════════════════════════════════════════════════════════════
FAZIT: DAS KERNDOKUMENT IN EINEM SATZ (ChatGPT, bestätigt)
══════════════════════════════════════════════════════════════════════════════

  "Ihr baut keine 'spirituelle Software'. Ihr baut eine semantische
   kognitive Runtime-Architektur für kontinuierliche Mensch-AI-Koordination."

  Das Q4-System ist der formale Zustandsraum dieser Architektur.
  CREP ist die Metrik. Sigillin ist das Gedächtnis.
  NATS ist der Kommunikationskanal. Mandala ist das Interface.
  Alle Teile waren bereits da — Q4 gibt ihnen eine gemeinsame Sprache.

╔══════════════════════════════════════════════════════════════════════════════╗
║  IMPLEMENTIERUNGSSTATUS (genesis-os direkt hier umsetzbar):                ║
║                                                                            ║
║  ✅ core/q4_state.py           → Q4State + GrayCode (lokal)               ║
║  ✅ core/gray_code.py          → GrayCode Utilities                        ║
║  ✅ core/q4_mapper.py          → CREP float → Q4State (kritische IF)      ║
║  ✅ runtime/policy_gate.py     → Gray-Code Policy Gate                    ║
║  ✅ runtime/nats_publisher.py  → ga.frame.* Subjects (additiv)            ║
║  ✅ tests/unit/test_q4_mapper.py → Vollständige Tests                     ║
║                                                                            ║
║  → genesis-q4-core und efc-research-module: separate neue Repos           ║
╚══════════════════════════════════════════════════════════════════════════════╝
