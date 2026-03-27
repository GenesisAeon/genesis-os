"""Tests for genesis_os.plugins.adapters – available-path coverage."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from genesis_os.core.crep import CREPScore
from genesis_os.core.orchestrator import GenesisState
from genesis_os.plugins.adapters import (
    advanced_weighting,
    aeon_ai,
    climate_dashboard,
    cosmic_web,
    entropy_governance,
    entropy_table,
    fieldtheory,
    implosive_genesis,
    mandala_visualizer,
    mirror_machine,
    sigillin,
    sonification_adapter,
    utac_core,
)


@pytest.fixture
def state_with_crep() -> GenesisState:
    crep = CREPScore(coherence=0.7, resonance=0.6, emergence=0.5, poetics=0.4)
    return GenesisState(crep=crep, entropy=0.42, phi=1.2, cycle=3)


@pytest.fixture
def state_no_crep() -> GenesisState:
    return GenesisState()


# ---------------------------------------------------------------------------
# mandala_visualizer
# ---------------------------------------------------------------------------
class TestMandalaVisualizer:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(mandala_visualizer, "_AVAILABLE", False):
            result = mandala_visualizer.plugin_fn(state_with_crep)
        assert result == {"mandala_visualizer_available": False}

    def test_available(self, state_with_crep: GenesisState) -> None:
        with patch.object(mandala_visualizer, "_AVAILABLE", True):
            result = mandala_visualizer.plugin_fn(state_with_crep)
        assert result == {"mandala_visualizer_available": True}


# ---------------------------------------------------------------------------
# sonification_adapter
# ---------------------------------------------------------------------------
class TestSonificationAdapter:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(sonification_adapter, "_AVAILABLE", False):
            result = sonification_adapter.plugin_fn(state_with_crep)
        assert result == {"sonification_available": False}

    def test_available(self, state_with_crep: GenesisState) -> None:
        with patch.object(sonification_adapter, "_AVAILABLE", True):
            result = sonification_adapter.plugin_fn(state_with_crep)
        assert result == {"sonification_available": True}


# ---------------------------------------------------------------------------
# advanced_weighting
# ---------------------------------------------------------------------------
class TestAdvancedWeighting:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(advanced_weighting, "_AVAILABLE", False):
            result = advanced_weighting.plugin_fn(state_with_crep)
        assert result["weighting_available"] is False

    def test_no_crep(self, state_no_crep: GenesisState) -> None:
        with patch.object(advanced_weighting, "_AVAILABLE", True):
            result = advanced_weighting.plugin_fn(state_no_crep)
        assert result["weighting_available"] is True

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_engine = MagicMock()
        mock_weights = MagicMock()
        mock_weights.tolist.return_value = [0.1, 0.2, 0.3, 0.4]
        mock_engine.compute.return_value = mock_weights
        with patch.object(advanced_weighting, "_AVAILABLE", True), \
             patch.object(advanced_weighting, "_ENGINE", mock_engine):
            result = advanced_weighting.plugin_fn(state_with_crep)
        assert result["weighting_available"] is True
        assert result["crep_weights"] == [0.1, 0.2, 0.3, 0.4]

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_engine = MagicMock()
        mock_engine.compute.side_effect = RuntimeError("fail")
        with patch.object(advanced_weighting, "_AVAILABLE", True), \
             patch.object(advanced_weighting, "_ENGINE", mock_engine):
            result = advanced_weighting.plugin_fn(state_with_crep)
        assert result["weighting_available"] is True
        assert result["crep_weights"] is None


# ---------------------------------------------------------------------------
# aeon_ai
# ---------------------------------------------------------------------------
class TestAeonAi:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(aeon_ai, "_AVAILABLE", False):
            result = aeon_ai.plugin_fn(state_with_crep)
        assert result == {"aeon_available": False}

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_detector = MagicMock()
        mock_detector.detect.return_value = "RESONANCE"
        mock_reflector = MagicMock()
        mock_reflector.reflect.return_value = 0.88
        with patch.object(aeon_ai, "_AVAILABLE", True), \
             patch.object(aeon_ai, "_DETECTOR", mock_detector), \
             patch.object(aeon_ai, "_REFLECTOR", mock_reflector):
            result = aeon_ai.plugin_fn(state_with_crep)
        assert result["aeon_available"] is True
        assert result["aeon_phase"] == "RESONANCE"
        assert result["aeon_reflection"] == 0.88

    def test_no_crep(self, state_no_crep: GenesisState) -> None:
        mock_detector = MagicMock()
        mock_reflector = MagicMock()
        with patch.object(aeon_ai, "_AVAILABLE", True), \
             patch.object(aeon_ai, "_DETECTOR", mock_detector), \
             patch.object(aeon_ai, "_REFLECTOR", mock_reflector):
            result = aeon_ai.plugin_fn(state_no_crep)
        assert result["aeon_available"] is True
        mock_detector.detect.assert_not_called()

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_detector = MagicMock()
        mock_detector.detect.side_effect = RuntimeError("boom")
        mock_reflector = MagicMock()
        with patch.object(aeon_ai, "_AVAILABLE", True), \
             patch.object(aeon_ai, "_DETECTOR", mock_detector), \
             patch.object(aeon_ai, "_REFLECTOR", mock_reflector):
            result = aeon_ai.plugin_fn(state_with_crep)
        assert result["aeon_available"] is True
        assert "aeon_phase" not in result


# ---------------------------------------------------------------------------
# climate_dashboard
# ---------------------------------------------------------------------------
class TestClimateDashboard:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(climate_dashboard, "_AVAILABLE", False):
            result = climate_dashboard.plugin_fn(state_with_crep)
        assert result == {"climate_dashboard_available": False}

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_climate = MagicMock()
        mock_climate.entropy.return_value = 0.55
        with patch.object(climate_dashboard, "_AVAILABLE", True), \
             patch.object(climate_dashboard, "_CLIMATE", mock_climate):
            result = climate_dashboard.plugin_fn(state_with_crep)
        assert result["climate_dashboard_available"] is True
        assert result["climate_entropy"] == pytest.approx(0.55)

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_climate = MagicMock()
        mock_climate.entropy.side_effect = RuntimeError("err")
        with patch.object(climate_dashboard, "_AVAILABLE", True), \
             patch.object(climate_dashboard, "_CLIMATE", mock_climate):
            result = climate_dashboard.plugin_fn(state_with_crep)
        assert result["climate_entropy"] is None


# ---------------------------------------------------------------------------
# cosmic_web
# ---------------------------------------------------------------------------
class TestCosmicWeb:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(cosmic_web, "_AVAILABLE", False):
            result = cosmic_web.plugin_fn(state_with_crep)
        assert result["cosmic_web_available"] is False

    def test_no_crep(self, state_no_crep: GenesisState) -> None:
        with patch.object(cosmic_web, "_AVAILABLE", True):
            result = cosmic_web.plugin_fn(state_no_crep)
        assert result["cosmic_web_available"] is True

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_sim = MagicMock()
        mock_sim.step.return_value = 3.14
        with patch.object(cosmic_web, "_AVAILABLE", True), \
             patch.object(cosmic_web, "_SIM", mock_sim):
            result = cosmic_web.plugin_fn(state_with_crep)
        assert result["cosmic_web_available"] is True
        assert result["node_density"] == pytest.approx(3.14)

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_sim = MagicMock()
        mock_sim.step.side_effect = RuntimeError("sim fail")
        with patch.object(cosmic_web, "_AVAILABLE", True), \
             patch.object(cosmic_web, "_SIM", mock_sim):
            result = cosmic_web.plugin_fn(state_with_crep)
        assert result["node_density"] is None


# ---------------------------------------------------------------------------
# entropy_governance
# ---------------------------------------------------------------------------
class TestEntropyGovernance:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(entropy_governance, "_AVAILABLE", False):
            result = entropy_governance.plugin_fn(state_with_crep)
        assert result == {"entropy_governance_available": False}

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_policy = MagicMock()
        mock_policy.apply.return_value = 0.38
        with patch.object(entropy_governance, "_AVAILABLE", True), \
             patch.object(entropy_governance, "_POLICY", mock_policy):
            result = entropy_governance.plugin_fn(state_with_crep)
        assert result["entropy_governance_available"] is True
        assert result["governed_entropy"] == pytest.approx(0.38)

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_policy = MagicMock()
        mock_policy.apply.side_effect = RuntimeError("policy err")
        with patch.object(entropy_governance, "_AVAILABLE", True), \
             patch.object(entropy_governance, "_POLICY", mock_policy):
            result = entropy_governance.plugin_fn(state_with_crep)
        assert result["governed_entropy"] is None


# ---------------------------------------------------------------------------
# entropy_table
# ---------------------------------------------------------------------------
class TestEntropyTable:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(entropy_table, "_AVAILABLE", False):
            result = entropy_table.plugin_fn(state_with_crep)
        assert result == {"entropy_table_available": False}

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_table = MagicMock()
        mock_table.lookup.return_value = {"row": 5}
        with patch.object(entropy_table, "_AVAILABLE", True), \
             patch.object(entropy_table, "_TABLE", mock_table):
            result = entropy_table.plugin_fn(state_with_crep)
        assert result["entropy_table_available"] is True
        assert result["entropy_table_entry"] == {"row": 5}

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_table = MagicMock()
        mock_table.lookup.side_effect = KeyError("missing")
        with patch.object(entropy_table, "_AVAILABLE", True), \
             patch.object(entropy_table, "_TABLE", mock_table):
            result = entropy_table.plugin_fn(state_with_crep)
        assert result["entropy_table_entry"] is None


# ---------------------------------------------------------------------------
# fieldtheory
# ---------------------------------------------------------------------------
class TestFieldTheory:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(fieldtheory, "_AVAILABLE", False):
            result = fieldtheory.plugin_fn(state_with_crep)
        assert result == {"fieldtheory_available": False}

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_potential = MagicMock()
        mock_potential.compute.return_value = 2.71
        with patch.object(fieldtheory, "_AVAILABLE", True), \
             patch.object(fieldtheory, "_POTENTIAL", mock_potential):
            result = fieldtheory.plugin_fn(state_with_crep)
        assert result["fieldtheory_available"] is True
        assert result["field_potential"] == pytest.approx(2.71)

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_potential = MagicMock()
        mock_potential.compute.side_effect = ValueError("oops")
        with patch.object(fieldtheory, "_AVAILABLE", True), \
             patch.object(fieldtheory, "_POTENTIAL", mock_potential):
            result = fieldtheory.plugin_fn(state_with_crep)
        assert result["field_potential"] is None


# ---------------------------------------------------------------------------
# implosive_genesis
# ---------------------------------------------------------------------------
class TestImplosiveGenesis:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(implosive_genesis, "_AVAILABLE", False):
            result = implosive_genesis.plugin_fn(state_with_crep)
        assert result == {"implosive_genesis_available": False}

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_field = MagicMock()
        mock_field.compute.return_value = 1.618
        with patch.object(implosive_genesis, "_AVAILABLE", True), \
             patch.object(implosive_genesis, "_FIELD", mock_field):
            result = implosive_genesis.plugin_fn(state_with_crep)
        assert result["implosive_genesis_available"] is True
        assert result["implosive_strength"] == pytest.approx(1.618)

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_field = MagicMock()
        mock_field.compute.side_effect = OverflowError("overflow")
        with patch.object(implosive_genesis, "_AVAILABLE", True), \
             patch.object(implosive_genesis, "_FIELD", mock_field):
            result = implosive_genesis.plugin_fn(state_with_crep)
        assert result["implosive_strength"] is None


# ---------------------------------------------------------------------------
# mirror_machine
# ---------------------------------------------------------------------------
class TestMirrorMachine:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(mirror_machine, "_AVAILABLE", False):
            result = mirror_machine.plugin_fn(state_with_crep)
        assert result["mirror_available"] is False

    def test_no_crep(self, state_no_crep: GenesisState) -> None:
        with patch.object(mirror_machine, "_AVAILABLE", True):
            result = mirror_machine.plugin_fn(state_no_crep)
        assert result["mirror_available"] is True

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_mirror = MagicMock()
        mock_mirror.reflect.return_value = 0.99
        with patch.object(mirror_machine, "_AVAILABLE", True), \
             patch.object(mirror_machine, "_MIRROR", mock_mirror):
            result = mirror_machine.plugin_fn(state_with_crep)
        assert result["mirror_available"] is True
        assert result["mirror_resonance"] == pytest.approx(0.99)

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_mirror = MagicMock()
        mock_mirror.reflect.side_effect = RuntimeError("mirror broke")
        with patch.object(mirror_machine, "_AVAILABLE", True), \
             patch.object(mirror_machine, "_MIRROR", mock_mirror):
            result = mirror_machine.plugin_fn(state_with_crep)
        assert result["mirror_resonance"] is None


# ---------------------------------------------------------------------------
# sigillin
# ---------------------------------------------------------------------------
class TestSigillin:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(sigillin, "_AVAILABLE", False):
            result = sigillin.plugin_fn(state_with_crep)
        assert result == {"sigillin_available": False}

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_sigil = MagicMock()
        mock_sigil.generate.return_value = "⊕RESONANCE⊕"
        with patch.object(sigillin, "_AVAILABLE", True), \
             patch.object(sigillin, "_SIGIL", mock_sigil):
            result = sigillin.plugin_fn(state_with_crep)
        assert result["sigillin_available"] is True
        assert result["sigil_token"] == "⊕RESONANCE⊕"

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_sigil = MagicMock()
        mock_sigil.generate.side_effect = RuntimeError("sigil err")
        with patch.object(sigillin, "_AVAILABLE", True), \
             patch.object(sigillin, "_SIGIL", mock_sigil):
            result = sigillin.plugin_fn(state_with_crep)
        assert result["sigil_token"] is None


# ---------------------------------------------------------------------------
# utac_core
# ---------------------------------------------------------------------------
class TestUtacCore:
    def test_unavailable(self, state_with_crep: GenesisState) -> None:
        with patch.object(utac_core, "_AVAILABLE", False):
            result = utac_core.plugin_fn(state_with_crep)
        assert result["utac_core_available"] is False

    def test_no_crep(self, state_no_crep: GenesisState) -> None:
        with patch.object(utac_core, "_AVAILABLE", True):
            result = utac_core.plugin_fn(state_no_crep)
        assert result["utac_core_available"] is True

    def test_success(self, state_with_crep: GenesisState) -> None:
        mock_engine = MagicMock()
        mock_engine.step.return_value = 0.37
        with patch.object(utac_core, "_AVAILABLE", True), \
             patch.object(utac_core, "_ENGINE", mock_engine):
            result = utac_core.plugin_fn(state_with_crep)
        assert result["utac_core_available"] is True
        assert result["utac_entropy"] == pytest.approx(0.37)

    def test_exception(self, state_with_crep: GenesisState) -> None:
        mock_engine = MagicMock()
        mock_engine.step.side_effect = RuntimeError("utac fail")
        with patch.object(utac_core, "_AVAILABLE", True), \
             patch.object(utac_core, "_ENGINE", mock_engine):
            result = utac_core.plugin_fn(state_with_crep)
        assert result["utac_entropy"] is None

    def test_compute_tension_metric_returns_float(self) -> None:
        result = utac_core.compute_tension_metric(1.2, 15.0)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_compute_tension_metric_zero_anomaly(self) -> None:
        # Zero anomaly → gamma=1 → minimum tension (close to 0)
        result = utac_core.compute_tension_metric(0.0, 30.0)
        assert result == pytest.approx(0.0, abs=1e-9)

    def test_compute_tension_metric_high_anomaly(self) -> None:
        # High anomaly produces higher tension than zero anomaly at same ice
        low = utac_core.compute_tension_metric(0.0, 20.0)
        high = utac_core.compute_tension_metric(3.0, 20.0)
        assert high > low

    def test_compute_tension_metric_ice_stress(self) -> None:
        # Lower ice volume → higher tension (more ice stress)
        plenty_ice = utac_core.compute_tension_metric(1.0, 30.0)
        low_ice = utac_core.compute_tension_metric(1.0, 5.0)
        assert low_ice > plenty_ice

    def test_compute_tension_metric_top_level_import(self) -> None:
        from genesis_os import utac_core as uc
        result = uc.compute_tension_metric(1.38, 12.8)
        assert isinstance(result, float)
