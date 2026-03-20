"""Contract tests for all plugin adapters.

Each adapter must expose a ``plugin_fn`` callable that:
1. Accepts a GenesisState argument.
2. Returns a dict.
3. Does not raise when the underlying package is absent.
4. Includes an ``*_available`` key indicating package presence.
"""

from __future__ import annotations

import importlib

import pytest

from genesis_os.core.crep import CREPScore
from genesis_os.core.orchestrator import GenesisState

_ADAPTER_MODULES = [
    "genesis_os.plugins.adapters.aeon_ai",
    "genesis_os.plugins.adapters.advanced_weighting",
    "genesis_os.plugins.adapters.fieldtheory",
    "genesis_os.plugins.adapters.mirror_machine",
    "genesis_os.plugins.adapters.cosmic_web",
    "genesis_os.plugins.adapters.sigillin",
    "genesis_os.plugins.adapters.entropy_governance",
    "genesis_os.plugins.adapters.utac_core",
    "genesis_os.plugins.adapters.mandala_visualizer",
    "genesis_os.plugins.adapters.sonification_adapter",
    "genesis_os.plugins.adapters.climate_dashboard",
    "genesis_os.plugins.adapters.implosive_genesis",
    "genesis_os.plugins.adapters.entropy_table",
]


def _make_state() -> GenesisState:
    state = GenesisState()
    state.crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
    return state


@pytest.fixture
def sample_state() -> GenesisState:
    return _make_state()


@pytest.mark.parametrize("module_path", _ADAPTER_MODULES)
class TestAdapterContract:
    def test_module_importable(self, module_path: str) -> None:
        """Each adapter module must be importable."""
        mod = importlib.import_module(module_path)
        assert mod is not None

    def test_plugin_fn_exists(self, module_path: str) -> None:
        """Each adapter must define plugin_fn."""
        mod = importlib.import_module(module_path)
        assert hasattr(mod, "plugin_fn"), f"{module_path} missing plugin_fn"

    def test_plugin_fn_callable(self, module_path: str) -> None:
        """plugin_fn must be callable."""
        mod = importlib.import_module(module_path)
        assert callable(mod.plugin_fn)

    def test_plugin_fn_returns_dict(self, module_path: str, sample_state: GenesisState) -> None:
        """plugin_fn must return a dict."""
        mod = importlib.import_module(module_path)
        result = mod.plugin_fn(sample_state)
        assert isinstance(result, dict)

    def test_plugin_fn_no_raise(self, module_path: str, sample_state: GenesisState) -> None:
        """plugin_fn must not raise any exception."""
        mod = importlib.import_module(module_path)
        try:
            mod.plugin_fn(sample_state)
        except Exception as exc:
            pytest.fail(f"{module_path}.plugin_fn raised: {exc!r}")

    def test_plugin_fn_has_available_key(self, module_path: str, sample_state: GenesisState) -> None:
        """plugin_fn result must contain an *_available key."""
        mod = importlib.import_module(module_path)
        result = mod.plugin_fn(sample_state)
        has_avail = any(k.endswith("_available") for k in result)
        assert has_avail, f"{module_path} result missing *_available key: {result}"

    def test_plugin_fn_available_key_is_bool(self, module_path: str, sample_state: GenesisState) -> None:
        """The *_available value must be a boolean."""
        mod = importlib.import_module(module_path)
        result = mod.plugin_fn(sample_state)
        avail_keys = [k for k in result if k.endswith("_available")]
        for k in avail_keys:
            assert isinstance(result[k], bool), f"{k} is not bool in {module_path}"

    def test_plugin_fn_works_with_empty_state(self, module_path: str) -> None:
        """plugin_fn must handle a freshly created GenesisState."""
        mod = importlib.import_module(module_path)
        state = GenesisState()
        try:
            result = mod.plugin_fn(state)
            assert isinstance(result, dict)
        except Exception as exc:
            pytest.fail(f"{module_path}.plugin_fn raised with empty state: {exc!r}")

    def test_plugin_fn_deterministic(self, module_path: str, sample_state: GenesisState) -> None:
        """Calling plugin_fn twice with the same state must not raise."""
        mod = importlib.import_module(module_path)
        r1 = mod.plugin_fn(sample_state)
        r2 = mod.plugin_fn(sample_state)
        # Both must be dicts (values may differ for stateful plugins)
        assert isinstance(r1, dict)
        assert isinstance(r2, dict)
