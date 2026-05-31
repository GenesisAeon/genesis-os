"""Tests für genesis_os.runtime.nats_publisher + monitoring — Phase F."""

from __future__ import annotations

import asyncio
import json

import pytest

from genesis_os.monitoring.prometheus_exporter import GenesisPrometheusExporter
from genesis_os.runtime.nats_publisher import NATSPublisher


class FakeState:
    """Minimaler Stub für GenesisState."""

    def __init__(self) -> None:
        self.cycle = 5
        self.entropy = 0.42
        self.phi = 1.3
        self.lagrangian = -0.17
        self.emergence_events: list[object] = []
        self.crep = FakeCREP()

    class Phase:
        value = "INTEGRATION"

    phase = Phase()


class FakeCREP:
    coherence = 0.7
    resonance = 0.6
    emergence = 0.8
    poetics = 0.5
    gamma = 0.612
    gamma_canonical = 0.643


class TestNATSPublisherNoServer:
    @pytest.mark.asyncio
    async def test_connect_no_server_returns_false(self) -> None:
        publisher = NATSPublisher(url="nats://localhost:19999")
        result = await publisher.connect()
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_no_connection_no_error(self) -> None:
        publisher = NATSPublisher(url="nats://localhost:19999")
        await publisher.publish("test.subject", {"key": "value"})

    @pytest.mark.asyncio
    async def test_publish_cycle_state_no_error(self) -> None:
        publisher = NATSPublisher(url="nats://localhost:19999")
        state = FakeState()
        await publisher.publish_cycle_state(state)

    @pytest.mark.asyncio
    async def test_close_no_connection_no_error(self) -> None:
        publisher = NATSPublisher(url="nats://localhost:19999")
        await publisher.close()

    def test_subject_constants(self) -> None:
        assert NATSPublisher.SUBJECT_CYCLE == "genesis.cycle.state"
        assert NATSPublisher.SUBJECT_CREP == "genesis.crep.score"
        assert NATSPublisher.SUBJECT_EMERGE == "genesis.emergence.event"
        assert NATSPublisher.SUBJECT_MIRROR == "genesis.mirror.trigger"


class TestCycleStateSerializer:
    def test_cycle_state_all_fields(self) -> None:
        state = FakeState()
        payload = {
            "cycle": state.cycle,
            "phase": state.phase.value,
            "entropy": state.entropy,
            "phi": state.phi,
            "lagrangian": state.lagrangian,
            "gamma": state.crep.gamma,
            "emergence_count": len(state.emergence_events),
        }
        serialized = json.dumps(payload)
        parsed = json.loads(serialized)
        assert parsed["cycle"] == 5
        assert parsed["entropy"] == pytest.approx(0.42)
        assert parsed["phase"] == "INTEGRATION"

    def test_cycle_state_json_round_trip(self) -> None:
        state = FakeState()
        payload = {
            "cycle": state.cycle,
            "phase": state.phase.value,
            "entropy": state.entropy,
        }
        assert json.loads(json.dumps(payload))["cycle"] == 5


class TestPrometheusExporterNoLib:
    def test_update_no_prometheus_no_error(self) -> None:
        exporter = GenesisPrometheusExporter(port=19101)
        state = FakeState()
        exporter.update(state, tension=1.5)

    def test_start_no_prometheus_returns_false_or_true(self) -> None:
        exporter = GenesisPrometheusExporter(port=19102)
        result = exporter.start()
        assert isinstance(result, bool)

    def test_is_available_property(self) -> None:
        exporter = GenesisPrometheusExporter()
        assert isinstance(exporter.is_available, bool)

    def test_update_with_no_crep_no_error(self) -> None:
        class StateNoCREP:
            cycle = 1
            entropy = 0.5
            phi = 1.0
            lagrangian = 0.0
            emergence_events: list[object] = []
            crep = None

            class Phase:
                value = "INITIATION"

            phase = Phase()

        exporter = GenesisPrometheusExporter(port=19103)
        exporter.update(StateNoCREP(), tension=0.0)
