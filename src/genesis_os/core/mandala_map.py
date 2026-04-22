"""MandalaMap — Laufzeit-Graph des GenesisAeon-Ökosystems.

Lädt unified-mandala/MandalaMap.yaml und verwaltet den Systemgraphen:
    Knoten = Module des Systems
    Kanten = Datenflüsse
    Kantengewichte = CREP-Γ der letzten Kopplung

Kann auch aus einem Python-Dict initialisiert werden (für Tests).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MandalaEdge:
    """Gerichtete Kante im MandalaMap-Graph.

    Attributes:
        source: Quell-Modul.
        target: Ziel-Modul.
        gamma: CREP-Γ der letzten Kopplung [0, 1].
        flow_type: Art des Datenflusses (``"data"``, ``"event"``, etc.).
    """

    source: str
    target: str
    gamma: float = 0.0
    flow_type: str = "data"


@dataclass
class MandalaMap:
    """Laufzeit-Graph des GenesisAeon-Ökosystems.

    Attributes:
        nodes: Liste aller Systemmodule.
        edges: Liste aller Datenfluss-Kanten.
        metadata: Beliebige Metadaten aus der YAML-Datei.
    """

    nodes: list[str] = field(default_factory=list)
    edges: list[MandalaEdge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | str) -> MandalaMap:
        """Lädt einen MandalaMap aus einer YAML-Datei.

        Args:
            path: Pfad zur MandalaMap.yaml-Datei.

        Returns:
            MandalaMap-Instanz.
        """
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        mm = cls()
        mm.nodes = list(data.get("nodes", []))
        mm.metadata = {k: v for k, v in data.items() if k not in ("nodes", "edges")}

        for edge_data in data.get("edges", []):
            if isinstance(edge_data, dict):
                mm.edges.append(
                    MandalaEdge(
                        source=str(edge_data.get("source", "")),
                        target=str(edge_data.get("target", "")),
                        gamma=float(edge_data.get("gamma", 0.0)),
                        flow_type=str(edge_data.get("flow_type", "data")),
                    )
                )
        return mm

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MandalaMap:
        """Erstellt einen MandalaMap aus einem Python-Dict (für Tests).

        Args:
            data: Dict mit ``nodes`` und ``edges`` Keys.

        Returns:
            MandalaMap-Instanz.
        """
        mm = cls()
        mm.nodes = list(data.get("nodes", []))
        for edge_data in data.get("edges", []):
            if isinstance(edge_data, dict):
                mm.edges.append(
                    MandalaEdge(
                        source=str(edge_data.get("source", "")),
                        target=str(edge_data.get("target", "")),
                        gamma=float(edge_data.get("gamma", 0.0)),
                        flow_type=str(edge_data.get("flow_type", "data")),
                    )
                )
        return mm

    def update_edge_weight(self, source: str, target: str, gamma: float) -> None:
        """Aktualisiert das CREP-Γ einer Kante oder erstellt sie neu.

        Args:
            source: Quell-Modul.
            target: Ziel-Modul.
            gamma: Neues CREP-Γ.
        """
        for edge in self.edges:
            if edge.source == source and edge.target == target:
                edge.gamma = float(gamma)
                return
        self.edges.append(MandalaEdge(source=source, target=target, gamma=float(gamma)))

    def mean_gamma(self) -> float:
        """Mittleres CREP-Γ über alle Kanten."""
        if not self.edges:
            return 0.0
        return sum(e.gamma for e in self.edges) / len(self.edges)

    def get_edge(self, source: str, target: str) -> MandalaEdge | None:
        """Gibt eine Kante zurück oder None wenn nicht vorhanden."""
        for edge in self.edges:
            if edge.source == source and edge.target == target:
                return edge
        return None

    def to_adjacency_dict(self) -> dict[str, list[str]]:
        """Gibt einen Adjazenz-Dict zurück (Quell → [Ziele])."""
        adj: dict[str, list[str]] = {}
        for edge in self.edges:
            adj.setdefault(edge.source, []).append(edge.target)
        return adj
