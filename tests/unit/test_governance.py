"""Tests für genesis_os.governance — Phase H."""

from __future__ import annotations

import pytest

from genesis_os.core.crep import CREPScore
from genesis_os.governance.ethics_gate import EthicsDecision, EthicsGate
from genesis_os.governance.opa_bridge import OPABridge, PolicyDecision
from genesis_os.governance.personhood import PersonhoodLevel, assess_personhood


class TestPersonhoodLevel:
    def test_no_crep_returns_informational(self) -> None:
        level = assess_personhood(None)
        assert level == PersonhoodLevel.INFORMATIONAL
        assert level.value == 0

    def test_zero_crep_returns_informational(self) -> None:
        crep = CREPScore(coherence=0.0, resonance=0.0, emergence=0.0, poetics=0.0)
        assert assess_personhood(crep) == PersonhoodLevel.INFORMATIONAL

    def test_only_coherence_returns_reactive(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.0, emergence=0.0, poetics=0.0)
        assert assess_personhood(crep) == PersonhoodLevel.REACTIVE

    def test_coherence_resonance_returns_adaptive(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.0, poetics=0.0)
        assert assess_personhood(crep) == PersonhoodLevel.ADAPTIVE

    def test_cre_returns_emergent(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.05)
        assert assess_personhood(crep) == PersonhoodLevel.EMERGENT

    def test_full_crep_high_gamma_returns_poetic(self) -> None:
        crep = CREPScore(coherence=1.0, resonance=1.0, emergence=1.0, poetics=1.0)
        assert crep.gamma > 0.8
        assert assess_personhood(crep) == PersonhoodLevel.POETIC

    def test_full_crep_low_gamma_returns_emergent(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        assert crep.gamma < 0.8
        assert assess_personhood(crep) == PersonhoodLevel.EMERGENT

    def test_description_property(self) -> None:
        assert "Poetisches" in PersonhoodLevel.POETIC.description
        assert "Informationssystem" in PersonhoodLevel.INFORMATIONAL.description

    def test_unified_mandala_name(self) -> None:
        assert PersonhoodLevel.EMERGENT.unified_mandala_name == "emergent"
        assert PersonhoodLevel.POETIC.unified_mandala_name == "poetic"

    def test_int_enum_ordering(self) -> None:
        assert PersonhoodLevel.POETIC > PersonhoodLevel.REACTIVE
        assert PersonhoodLevel.INFORMATIONAL < PersonhoodLevel.ADAPTIVE


class FakeState:
    def __init__(self, crep: CREPScore | None = None) -> None:
        self.crep = crep
        self.entropy = 0.5
        self.cycle = 1


class TestEthicsGate:
    def test_approved_below_tension(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        gate = EthicsGate(tension_threshold=5.0)
        decision = gate.check(FakeState(crep), tension=1.0)
        assert decision.approved is True

    def test_blocked_high_tension(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        gate = EthicsGate(tension_threshold=5.0)
        decision = gate.check(FakeState(crep), tension=10.0)
        assert decision.approved is False
        assert "Tension" in decision.reason

    def test_blocked_low_personhood(self) -> None:
        gate = EthicsGate(min_personhood=PersonhoodLevel.EMERGENT)
        crep = CREPScore(coherence=0.5, resonance=0.0, emergence=0.0, poetics=0.0)
        decision = gate.check(FakeState(crep), tension=0.0)
        assert decision.approved is False
        assert "PersonhoodLevel" in decision.reason

    def test_gate_disabled_always_approved(self) -> None:
        gate = EthicsGate(tension_threshold=1.0, enabled=False)
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        decision = gate.check(FakeState(crep), tension=100.0)
        assert decision.approved is True
        assert "disabled" in decision.reason

    def test_decision_log_grows(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        gate = EthicsGate()
        for _ in range(3):
            gate.check(FakeState(crep), tension=0.0)
        assert len(gate.decision_log) == 3

    def test_decision_log_is_copy(self) -> None:
        gate = EthicsGate()
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        gate.check(FakeState(crep))
        log = gate.decision_log
        log.clear()
        assert len(gate.decision_log) == 1

    def test_last_decision_none_initially(self) -> None:
        gate = EthicsGate()
        assert gate.last_decision is None

    def test_last_decision_after_check(self) -> None:
        gate = EthicsGate()
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        gate.check(FakeState(crep))
        assert gate.last_decision is not None

    def test_reset_clears_log(self) -> None:
        gate = EthicsGate()
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        gate.check(FakeState(crep))
        gate.reset()
        assert len(gate.decision_log) == 0

    def test_no_crep_defaults_to_informational(self) -> None:
        gate = EthicsGate()
        decision = gate.check(FakeState(crep=None), tension=0.0)
        assert decision.personhood_level == PersonhoodLevel.INFORMATIONAL


class TestOPABridge:
    def test_fallback_no_server(self) -> None:
        bridge = OPABridge(opa_url="http://localhost:18181")
        decision = bridge.evaluate({"entropy": 0.5})
        assert decision.allowed is True
        assert "OPA" in decision.reason or "not installed" in decision.reason

    def test_is_available_false_no_server(self) -> None:
        bridge = OPABridge(opa_url="http://localhost:18181")
        assert bridge.is_available() is False

    def test_close_no_error(self) -> None:
        bridge = OPABridge(opa_url="http://localhost:18181")
        bridge.close()

    def test_policy_decision_dataclass(self) -> None:
        dec = PolicyDecision(allowed=True, reason="test", policy_name="genesis/allow")
        assert dec.allowed is True
        assert dec.policy_name == "genesis/allow"


class TestOrchestatorEthicsIntegration:
    def test_genesis_runs_with_ethics_gate(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        config = GenesisConfig(
            max_cycles=5,
            entropy=0.5,
            ethics_gate_enabled=True,
            tension_threshold=5.0,
        )
        genesis = GenesisOS(config=config)
        state = genesis.run()
        assert state.cycle > 0

    def test_genesis_runs_without_ethics_gate(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        config = GenesisConfig(
            max_cycles=5,
            ethics_gate_enabled=False,
        )
        genesis = GenesisOS(config=config)
        state = genesis.run()
        assert state.cycle == 5

    def test_genesis_config_has_ethics_fields(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig

        config = GenesisConfig()
        assert hasattr(config, "ethics_gate_enabled")
        assert hasattr(config, "tension_threshold")
        assert hasattr(config, "min_personhood_level")
        assert config.ethics_gate_enabled is True
        assert config.tension_threshold == pytest.approx(5.0)
        assert config.min_personhood_level == 0
