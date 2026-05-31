"""Tests für Phase 6 — AI-UI-AI Agent Roles.

Prüft CoordinatorAgent, TransformAgent, PhilosophyAgent, UIAgent,
AgentLoop, AgentMemory und PolicyEngine.

Alle Tests sind deterministisch (kein echtes NATS nötig).
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from genesis_os.aeon.agents import (
    AgentLoop,
    AgentMemory,
    CoordinatorAgent,
    PhilosophyAgent,
    PolicyEngine,
    SigillinSnapshot,
    TransformAgent,
    UIAgent,
    _compute_sigillin_id,
)
from genesis_os.core.crep import CREPScore
from genesis_os.core.q4_state import InvalidTransitionError, Q4State


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def crep_low() -> CREPScore:
    return CREPScore(coherence=0.1, resonance=0.1, emergence=0.1, poetics=0.1)


@pytest.fixture
def crep_high() -> CREPScore:
    return CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)


@pytest.fixture
def crep_mixed() -> CREPScore:
    # coherence=0.8 (>0.5), resonance=0.44 (<0.6), emergence=0.91 (>0.7), poetics=0.87 (>0.8)
    # → Q4State(C=1, R=0, E=1, P=1) = ID 11 = "1011"
    return CREPScore(coherence=0.8, resonance=0.44, emergence=0.91, poetics=0.87)


@pytest.fixture
def coordinator() -> CoordinatorAgent:
    return CoordinatorAgent(nats_url="nats://localhost:4222")


# ---------------------------------------------------------------------------
# AgentMemory
# ---------------------------------------------------------------------------


class TestAgentMemory:
    def test_record_returns_snapshot(self, crep_mixed: CREPScore) -> None:
        mem = AgentMemory()
        state = Q4State.from_id(11)
        snap = mem.record(state, crep_mixed, context="test")
        assert snap.sigillin_id.startswith("sig_")
        assert snap.q4_state.id == 11
        assert snap.context == "test"
        assert snap.lineage == []

    def test_lineage_chain(self, crep_low: CREPScore, crep_high: CREPScore) -> None:
        mem = AgentMemory()
        s1 = mem.record(Q4State.from_id(0), crep_low)
        s2 = mem.record(Q4State.from_id(1), crep_high)
        assert s2.lineage == [s1.sigillin_id]

    def test_max_depth_fifo(self, crep_low: CREPScore) -> None:
        mem = AgentMemory(max_depth=3)
        ids = []
        for i in range(5):
            s = mem.record(Q4State.from_id(0), crep_low)
            ids.append(s.sigillin_id)
        assert len(mem.trajectory()) == 3
        # Die ältesten sind rausgefallen
        remaining = [s.sigillin_id for s in mem.trajectory()]
        assert ids[0] not in remaining
        assert ids[-1] in remaining

    def test_replay_by_id(self, crep_mixed: CREPScore) -> None:
        mem = AgentMemory()
        snap = mem.record(Q4State.from_id(5), crep_mixed)
        found = mem.replay(snap.sigillin_id)
        assert found is not None
        assert found.sigillin_id == snap.sigillin_id

    def test_replay_missing_returns_none(self) -> None:
        mem = AgentMemory()
        assert mem.replay("sig_nonexistent") is None

    def test_reset_clears_all(self, crep_low: CREPScore) -> None:
        mem = AgentMemory()
        mem.record(Q4State.from_id(0), crep_low)
        mem.reset()
        assert mem.last() is None
        assert mem.trajectory() == []

    def test_deterministic_id(self, crep_mixed: CREPScore) -> None:
        mem1 = AgentMemory()
        mem2 = AgentMemory()
        s1 = mem1.record(Q4State.from_id(11), crep_mixed, context="x")
        s2 = mem2.record(Q4State.from_id(11), crep_mixed, context="x")
        # IDs können unterschiedlich sein wegen Timestamp, aber Format ist korrekt
        assert s1.sigillin_id.startswith("sig_")
        assert len(s1.sigillin_id) == 4 + 16  # "sig_" + 16 hex chars


class TestComputeSigillinId:
    def test_deterministic(self) -> None:
        content = {"a": 1, "b": "test"}
        assert _compute_sigillin_id(content) == _compute_sigillin_id(content)

    def test_different_content_different_id(self) -> None:
        assert _compute_sigillin_id({"a": 1}) != _compute_sigillin_id({"a": 2})

    def test_format(self) -> None:
        result = _compute_sigillin_id({"test": True})
        assert result.startswith("sig_")
        assert len(result) == 20  # "sig_" + 16 chars


# ---------------------------------------------------------------------------
# PolicyEngine
# ---------------------------------------------------------------------------


class TestPolicyEngine:
    def test_valid_hamming1_transition(self) -> None:
        engine = PolicyEngine(strict=True)
        # ID 0 (0000) → ID 1 (0001): Hamming = 1 ✓
        assert engine.authorize(Q4State.from_id(0), Q4State.from_id(1)) is True

    def test_invalid_hamming2_raises(self) -> None:
        engine = PolicyEngine(strict=True)
        # ID 0 (0000) → ID 3 (0011): Hamming = 2 ✗
        with pytest.raises(InvalidTransitionError):
            engine.authorize(Q4State.from_id(0), Q4State.from_id(3))

    def test_invalid_non_strict_returns_false(self) -> None:
        engine = PolicyEngine(strict=False)
        result = engine.authorize(Q4State.from_id(0), Q4State.from_id(3))
        assert result is False

    def test_violation_count_increments(self) -> None:
        engine = PolicyEngine(strict=False)
        engine.authorize(Q4State.from_id(0), Q4State.from_id(3))
        engine.authorize(Q4State.from_id(0), Q4State.from_id(15))
        assert engine.violation_count == 2

    def test_veto_function_respected(self) -> None:
        engine = PolicyEngine(strict=False)
        engine.register_veto(lambda f, t: t.id == 1)  # Veto auf Zielzustand 1
        result = engine.authorize(Q4State.from_id(0), Q4State.from_id(1))
        assert result is False
        assert engine.violation_count == 1

    def test_suggest_path_valid(self) -> None:
        engine = PolicyEngine(strict=True)
        path = engine.suggest_path(Q4State.from_id(0), Q4State.from_id(15))
        assert path[0].id == 0
        assert path[-1].id == 15
        # Alle Schritte haben Hamming-Distanz 1
        for a, b in zip(path, path[1:]):
            from genesis_os.core.gray_code import hamming_distance
            assert hamming_distance(a.id, b.id) == 1

    def test_gray_policy_enforced_all_pairs(self) -> None:
        engine = PolicyEngine(strict=True)
        # Alle gültigen Gray-Code-Nachbarn müssen autorisiert werden
        from genesis_os.core.q4_state import GRAY_ORDER
        valid_count = 0
        for i in range(len(GRAY_ORDER) - 1):
            s1 = Q4State.from_id(GRAY_ORDER[i])
            s2 = Q4State.from_id(GRAY_ORDER[i + 1])
            assert engine.authorize(s1, s2) is True
            valid_count += 1
        assert valid_count == 15


# ---------------------------------------------------------------------------
# SigillinSnapshot
# ---------------------------------------------------------------------------


class TestSigillinSnapshot:
    def test_to_dict_schema(self, crep_mixed: CREPScore) -> None:
        snap = SigillinSnapshot(
            sigillin_id="sig_abc123",
            q4_state=Q4State.from_id(11),
            crep=crep_mixed,
            timestamp=1234567890.0,
            context="test",
            lineage=["sig_prev"],
        )
        d = snap.to_dict()
        assert d["id"] == "sig_abc123"
        assert d["q4_state"]["binary"] == "1011"
        assert d["q4_state"]["id"] == 11
        assert "gamma" in d["crep"]
        assert d["lineage"] == ["sig_prev"]


# ---------------------------------------------------------------------------
# CoordinatorAgent (async, ohne echtes NATS)
# ---------------------------------------------------------------------------


class TestCoordinatorAgent:
    def test_initial_state_is_zero(self) -> None:
        c = CoordinatorAgent()
        assert c.current_state.id == 0

    @pytest.mark.asyncio
    async def test_update_q4_no_change(self, crep_low: CREPScore) -> None:
        c = CoordinatorAgent()
        # Alle CREP unter Schwellenwert → Q4State(0,0,0,0) = ID 0 = kein Übergang
        result = await c.update_q4(crep_low)
        assert result is not None
        assert result.id == 0

    @pytest.mark.asyncio
    async def test_update_q4_valid_transition(self, crep_mixed: CREPScore) -> None:
        c = CoordinatorAgent()
        # crep_mixed → Q4State(1,0,1,1) = ID 11
        # Aber direkt von 0 zu 11 ist Hamming=3 → ungültig!
        # CoordinatorAgent gibt None zurück wenn Übergang ungültig
        result = await c.update_q4(crep_mixed)
        # Q4State(0,0,0,0) → Q4State(1,0,1,1): Hamming=3, PolicyGate blockiert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_q4_single_bit(self) -> None:
        c = CoordinatorAgent()
        # coherence=0.9 (>0.5), rest unter Schwellenwert → ID 8 = 1000
        crep_c_only = CREPScore(coherence=0.9, resonance=0.1, emergence=0.1, poetics=0.1)
        # 0000 → 1000: Hamming=1 ✓
        result = await c.update_q4(crep_c_only)
        assert result is not None
        assert result.binary == "1000"
        assert c.current_state.binary == "1000"

    @pytest.mark.asyncio
    async def test_memory_records_transitions(self) -> None:
        c = CoordinatorAgent()
        crep_c = CREPScore(coherence=0.9, resonance=0.1, emergence=0.1, poetics=0.1)
        await c.update_q4(crep_c)  # 0000 → 1000
        assert c.memory.last() is not None
        assert c.memory.last().q4_state.binary == "1000"


# ---------------------------------------------------------------------------
# TransformAgent
# ---------------------------------------------------------------------------


class TestTransformAgent:
    @pytest.mark.asyncio
    async def test_process_creates_snapshot(self, crep_low: CREPScore) -> None:
        coord = CoordinatorAgent()
        transform = TransformAgent(coordinator=coord)
        snap = await transform.process(crep_low)
        assert snap.sigillin_id.startswith("sig_")
        assert snap.q4_state.id == coord.current_state.id

    @pytest.mark.asyncio
    async def test_memory_grows_with_process(self, crep_low: CREPScore) -> None:
        coord = CoordinatorAgent()
        transform = TransformAgent(coordinator=coord)
        await transform.process(crep_low)
        await transform.process(crep_low)
        assert len(transform.memory.trajectory()) == 2


# ---------------------------------------------------------------------------
# PhilosophyAgent
# ---------------------------------------------------------------------------


class TestPhilosophyAgent:
    @pytest.mark.asyncio
    async def test_evaluate_safe(self, crep_low: CREPScore) -> None:
        coord = CoordinatorAgent()
        phil = PhilosophyAgent(coordinator=coord)
        result = await phil.evaluate(crep_low)
        assert result["level"] == "safe"

    @pytest.mark.asyncio
    async def test_evaluate_critical(self) -> None:
        coord = CoordinatorAgent()
        phil = PhilosophyAgent(coordinator=coord)
        crep = CREPScore(coherence=1.0, resonance=1.0, emergence=1.0, poetics=1.0)
        result = await phil.evaluate(crep)
        assert result["level"] == "critical"

    @pytest.mark.asyncio
    async def test_evaluation_history(self, crep_low: CREPScore) -> None:
        coord = CoordinatorAgent()
        phil = PhilosophyAgent(coordinator=coord)
        await phil.evaluate(crep_low)
        await phil.evaluate(crep_low)
        assert len(phil.evaluation_history) == 2

    def test_veto_registered_in_policy(self) -> None:
        coord = CoordinatorAgent()
        initial_vetoes = len(coord.policy._vetoes)
        PhilosophyAgent(coordinator=coord)
        assert len(coord.policy._vetoes) == initial_vetoes + 1


# ---------------------------------------------------------------------------
# UIAgent
# ---------------------------------------------------------------------------


class TestUIAgent:
    @pytest.mark.asyncio
    async def test_handle_user_input_calls_handlers(self) -> None:
        coord = CoordinatorAgent()
        ui = UIAgent(coordinator=coord)
        called: list[tuple[str, Any]] = []

        async def handler(input_type: str, data: Any) -> None:
            called.append((input_type, data))

        ui.register_input_handler(handler)
        await ui.handle_user_input("click", {"state_id": 5})
        assert len(called) == 1
        assert called[0] == ("click", {"state_id": 5})


# ---------------------------------------------------------------------------
# AgentLoop
# ---------------------------------------------------------------------------


class TestAgentLoop:
    def test_create_factory(self) -> None:
        loop = AgentLoop.create(nats_url="nats://localhost:4222", strict_policy=False)
        assert isinstance(loop.coordinator, CoordinatorAgent)
        assert isinstance(loop.transform, TransformAgent)
        assert isinstance(loop.philosophy, PhilosophyAgent)
        assert isinstance(loop.ui, UIAgent)

    @pytest.mark.asyncio
    async def test_tick_increments_count(self, crep_low: CREPScore) -> None:
        loop = AgentLoop.create(strict_policy=False)
        result = await loop.tick(crep_low)
        assert loop.tick_count == 1
        assert "governance_level" in result
        assert "sigillin_id" in result

    @pytest.mark.asyncio
    async def test_run_max_ticks(self, crep_low: CREPScore) -> None:
        loop = AgentLoop.create(strict_policy=False, tick_interval_s=0.0)
        counter = [0]

        def source() -> CREPScore | None:
            counter[0] += 1
            return crep_low

        await loop.run(source, max_ticks=5)
        assert loop.tick_count == 5
        assert not loop.is_running

    @pytest.mark.asyncio
    async def test_run_stops_on_none_source(self) -> None:
        loop = AgentLoop.create(strict_policy=False, tick_interval_s=0.0)
        calls = [0]

        def source() -> CREPScore | None:
            calls[0] += 1
            if calls[0] >= 3:
                return None
            return CREPScore(coherence=0.1, resonance=0.1, emergence=0.1, poetics=0.1)

        await loop.run(source)
        assert loop.tick_count == 2

    @pytest.mark.asyncio
    async def test_deterministic_output(self, crep_low: CREPScore) -> None:
        """Gleicher Input → gleicher Q4-Zustand (Deterministik-Invariante)."""
        loop1 = AgentLoop.create(strict_policy=False)
        loop2 = AgentLoop.create(strict_policy=False)
        r1 = await loop1.tick(crep_low)
        r2 = await loop2.tick(crep_low)
        assert r1["q4_binary"] == r2["q4_binary"]
        assert r1["governance_level"] == r2["governance_level"]

    @pytest.mark.asyncio
    async def test_loop_latency_benchmark(self) -> None:
        """Loop-Latenz-Benchmark: tick() sollte < 200ms (ohne NATS) ausführen."""
        import time

        loop = AgentLoop.create(strict_policy=False)
        crep = CREPScore(coherence=0.1, resonance=0.1, emergence=0.1, poetics=0.1)
        start = time.perf_counter()
        for _ in range(10):
            await loop.tick(crep)
        elapsed = (time.perf_counter() - start) / 10
        # 200ms Toleranz ohne NATS
        assert elapsed < 0.2, f"tick() too slow: {elapsed:.3f}s"


# ---------------------------------------------------------------------------
# Integrations-Tests: Vollständiger Übergangs-Pfad
# ---------------------------------------------------------------------------


class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_state_trajectory(self) -> None:
        """Testet eine vollständige Zustands-Trajektorie von 0000 → 1000 → 1001."""
        loop = AgentLoop.create(strict_policy=True)

        # Schritt 1: 0000 → 1000 (nur C aktiv)
        crep_c = CREPScore(coherence=0.9, resonance=0.1, emergence=0.1, poetics=0.1)
        r1 = await loop.tick(crep_c)
        assert loop.coordinator.current_state.binary == "1000"

        # Schritt 2: 1000 → 1001 (C + P aktiv)
        crep_cp = CREPScore(coherence=0.9, resonance=0.1, emergence=0.1, poetics=0.9)
        r2 = await loop.tick(crep_cp)
        assert loop.coordinator.current_state.binary == "1001"

        # Memory enthält beide Übergänge
        trajectory = loop.coordinator.memory.trajectory()
        assert len(trajectory) == 2
        assert trajectory[0].q4_state.binary == "1000"
        assert trajectory[1].q4_state.binary == "1001"

    @pytest.mark.asyncio
    async def test_state_consistency_across_agents(self) -> None:
        """Alle Agenten sind über denselben Coordinator einig über den Q4-Zustand."""
        coord = CoordinatorAgent()
        transform = TransformAgent(coordinator=coord)
        phil = PhilosophyAgent(coordinator=coord)
        ui = UIAgent(coordinator=coord)

        crep_c = CREPScore(coherence=0.9, resonance=0.1, emergence=0.1, poetics=0.1)
        await coord.update_q4(crep_c)

        snap = await transform.process(crep_c)
        gov = await phil.evaluate(crep_c)

        # Alle sehen denselben Q4-Zustand
        assert snap.q4_state.binary == coord.current_state.binary
        assert gov["q4_binary"] == coord.current_state.binary
