"""Plugin adapters: thin wrappers around optional full-stack packages.

All adapters implement a common interface and degrade gracefully when their
target package is not installed.
"""

from __future__ import annotations

from genesis_os.plugins.registry import PluginRegistry

__all__ = ["PluginRegistry"]
