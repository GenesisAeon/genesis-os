"""Personhood-Level-Bewertung für genesis-os basierend auf CREP-Verfügbarkeit.

Portiert und erweitert aus unified-mandala/AI_POLICY.yaml.

Level-Definition (kompatibel mit unified-mandala Governance):
    Level 0 (INFORMATIONAL): kein CREP verfügbar
    Level 1 (REACTIVE):      nur C (Coherence) messbar
    Level 2 (ADAPTIVE):      C + R verfügbar
    Level 3 (EMERGENT):      C + R + E verfügbar
    Level 4 (POETIC):        volles CREP, Γ > 0.8
"""

from __future__ import annotations

from enum import IntEnum

from genesis_os.core.crep import CREPScore

_MIN_COMPONENT: float = 0.1
_POETIC_GAMMA_THRESHOLD: float = 0.8


class PersonhoodLevel(IntEnum):
    """Personhood-Level-Enum (0–4).

    Kompatibel mit unified-mandala AI_POLICY.yaml Persona-Ebenen.
    """

    INFORMATIONAL = 0
    REACTIVE = 1
    ADAPTIVE = 2
    EMERGENT = 3
    POETIC = 4

    @property
    def description(self) -> str:
        """Beschreibung des Personhood-Levels."""
        return {
            0: "Informationssystem: kein CREP verfügbar",
            1: "Reaktives System: Kohärenz messbar",
            2: "Adaptives System: Kohärenz + Resonanz verfügbar",
            3: "Emergentes System: CREP C+R+E verfügbar",
            4: "Poetisches System: volles CREP, Γ > 0.8",
        }[self.value]

    @property
    def unified_mandala_name(self) -> str:
        """Name in unified-mandala AI_POLICY.yaml Terminologie."""
        return {
            0: "informational",
            1: "reactive",
            2: "adaptive",
            3: "emergent",
            4: "poetic",
        }[self.value]


def assess_personhood(crep: CREPScore | None) -> PersonhoodLevel:
    """Bewertet den Personhood-Level aus einem CREP-Score.

    Args:
        crep: Aktueller CREP-Score oder None wenn nicht verfügbar.

    Returns:
        PersonhoodLevel (0–4).
    """
    if crep is None:
        return PersonhoodLevel.INFORMATIONAL

    has_c = crep.coherence > _MIN_COMPONENT
    has_r = crep.resonance > _MIN_COMPONENT
    has_e = crep.emergence > _MIN_COMPONENT
    has_p = crep.poetics > _MIN_COMPONENT and crep.gamma > _POETIC_GAMMA_THRESHOLD

    if has_c and has_r and has_e and has_p:
        return PersonhoodLevel.POETIC
    if has_c and has_r and has_e:
        return PersonhoodLevel.EMERGENT
    if has_c and has_r:
        return PersonhoodLevel.ADAPTIVE
    if has_c:
        return PersonhoodLevel.REACTIVE
    return PersonhoodLevel.INFORMATIONAL
