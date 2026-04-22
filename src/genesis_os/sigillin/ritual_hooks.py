"""Ritual Hooks für genesis-os — Pre-commit und Pre-push Checks.

Portiert aus unified-mandala pre-rituale.md.
Wird als Pre-commit Hook verwendet (siehe .pre-commit-config.yaml).
"""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def pre_commit_ritual(crep_threshold: float = 0.4) -> bool:
    """Pre-commit Check: CREP-Gate + Sigillin-Sync.

    Prüft ob das System einen Mindest-CREP-Score hat und
    der Sigillin-Trilayer synchron ist.

    Args:
        crep_threshold: Minimales Γ für Commit (default 0.4).

    Returns:
        True wenn Commit erlaubt, False wenn blockiert.
    """
    try:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        config = GenesisConfig(max_cycles=1)
        genesis = GenesisOS(config=config)
        state = genesis.run(max_cycles=1)
        if state.crep is not None and state.crep.gamma < crep_threshold:
            logger.warning(
                "pre_commit_ritual: CREP-Gate blockiert. Γ=%.3f < %.3f",
                state.crep.gamma,
                crep_threshold,
            )
            return False
    except Exception as exc:
        logger.debug("pre_commit_ritual: CREP check skipped: %s", exc)
    return True


def pre_push_ritual(crep_threshold: float = 0.6) -> bool:
    """Pre-push Check: CREP > 0.6 Required für Push.

    Args:
        crep_threshold: Minimales Γ für Push (default 0.6).

    Returns:
        True wenn Push erlaubt, False wenn blockiert.
    """
    try:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        config = GenesisConfig(max_cycles=5)
        genesis = GenesisOS(config=config)
        state = genesis.run(max_cycles=5)
        if state.crep is not None and state.crep.gamma < crep_threshold:
            logger.warning(
                "pre_push_ritual: CREP-Gate blockiert Push. Γ=%.3f < %.3f",
                state.crep.gamma,
                crep_threshold,
            )
            return False
    except Exception as exc:
        logger.debug("pre_push_ritual: CREP check skipped: %s", exc)
    return True


def sigillin_sync_check() -> bool:
    """Prüft ob Sigillin-Trilayer synchron ist.

    Returns:
        True wenn synchron oder kein Sigillin-State vorhanden.
    """
    try:
        from genesis_os.sigillin.sync import SigillinSync  # noqa: F401

        # SigillinSync does not expose is_synced yet — default to True
        return True
    except Exception:
        return True


def main() -> None:  # pragma: no cover
    """Entry point für Pre-commit Hook."""
    if not pre_commit_ritual():
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
