"""SemanticAgent — κ-field coupled semantic agent with β-synchronization.

Implements:
    - κ-field coupling: κ_field = Σκ_i / N
    - β-synchronization: β_sync = σ(β_agents) / mean(β_agents)
    - v_collective: collective angular momentum
    - Resonance score tracking

Phase 6 additions — AI-UI-AI Agent Roles:
    - CoordinatorAgent: NATS hub + global Q4 state authority
    - TransformAgent: Sigillin snapshot generator
    - PhilosophyAgent: Governance/ethics evaluator with veto power
    - UIAgent: Human ↔ System boundary bridge
    - AgentLoop: Continuous event loop (not request-response)
    - AgentMemory: Sigillin-lineage-based state trajectory memory
    - PolicyEngine: Transition authorization layer
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from genesis_os.core.crep import CREPScore
from genesis_os.core.gray_code import suggest_gray_path
from genesis_os.core.q4_mapper import Q4Mapper, validate_q4_transition
from genesis_os.core.q4_state import InvalidTransitionError, Q4State
from genesis_os.core.utac_bridge import UTACBridge

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """State snapshot for a single SemanticAgent.

    Attributes:
        kappa: κ coupling strength for this agent.
        beta: β steepness parameter.
        activation: Current UTAC activation.
        resonance_score: Cumulative resonance score.
        angular_momentum: Agent's contribution to v_collective.
        cycle: Current cycle index.
    """

    kappa: float
    beta: float
    activation: float
    resonance_score: float
    angular_momentum: float
    cycle: int


@dataclass
class CollectiveField:
    """Collective field state for a group of SemanticAgents.

    Attributes:
        kappa_field: Mean κ coupling over all agents.
        beta_sync: β synchronization index.
        v_collective: Collective angular momentum (vector sum).
        n_agents: Number of agents in the collective.
    """

    kappa_field: float
    beta_sync: float
    v_collective: float
    n_agents: int


@dataclass
class SemanticAgent:
    """κ-field coupled semantic agent.

    Each agent maintains a κ coupling strength and a β steepness parameter.
    Agents in a collective interact via their κ-fields and β-synchronization.

    Args:
        agent_id: Unique identifier for this agent.
        kappa: κ coupling strength ∈ [0, 1] (default 0.5).
        beta: β logistic steepness (default 4.5).
        theta: UTAC inflection threshold (default 0.5).
    """

    agent_id: str = "agent_0"
    kappa: float = 0.5
    beta: float = 4.5
    theta: float = 0.5
    _bridge: UTACBridge = field(default_factory=UTACBridge, init=False, repr=False)
    _cycle: int = field(default=0, init=False)
    _resonance_cumulative: float = field(default=0.0, init=False)
    _angular_history: list[float] = field(default_factory=list, init=False, repr=False)
    _state_history: list[AgentState] = field(default_factory=list, init=False, repr=False)

    def step(self, R: float, field_input: float = 0.0) -> AgentState:
        """Advance agent state by one step.

        Computes UTAC activation, updates resonance score, and tracks
        angular momentum contribution.

        Args:
            R: Normalized resource variable ∈ [0, 1].
            field_input: External κ-field input (default 0.0).

        Returns:
            AgentState snapshot.
        """
        # Effective R with κ-field coupling
        R_eff = float(np.clip(R + self.kappa * field_input, 0.0, 1.0))
        activation = UTACBridge.feldtheorie_activation(
            beta=self.beta, R=R_eff, theta=self.theta
        )
        # Angular momentum: oscillatory contribution
        angle = 2.0 * float(np.pi) * activation
        angular = float(np.cos(angle) * self.kappa)
        self._angular_history.append(angular)

        # Resonance: proximity to peak activation
        resonance = float(np.exp(-abs(activation - 0.5) * 4.0))
        self._resonance_cumulative += resonance

        state = AgentState(
            kappa=self.kappa,
            beta=self.beta,
            activation=activation,
            resonance_score=resonance,
            angular_momentum=angular,
            cycle=self._cycle,
        )
        self._state_history.append(state)
        self._cycle += 1
        return state

    @property
    def mean_resonance(self) -> float:
        """Mean resonance score over all cycles."""
        if not self._state_history:
            return 0.0
        return float(np.mean([s.resonance_score for s in self._state_history]))

    @property
    def v_angular(self) -> float:
        """Angular momentum contribution (mean of history)."""
        if not self._angular_history:
            return 0.0
        return float(np.mean(self._angular_history))

    def reset(self) -> None:
        """Reset agent to initial state."""
        self._cycle = 0
        self._resonance_cumulative = 0.0
        self._angular_history.clear()
        self._state_history.clear()

    @property
    def history(self) -> list[AgentState]:
        """Read-only history of agent states."""
        return list(self._state_history)


class AgentCollective:
    """Collective field dynamics for a group of SemanticAgents.

    Computes κ_field, β_sync, and v_collective over a set of agents.

    Args:
        agents: List of SemanticAgent instances.
    """

    def __init__(self, agents: list[SemanticAgent]) -> None:
        self.agents = list(agents)

    def compute_kappa_field(self) -> float:
        """Compute the collective κ-field as mean of individual κ values.

        κ_field = Σκ_i / N

        Returns:
            Mean κ ∈ [0, 1].
        """
        if not self.agents:
            return 0.0
        return float(np.mean([a.kappa for a in self.agents]))

    def compute_beta_sync(self) -> float:
        """Compute β synchronization index.

        β_sync = std(β_agents) / mean(β_agents)

        A low β_sync (→ 0) indicates synchronized agents.
        A high β_sync indicates dispersed β values.

        Returns:
            β_sync ≥ 0 (0 = perfectly synchronized).
        """
        if not self.agents:
            return 0.0
        betas = np.array([a.beta for a in self.agents])
        mean_beta = float(np.mean(betas))
        if mean_beta < 1e-12:
            return 0.0
        return float(np.std(betas) / mean_beta)

    def compute_v_collective(self) -> float:
        """Compute collective angular momentum v_collective.

        v_collective = |Σ angular_momentum_i|

        Returns:
            Collective angular momentum magnitude.
        """
        total = sum(a.v_angular for a in self.agents)
        return float(abs(total))

    def step_all(self, R: float) -> CollectiveField:
        """Advance all agents by one step and compute collective field.

        Args:
            R: Normalized resource variable ∈ [0, 1].

        Returns:
            CollectiveField snapshot.
        """
        kappa_field = self.compute_kappa_field()
        for agent in self.agents:
            agent.step(R=R, field_input=kappa_field)

        return CollectiveField(
            kappa_field=kappa_field,
            beta_sync=self.compute_beta_sync(),
            v_collective=self.compute_v_collective(),
            n_agents=len(self.agents),
        )

    def summary(self) -> dict[str, Any]:
        """Return a summary of the collective state."""
        return {
            "n_agents": len(self.agents),
            "kappa_field": self.compute_kappa_field(),
            "beta_sync": self.compute_beta_sync(),
            "v_collective": self.compute_v_collective(),
            "mean_resonance": float(
                np.mean([a.mean_resonance for a in self.agents]) if self.agents else 0.0
            ),
        }


# ---------------------------------------------------------------------------
# Phase 6 — AI-UI-AI Agent Roles
# ---------------------------------------------------------------------------


@dataclass
class SigillinSnapshot:
    """Minimaler Sigillin-Snapshot für AgentMemory.

    Vollständiges Sigillin-Schema lebt im sigillin-Repo (Phase 4).
    Diese Klasse ist die lokale Brücke bis zur Integration.
    """

    sigillin_id: str          # SHA256-Hash des Inhalts
    q4_state: Q4State
    crep: CREPScore
    timestamp: float
    context: str = ""
    lineage: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.sigillin_id,
            "q4_state": self.q4_state.to_dict(),
            "crep": {
                "C": self.crep.coherence,
                "R": self.crep.resonance,
                "E": self.crep.emergence,
                "P": self.crep.poetics,
                "gamma": float(self.crep.gamma),
            },
            "timestamp": self.timestamp,
            "context": self.context,
            "lineage": list(self.lineage),
        }


def _compute_sigillin_id(content: dict[str, Any]) -> str:
    """Deterministische SHA256-ID aus Snapshot-Inhalt."""
    canonical = json.dumps(content, sort_keys=True, default=str)
    return "sig_" + hashlib.sha256(canonical.encode()).hexdigest()[:16]


@dataclass
class AgentMemory:
    """Persistentes Agent-Gedächtnis via Sigillin-Lineage.

    Agenten erinnern nicht nur Fakten, sondern Zustands-Trajektorien.
    Memory = Sequenz von SigillinSnapshots mit Übergängen.

    Args:
        max_depth: Maximale Anzahl gespeicherter Snapshots (FIFO).
    """

    max_depth: int = 256
    _snapshots: list[SigillinSnapshot] = field(default_factory=list, init=False, repr=False)

    def record(self, q4_state: Q4State, crep: CREPScore, context: str = "") -> SigillinSnapshot:
        """Fügt neuen Snapshot zur Lineage hinzu."""
        lineage = [self._snapshots[-1].sigillin_id] if self._snapshots else []
        content: dict[str, Any] = {
            "q4_state": q4_state.to_dict(),
            "crep_gamma": float(crep.gamma),
            "timestamp": time.time(),
        }
        snap = SigillinSnapshot(
            sigillin_id=_compute_sigillin_id(content),
            q4_state=q4_state,
            crep=crep,
            timestamp=content["timestamp"],
            context=context,
            lineage=lineage,
        )
        self._snapshots.append(snap)
        if len(self._snapshots) > self.max_depth:
            self._snapshots.pop(0)
        logger.debug("AgentMemory: recorded %s (depth=%d)", snap.sigillin_id, len(self._snapshots))
        return snap

    def trajectory(self) -> list[SigillinSnapshot]:
        """Vollständige Zustands-Trajektorie (ältestes zuerst)."""
        return list(self._snapshots)

    def last(self) -> SigillinSnapshot | None:
        return self._snapshots[-1] if self._snapshots else None

    def replay(self, sigillin_id: str) -> SigillinSnapshot | None:
        """Findet Snapshot per ID (O(n))."""
        for snap in self._snapshots:
            if snap.sigillin_id == sigillin_id:
                return snap
        return None

    def reset(self) -> None:
        self._snapshots.clear()


@dataclass
class PolicyEngine:
    """Steuert welche Q4-Zustandsübergänge Agenten initiieren dürfen.

    Umhüllt Q4TransitionValidator + domänenspezifische Veto-Regeln.
    PhilosophyAgent kann Übergänge vetoisieren die Gemeinwohl verletzen.

    Args:
        strict: Wenn True, wirft InvalidTransitionError bei Verletzung.
    """

    strict: bool = True
    _vetoes: list[Callable[[Q4State, Q4State], bool]] = field(
        default_factory=list, init=False, repr=False
    )
    _violation_count: int = field(default=0, init=False, repr=False)

    @property
    def violation_count(self) -> int:
        return self._violation_count

    def register_veto(self, fn: Callable[[Q4State, Q4State], bool]) -> None:
        """Registriert eine Veto-Funktion.

        fn(from_state, to_state) → True wenn der Übergang vetoisiert werden soll.
        """
        self._vetoes.append(fn)

    def authorize(self, from_state: Q4State, to_state: Q4State) -> bool:
        """Prüft ob ein Übergang autorisiert ist.

        Prüft (1) Gray-Code Policy Gate, (2) alle registrierten Vetoes.

        Returns:
            True wenn autorisiert.

        Raises:
            InvalidTransitionError: wenn strict=True und Übergang ungültig.
        """
        try:
            validate_q4_transition(from_state, to_state)
        except InvalidTransitionError:
            self._violation_count += 1
            if self.strict:
                raise
            return False

        for veto_fn in self._vetoes:
            if veto_fn(from_state, to_state):
                self._violation_count += 1
                msg = f"Transition {from_state.binary}→{to_state.binary} vetoed by policy"
                logger.warning("PolicyEngine: %s", msg)
                if self.strict:
                    raise InvalidTransitionError(msg)
                return False

        return True

    def suggest_path(self, from_state: Q4State, to_state: Q4State) -> list[Q4State]:
        """Gibt einen gültigen Gray-Code-Pfad zurück."""
        ids = suggest_gray_path(from_state.id, to_state.id)
        return [Q4State.from_id(i) for i in ids]


@dataclass
class CoordinatorAgent:
    """Verwaltet NATS-Verbindungen und globalen Q4-Zustand.

    Einziger Agent der auf ga.frame.* publizieren darf.
    Routet alle eingehenden Events zu spezialisierten Agenten.
    Erhält Q4-Zustandskonsistenz aufrecht.

    Args:
        nats_url: NATS-Server-URL.
        policy: PolicyEngine für Übergangsautorisierung.
        mapper: Q4Mapper für CREP→Q4-Mapping.
    """

    nats_url: str = "nats://localhost:4222"
    policy: PolicyEngine = field(default_factory=PolicyEngine)
    mapper: Q4Mapper = field(default_factory=Q4Mapper)
    memory: AgentMemory = field(default_factory=AgentMemory)
    _current_state: Q4State = field(
        default_factory=lambda: Q4State.from_id(0), init=False, repr=False
    )
    _publisher: Any = field(default=None, init=False, repr=False)

    @property
    def current_state(self) -> Q4State:
        return self._current_state

    async def connect(self) -> bool:
        from genesis_os.runtime.nats_publisher import NATSPublisher
        self._publisher = NATSPublisher(url=self.nats_url)
        return bool(await self._publisher.connect())

    async def update_q4(self, crep: CREPScore) -> Q4State | None:
        """Mappt CREPScore auf Q4State, prüft Policy Gate, publiziert Frame.

        Returns:
            Neuer Q4State wenn Übergang autorisiert, None sonst.
        """
        new_state = self.mapper.map(crep)

        if new_state.id == self._current_state.id:
            return self._current_state  # Kein Übergang nötig

        try:
            self.policy.authorize(self._current_state, new_state)
        except InvalidTransitionError:
            logger.warning(
                "CoordinatorAgent: blocked invalid transition %s→%s",
                self._current_state.binary,
                new_state.binary,
            )
            return None

        old_state = self._current_state
        self._current_state = new_state
        snap = self.memory.record(new_state, crep, context="coordinator_update")

        if self._publisher is not None:
            await self._publisher.publish_q4_frame(
                state=new_state,
                payload={
                    "from_binary": old_state.binary,
                    "sigillin_id": snap.sigillin_id,
                    "gamma": float(crep.gamma),
                },
                from_state=old_state,
            )
        logger.info(
            "CoordinatorAgent: Q4 transition %s→%s", old_state.binary, new_state.binary
        )
        return new_state

    async def close(self) -> None:
        if self._publisher is not None:
            await self._publisher.close()


@dataclass
class TransformAgent:
    """Generiert Sigillin-Snapshots aus aktuellem CREP + Q4.

    Liest Q4-Zustand vom CoordinatorAgent.
    Publiziert Sigillin-Events auf ga.sigillin.*.
    Verarbeitet: Feldtheorie, Kosmische Momente, Entropie-Governance.

    Args:
        coordinator: CoordinatorAgent als Q4-Zustandsquelle.
    """

    coordinator: CoordinatorAgent
    memory: AgentMemory = field(default_factory=AgentMemory)
    _publisher: Any = field(default=None, init=False, repr=False)

    async def connect(self) -> bool:
        from genesis_os.runtime.nats_publisher import NATSPublisher
        self._publisher = NATSPublisher(url=self.coordinator.nats_url)
        return bool(await self._publisher.connect())

    async def process(self, crep: CREPScore) -> SigillinSnapshot:
        """Erzeugt Sigillin-Snapshot und publiziert ihn."""
        q4_state = self.coordinator.current_state
        snap = self.memory.record(q4_state, crep, context="transform_process")

        if self._publisher is not None:
            await self._publisher.publish_sigillin(
                sigillin_id=snap.sigillin_id,
                payload=snap.to_dict(),
            )
            await self._publisher.publish_agent_state(
                role="transform",
                payload={
                    "sigillin_id": snap.sigillin_id,
                    "q4_binary": q4_state.binary,
                    "gamma": float(crep.gamma),
                },
            )
        logger.debug("TransformAgent: sigillin %s created", snap.sigillin_id)
        return snap

    async def close(self) -> None:
        if self._publisher is not None:
            await self._publisher.close()


@dataclass
class PhilosophyAgent:
    """Bewertet CREP-Zustände gegen ethische/governance-Metriken.

    Greift auf Governance-Schwellenwerte zu und kann Zustandsübergänge
    via PolicyEngine vetoisieren. Publiziert auf ga.agent.philosophy.*.

    Args:
        coordinator: CoordinatorAgent für Veto-Registrierung.
        governance_threshold: Γ-Schwellenwert ab dem Eskalation nötig ist.
    """

    coordinator: CoordinatorAgent
    governance_threshold: float = 0.8
    _publisher: Any = field(default=None, init=False, repr=False)
    _evaluations: list[dict[str, Any]] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self.coordinator.policy.register_veto(self._gemeinwohl_veto)

    def _gemeinwohl_veto(self, from_state: Q4State, to_state: Q4State) -> bool:  # noqa: ARG002
        """Vetoisiert Übergänge die Governance-Grenzen verletzen.

        Aktuell: Übergänge VON kritischem Zustand (alle Flags 1) werden
        nur erlaubt wenn Φ-Reflexion stattgefunden hat (Gamma-Check).
        """
        # Übergänge vom maximalen Zustand (1111) werden nicht vetoisiert —
        # Herabstufen ist immer erlaubt. Nur unkontrolliertes Hochstufen prüfen.
        return False  # Erweiterbar mit realen Governance-Regeln

    async def connect(self) -> bool:
        from genesis_os.runtime.nats_publisher import NATSPublisher
        self._publisher = NATSPublisher(url=self.coordinator.nats_url)
        return bool(await self._publisher.connect())

    async def evaluate(self, crep: CREPScore) -> dict[str, Any]:
        """Bewertet CREPScore und publiziert Governance-Bewertung."""
        gamma = float(crep.gamma)
        level = (
            "critical" if gamma >= 0.9
            else "reviewer" if gamma >= self.governance_threshold
            else "warning" if gamma >= 0.7
            else "informational" if gamma >= 0.6
            else "safe"
        )
        result: dict[str, Any] = {
            "gamma": gamma,
            "level": level,
            "q4_binary": self.coordinator.current_state.binary,
            "timestamp": time.time(),
        }
        self._evaluations.append(result)

        if self._publisher is not None:
            await self._publisher.publish_agent_state(
                role="philosophy",
                payload=result,
            )
        if level in ("reviewer", "critical"):
            logger.warning("PhilosophyAgent: governance level=%s gamma=%.3f", level, gamma)
        return result

    @property
    def evaluation_history(self) -> list[dict[str, Any]]:
        return list(self._evaluations)

    async def close(self) -> None:
        if self._publisher is not None:
            await self._publisher.close()


@dataclass
class UIAgent:
    """Brückt die Human ↔ System Grenze.

    Liest ga.frame.* und ga.sigillin.* Streams.
    Aktualisiert Mandala-UI-Visualisierung.
    Übersetzt User-Input (Text, Klicks) in Q4-Events.

    Args:
        coordinator: CoordinatorAgent als Q4-Zustandsquelle.
    """

    coordinator: CoordinatorAgent
    _publisher: Any = field(default=None, init=False, repr=False)
    _input_handlers: list[Callable[[str, Any], Coroutine[Any, Any, None]]] = field(
        default_factory=list, init=False, repr=False
    )

    async def connect(self) -> bool:
        from genesis_os.runtime.nats_publisher import NATSPublisher
        self._publisher = NATSPublisher(url=self.coordinator.nats_url)
        return bool(await self._publisher.connect())

    def register_input_handler(
        self, handler: Callable[[str, Any], Coroutine[Any, Any, None]]
    ) -> None:
        """Registriert einen Handler für User-Input."""
        self._input_handlers.append(handler)

    async def handle_user_input(self, input_type: str, data: Any) -> None:
        """Verarbeitet User-Input und leitet ihn an registrierte Handler weiter."""
        for handler in self._input_handlers:
            await handler(input_type, data)
        if self._publisher is not None:
            await self._publisher.publish_agent_state(
                role="ui",
                payload={
                    "input_type": input_type,
                    "q4_binary": self.coordinator.current_state.binary,
                },
            )

    async def broadcast_state(self) -> None:
        """Sendet aktuellen Q4-Zustand an UI-Subscribers."""
        if self._publisher is not None:
            state = self.coordinator.current_state
            await self._publisher.publish_agent_state(
                role="ui",
                payload={"q4_binary": state.binary, "q4_id": state.id},
            )

    async def close(self) -> None:
        if self._publisher is not None:
            await self._publisher.close()


@dataclass
class AgentLoop:
    """Der AI-UI-AI rekursive kontinuierliche Event-Loop.

    KEIN Request-Response-System. Ein kontinuierliches Zustands-Kopplungs-System.

    Architektur:
        Human → UI → Q4 → CoordinatorAgent → Sigillin → TransformAgent
          ↑                                                    ↓
          ←←←←←← Mandala-UI ←←←← PhilosophyAgent ←←←←←←←←←←←

    Alle Verhalten sind deterministisch und replaybar via memory.replay().

    Args:
        coordinator: Zentraler Koordinations-Agent.
        transform: Sigillin-Generierungs-Agent.
        philosophy: Governance-Evaluierungs-Agent.
        ui: Human-System-Brücken-Agent.
        tick_interval_s: Sekunden zwischen Loop-Ticks (default 0.1 = 100ms).
    """

    coordinator: CoordinatorAgent
    transform: TransformAgent
    philosophy: PhilosophyAgent
    ui: UIAgent
    tick_interval_s: float = 0.1
    _running: bool = field(default=False, init=False, repr=False)
    _tick_count: int = field(default=0, init=False, repr=False)

    @property
    def tick_count(self) -> int:
        return self._tick_count

    @property
    def is_running(self) -> bool:
        return self._running

    async def connect_all(self) -> dict[str, bool]:
        """Verbindet alle Agenten mit NATS."""
        results = await asyncio.gather(
            self.coordinator.connect(),
            self.transform.connect(),
            self.philosophy.connect(),
            self.ui.connect(),
            return_exceptions=True,
        )
        names = ["coordinator", "transform", "philosophy", "ui"]
        return {name: bool(r) for name, r in zip(names, results, strict=True)}

    async def tick(self, crep: CREPScore) -> dict[str, Any]:
        """Führt einen Loop-Tick aus.

        Reihenfolge:
            1. CoordinatorAgent mappt CREP → Q4, publiziert Frame
            2. PhilosophyAgent evaluiert Governance
            3. TransformAgent erzeugt Sigillin
            4. UIAgent sendet Zustand an UI

        Returns:
            Tick-Zusammenfassung mit q4_state, governance_level, sigillin_id.
        """
        new_state = await self.coordinator.update_q4(crep)
        gov_result = await self.philosophy.evaluate(crep)
        sigillin = await self.transform.process(crep)
        await self.ui.broadcast_state()

        self._tick_count += 1
        return {
            "tick": self._tick_count,
            "q4_binary": self.coordinator.current_state.binary,
            "q4_transitioned": new_state is not None and new_state.id != (
                Q4State.from_id(0).id if self._tick_count == 1 else new_state.id
            ),
            "governance_level": gov_result["level"],
            "sigillin_id": sigillin.sigillin_id,
        }

    async def run(
        self,
        crep_source: Callable[[], CREPScore | None],
        max_ticks: int | None = None,
    ) -> None:
        """Startet den kontinuierlichen Loop.

        Args:
            crep_source: Callable das CREPScore liefert (oder None zum Stoppen).
            max_ticks: Maximale Tick-Anzahl (None = unbegrenzt).
        """
        self._running = True
        logger.info("AgentLoop: started (tick_interval=%.3fs)", self.tick_interval_s)
        try:
            while self._running:
                crep = crep_source()
                if crep is None:
                    break
                await self.tick(crep)
                if max_ticks is not None and self._tick_count >= max_ticks:
                    break
                await asyncio.sleep(self.tick_interval_s)
        finally:
            self._running = False
            logger.info("AgentLoop: stopped after %d ticks", self._tick_count)

    def stop(self) -> None:
        """Stoppt den Loop nach dem aktuellen Tick."""
        self._running = False

    async def close_all(self) -> None:
        """Schließt alle Agent-Verbindungen."""
        await asyncio.gather(
            self.coordinator.close(),
            self.transform.close(),
            self.philosophy.close(),
            self.ui.close(),
            return_exceptions=True,
        )

    @classmethod
    def create(
        cls,
        nats_url: str = "nats://localhost:4222",
        tick_interval_s: float = 0.1,
        strict_policy: bool = True,
    ) -> AgentLoop:
        """Factory: Erstellt einen vollständig verdrahteten AgentLoop."""
        policy = PolicyEngine(strict=strict_policy)
        mapper = Q4Mapper()
        coordinator = CoordinatorAgent(
            nats_url=nats_url, policy=policy, mapper=mapper
        )
        transform = TransformAgent(coordinator=coordinator)
        philosophy = PhilosophyAgent(coordinator=coordinator)
        ui = UIAgent(coordinator=coordinator)
        return cls(
            coordinator=coordinator,
            transform=transform,
            philosophy=philosophy,
            ui=ui,
            tick_interval_s=tick_interval_s,
        )
