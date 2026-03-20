"""Unit tests for genesis_os.plugins.registry."""

from __future__ import annotations

import pytest

from genesis_os.core.orchestrator import GenesisConfig, GenesisOS, GenesisState
from genesis_os.plugins.registry import PluginRegistry


@pytest.fixture
def empty_registry() -> PluginRegistry:
    return PluginRegistry(auto_discover=False)


@pytest.fixture
def state() -> GenesisState:
    return GenesisState()


class TestPluginRegistry:
    def test_created_with_auto_discover_false(self, empty_registry: PluginRegistry) -> None:
        assert empty_registry.active == []

    def test_register_plugin(self, empty_registry: PluginRegistry, state: GenesisState) -> None:
        empty_registry.register("test", lambda s: {"x": 1})
        assert "test" in empty_registry.active

    def test_registered_plugin_callable(self, empty_registry: PluginRegistry, state: GenesisState) -> None:
        empty_registry.register("test", lambda s: {"x": 42})
        result = empty_registry.plugins["test"](state)
        assert result["x"] == 42

    def test_unregister_existing(self, empty_registry: PluginRegistry) -> None:
        empty_registry.register("test", lambda s: {})
        removed = empty_registry.unregister("test")
        assert removed is True
        assert "test" not in empty_registry.active

    def test_unregister_nonexistent(self, empty_registry: PluginRegistry) -> None:
        removed = empty_registry.unregister("nonexistent")
        assert removed is False

    def test_plugins_returns_copy(self, empty_registry: PluginRegistry) -> None:
        empty_registry.register("a", lambda s: {})
        p = empty_registry.plugins
        p.clear()
        assert len(empty_registry.plugins) == 1

    def test_active_list(self, empty_registry: PluginRegistry) -> None:
        empty_registry.register("a", lambda s: {})
        empty_registry.register("b", lambda s: {})
        assert set(empty_registry.active) == {"a", "b"}

    def test_discover_returns_dict(self, empty_registry: PluginRegistry) -> None:
        results = empty_registry.discover()
        assert isinstance(results, dict)

    def test_discover_all_packages_attempted(self, empty_registry: PluginRegistry) -> None:
        results = empty_registry.discover()
        # Some may fail (not installed), but all known adapters should be in results
        assert "aeon_ai" in results
        assert "cosmic_web" in results

    def test_failed_list_populated_when_not_installed(self, empty_registry: PluginRegistry) -> None:
        empty_registry.discover()
        # All packages are optional, so some will fail if not installed
        assert isinstance(empty_registry.failed, list)

    def test_plugins_integrated_in_genesis(self) -> None:
        call_log: list[str] = []

        def my_plugin(s: GenesisState) -> dict:
            call_log.append("called")
            return {"custom_value": 99}

        registry = PluginRegistry(auto_discover=False)
        registry.register("my_plugin", my_plugin)
        g = GenesisOS(config=GenesisConfig(seed=1), plugins=registry.plugins)
        g.run(max_cycles=3)
        assert len(call_log) == 3
