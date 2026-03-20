"""Contract tests using mocked optional packages to achieve full adapter coverage.

Patches module-level ``_AVAILABLE`` and engine stubs so every code path in
each adapter is exercised without requiring the real optional packages.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from genesis_os.core.crep import CREPScore
from genesis_os.core.orchestrator import GenesisState
from genesis_os.core.phase import Phase


def _state_with_crep() -> GenesisState:
    state = GenesisState()
    state.crep = CREPScore(coherence=0.7, resonance=0.6, emergence=0.5, poetics=0.8)
    state.phase = Phase.INITIATION
    state.cycle = 3
    state.phi = 1.5
    state.entropy = 0.4
    return state


# ──────────────────────────────────────────────────────────────────────────────
# aeon_ai adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestAeonAIAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.aeon_ai as mod

        mock_detector = MagicMock()
        mock_detector.detect.return_value = "Initiation"
        mock_reflector = MagicMock()
        mock_reflector.reflect.return_value = 0.85

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_DETECTOR", mock_detector),
            patch.object(mod, "_REFLECTOR", mock_reflector),
        ):
            state = _state_with_crep()
            result = mod.plugin_fn(state)

        assert result["aeon_available"] is True
        assert "aeon_phase" in result
        assert "aeon_reflection" in result

    def test_available_false_path(self) -> None:
        import genesis_os.plugins.adapters.aeon_ai as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["aeon_available"] is False

    def test_available_no_crep(self) -> None:
        import genesis_os.plugins.adapters.aeon_ai as mod

        with patch.object(mod, "_AVAILABLE", True):
            state = GenesisState()
            result = mod.plugin_fn(state)

        assert result["aeon_available"] is True

    def test_exception_in_detector(self) -> None:
        import genesis_os.plugins.adapters.aeon_ai as mod

        mock_detector = MagicMock()
        mock_detector.detect.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_DETECTOR", mock_detector),
            patch.object(mod, "_REFLECTOR", MagicMock()),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["aeon_available"] is True


# ──────────────────────────────────────────────────────────────────────────────
# advanced_weighting adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestAdvancedWeightingAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.advanced_weighting as mod

        mock_engine = MagicMock()
        mock_engine.compute.return_value = np.array([0.3, 0.3, 0.2, 0.2])

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_ENGINE", mock_engine),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["weighting_available"] is True
        assert result["crep_weights"] is not None

    def test_available_false_returns_false(self) -> None:
        import genesis_os.plugins.adapters.advanced_weighting as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["weighting_available"] is False

    def test_no_crep_when_available(self) -> None:
        import genesis_os.plugins.adapters.advanced_weighting as mod

        with patch.object(mod, "_AVAILABLE", True):
            state = GenesisState()  # no crep
            result = mod.plugin_fn(state)

        assert result["weighting_available"] is True

    def test_exception_in_engine(self) -> None:
        import genesis_os.plugins.adapters.advanced_weighting as mod

        mock_engine = MagicMock()
        mock_engine.compute.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_ENGINE", mock_engine),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["crep_weights"] is None


# ──────────────────────────────────────────────────────────────────────────────
# fieldtheory adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestFieldtheoryAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.fieldtheory as mod

        mock_pot = MagicMock()
        mock_pot.compute.return_value = 2.5

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_POTENTIAL", mock_pot),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["fieldtheory_available"] is True
        assert result["field_potential"] == pytest.approx(2.5)

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.fieldtheory as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["fieldtheory_available"] is False

    def test_exception_returns_none(self) -> None:
        import genesis_os.plugins.adapters.fieldtheory as mod

        mock_pot = MagicMock()
        mock_pot.compute.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_POTENTIAL", mock_pot),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["field_potential"] is None


# ──────────────────────────────────────────────────────────────────────────────
# mirror_machine adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestMirrorMachineAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.mirror_machine as mod

        mock_mirror = MagicMock()
        mock_mirror.reflect.return_value = 0.75

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_MIRROR", mock_mirror),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["mirror_available"] is True
        assert result["mirror_resonance"] == pytest.approx(0.75)

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.mirror_machine as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["mirror_available"] is False

    def test_no_crep(self) -> None:
        import genesis_os.plugins.adapters.mirror_machine as mod

        with patch.object(mod, "_AVAILABLE", True):
            result = mod.plugin_fn(GenesisState())

        assert result["mirror_available"] is True

    def test_exception_returns_none(self) -> None:
        import genesis_os.plugins.adapters.mirror_machine as mod

        mock_mirror = MagicMock()
        mock_mirror.reflect.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_MIRROR", mock_mirror),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["mirror_resonance"] is None


# ──────────────────────────────────────────────────────────────────────────────
# cosmic_web adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestCosmicWebAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.cosmic_web as mod

        mock_sim = MagicMock()
        mock_sim.step.return_value = 0.42

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_SIM", mock_sim),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["cosmic_web_available"] is True
        assert result["node_density"] == pytest.approx(0.42)

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.cosmic_web as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["cosmic_web_available"] is False

    def test_exception_returns_none(self) -> None:
        import genesis_os.plugins.adapters.cosmic_web as mod

        mock_sim = MagicMock()
        mock_sim.step.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_SIM", mock_sim),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["node_density"] is None


# ──────────────────────────────────────────────────────────────────────────────
# sigillin adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestSigillinAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.sigillin as mod

        mock_sigil = MagicMock()
        mock_sigil.generate.return_value = "SIGIL_XYZ"

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_SIGIL", mock_sigil),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["sigillin_available"] is True
        assert result["sigil_token"] == "SIGIL_XYZ"

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.sigillin as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["sigillin_available"] is False

    def test_exception_returns_none(self) -> None:
        import genesis_os.plugins.adapters.sigillin as mod

        mock_sigil = MagicMock()
        mock_sigil.generate.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_SIGIL", mock_sigil),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["sigil_token"] is None


# ──────────────────────────────────────────────────────────────────────────────
# entropy_governance adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestEntropyGovernanceAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.entropy_governance as mod

        mock_policy = MagicMock()
        mock_policy.apply.return_value = 0.35

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_POLICY", mock_policy),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["entropy_governance_available"] is True
        assert result["governed_entropy"] == pytest.approx(0.35)

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.entropy_governance as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["entropy_governance_available"] is False

    def test_exception_returns_none(self) -> None:
        import genesis_os.plugins.adapters.entropy_governance as mod

        mock_policy = MagicMock()
        mock_policy.apply.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_POLICY", mock_policy),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["governed_entropy"] is None


# ──────────────────────────────────────────────────────────────────────────────
# utac_core adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestUTACCoreAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.utac_core as mod

        mock_engine = MagicMock()
        mock_engine.step.return_value = 0.55

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_ENGINE", mock_engine),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["utac_core_available"] is True
        assert result["utac_entropy"] == pytest.approx(0.55)

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.utac_core as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["utac_core_available"] is False

    def test_no_crep(self) -> None:
        import genesis_os.plugins.adapters.utac_core as mod

        with patch.object(mod, "_AVAILABLE", True):
            result = mod.plugin_fn(GenesisState())

        assert result["utac_core_available"] is True

    def test_exception_returns_none(self) -> None:
        import genesis_os.plugins.adapters.utac_core as mod

        mock_engine = MagicMock()
        mock_engine.step.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_ENGINE", mock_engine),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["utac_entropy"] is None


# ──────────────────────────────────────────────────────────────────────────────
# climate_dashboard adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestClimateDashboardAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.climate_dashboard as mod

        mock_climate = MagicMock()
        mock_climate.entropy.return_value = 0.45

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_CLIMATE", mock_climate),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["climate_dashboard_available"] is True
        assert result["climate_entropy"] == pytest.approx(0.45)

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.climate_dashboard as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["climate_dashboard_available"] is False

    def test_exception_returns_none(self) -> None:
        import genesis_os.plugins.adapters.climate_dashboard as mod

        mock_climate = MagicMock()
        mock_climate.entropy.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_CLIMATE", mock_climate),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["climate_entropy"] is None


# ──────────────────────────────────────────────────────────────────────────────
# implosive_genesis adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestImplosiveGenesisAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.implosive_genesis as mod

        mock_field = MagicMock()
        mock_field.compute.return_value = 3.14

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_FIELD", mock_field),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["implosive_genesis_available"] is True
        assert result["implosive_strength"] == pytest.approx(3.14)

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.implosive_genesis as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["implosive_genesis_available"] is False

    def test_exception_returns_none(self) -> None:
        import genesis_os.plugins.adapters.implosive_genesis as mod

        mock_field = MagicMock()
        mock_field.compute.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_FIELD", mock_field),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["implosive_strength"] is None


# ──────────────────────────────────────────────────────────────────────────────
# entropy_table adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestEntropyTableAdapterMocked:
    def test_available_true_path(self) -> None:
        import genesis_os.plugins.adapters.entropy_table as mod

        mock_table = MagicMock()
        mock_table.lookup.return_value = {"level": "medium", "code": 3}

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_TABLE", mock_table),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["entropy_table_available"] is True
        assert result["entropy_table_entry"] is not None

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.entropy_table as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(_state_with_crep())

        assert result["entropy_table_available"] is False

    def test_exception_returns_none(self) -> None:
        import genesis_os.plugins.adapters.entropy_table as mod

        mock_table = MagicMock()
        mock_table.lookup.side_effect = RuntimeError("fail")

        with (
            patch.object(mod, "_AVAILABLE", True),
            patch.object(mod, "_TABLE", mock_table),
        ):
            result = mod.plugin_fn(_state_with_crep())

        assert result["entropy_table_entry"] is None


# ──────────────────────────────────────────────────────────────────────────────
# mandala_visualizer and sonification_adapter
# ──────────────────────────────────────────────────────────────────────────────


class TestMandalaVisualizerAdapterMocked:
    def test_available_true(self) -> None:
        import genesis_os.plugins.adapters.mandala_visualizer as mod

        with patch.object(mod, "_AVAILABLE", True):
            result = mod.plugin_fn(GenesisState())

        assert result["mandala_visualizer_available"] is True

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.mandala_visualizer as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(GenesisState())

        assert result["mandala_visualizer_available"] is False


class TestSonificationAdapterMocked:
    def test_available_true(self) -> None:
        import genesis_os.plugins.adapters.sonification_adapter as mod

        with patch.object(mod, "_AVAILABLE", True):
            result = mod.plugin_fn(GenesisState())

        assert result["sonification_available"] is True

    def test_available_false(self) -> None:
        import genesis_os.plugins.adapters.sonification_adapter as mod

        with patch.object(mod, "_AVAILABLE", False):
            result = mod.plugin_fn(GenesisState())

        assert result["sonification_available"] is False


# ──────────────────────────────────────────────────────────────────────────────
# PluginRegistry._load success path
# ──────────────────────────────────────────────────────────────────────────────


class TestPluginRegistryLoadMocked:
    def test_load_success_path(self) -> None:
        from genesis_os.plugins.registry import PluginRegistry

        mock_mod = MagicMock()
        mock_mod.plugin_fn = lambda s: {"ok": True}

        registry = PluginRegistry(auto_discover=False)
        with patch("importlib.import_module", return_value=mock_mod):
            result = registry._load("test_pkg", "fake.module.path")

        assert result is True
        assert "test_pkg" in registry.active

    def test_load_failure_exception(self) -> None:
        from genesis_os.plugins.registry import PluginRegistry

        registry = PluginRegistry(auto_discover=False)
        with patch("importlib.import_module", side_effect=Exception("generic error")):
            result = registry._load("bad_pkg", "fake.module.bad")

        assert result is False
        assert "bad_pkg" in registry.failed
