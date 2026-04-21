"""Sigillin — trilayer synchronization protocol.

Every important genesis-os theoretical concept must exist in three forms:
    YAML  — machine-readable parameter definitions
    JSON  — API-accessible format
    MD    — human-readable documentation

The SigillinSync class validates and generates these trilayer documents.
CI integration: pytest --sigillin-check flag validates gaps → CI fails.
"""

from genesis_os.sigillin.sync import SigillinSync

__all__ = ["SigillinSync"]
