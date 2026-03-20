"""Plugin registry: discovers and exposes optional package adapters."""

from __future__ import annotations

import importlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from genesis_os.core.orchestrator import GenesisState

logger = logging.getLogger(__name__)

_KNOWN_ADAPTERS: dict[str, str] = {
    "aeon_ai": "genesis_os.plugins.adapters.aeon_ai",
    "advanced_weighting": "genesis_os.plugins.adapters.advanced_weighting",
    "fieldtheory": "genesis_os.plugins.adapters.fieldtheory",
    "mirror_machine": "genesis_os.plugins.adapters.mirror_machine",
    "cosmic_web": "genesis_os.plugins.adapters.cosmic_web",
    "sigillin": "genesis_os.plugins.adapters.sigillin",
    "entropy_governance": "genesis_os.plugins.adapters.entropy_governance",
    "utac_core": "genesis_os.plugins.adapters.utac_core",
    "mandala_visualizer": "genesis_os.plugins.adapters.mandala_visualizer",
    "sonification": "genesis_os.plugins.adapters.sonification_adapter",
    "climate_dashboard": "genesis_os.plugins.adapters.climate_dashboard",
    "implosive_genesis": "genesis_os.plugins.adapters.implosive_genesis",
    "entropy_table": "genesis_os.plugins.adapters.entropy_table",
}


@dataclass
class PluginRegistry:
    """Discovers and manages plugin adapters for the GenesisOS orchestrator.

    Args:
        auto_discover: If True, attempt to load all known adapters on init.
    """

    auto_discover: bool = True
    _plugins: dict[str, Callable[[GenesisState], dict[str, Any]]] = field(
        default_factory=dict, init=False
    )
    _failed: list[str] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if self.auto_discover:
            self.discover()

    def discover(self) -> dict[str, bool]:
        """Attempt to import and register all known adapters.

        Returns:
            Dict mapping adapter name to load success status.
        """
        results: dict[str, bool] = {}
        for name, module_path in _KNOWN_ADAPTERS.items():
            results[name] = self._load(name, module_path)
        return results

    def _load(self, name: str, module_path: str) -> bool:
        try:
            mod = importlib.import_module(module_path)
            if hasattr(mod, "plugin_fn"):
                self._plugins[name] = mod.plugin_fn
                logger.debug("Loaded plugin adapter: %s", name)
                return True
        except ImportError:
            logger.debug("Plugin '%s' not available (ImportError).", name)
        except Exception:
            logger.warning("Plugin '%s' failed to load.", name, exc_info=True)
        self._failed.append(name)
        return False

    def register(self, name: str, fn: Callable[[GenesisState], dict[str, Any]]) -> None:
        """Manually register a plugin function.

        Args:
            name: Unique plugin name.
            fn: Callable accepting GenesisState and returning a state dict.
        """
        self._plugins[name] = fn

    def unregister(self, name: str) -> bool:
        """Remove a plugin by name.

        Args:
            name: Plugin name to remove.

        Returns:
            True if the plugin existed and was removed.
        """
        return self._plugins.pop(name, None) is not None

    @property
    def active(self) -> list[str]:
        """List of successfully loaded plugin names."""
        return list(self._plugins.keys())

    @property
    def failed(self) -> list[str]:
        """List of plugin names that failed to load."""
        return list(self._failed)

    @property
    def plugins(self) -> dict[str, Callable[[GenesisState], dict[str, Any]]]:
        """Dict of active plugin functions."""
        return dict(self._plugins)
