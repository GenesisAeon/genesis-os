"""Tension-Metrik aus unified-mandala v0.3.1 (portiert für genesis-os).

Physikalische Interpretation:
    Tension(t) = Γ_Klima · Q_KI(t) / (V_Eis(t) + ε)

    Γ_Klima: CREP-Gamma aus klimatischen ERA5-Feldern
    Q_KI:    KI-Energieverbrauch (GW) — Proxy für anthropogenen Druck
    V_Eis:   Arktisches Eisvolumen (km³)
    ε:       Regularisierung (verhindert Division durch Null)

    Albedo-Verlust:
    albedo_loss(t) = albedo_factor / (V_Eis(t) + ε)
    steigt stark an wenn Eisvolumen → 0 (Ice-Albedo-Feedback)

Physikalische Konsistenz mit genesis-os UTAC:
    Bei V_Eis → 0: Tension → ∞, CREP-E (Emergence) → max,
    was im Mirror-Machine einen Phase-Transition-Trigger auslöst.

Regenerativer Dämpfer (87.2×):
    87.2 — empirischer Dämpfungsfaktor aus unified-mandala v0.3.1
    Portiert als dimensionslose Konstante für neuromorphic noise damping.
"""

from __future__ import annotations

CRITICAL_TENSION_THRESHOLD: float = 5.0

# 87.2 — neuromorphic noise damping constant (unified-mandala v0.3.1)
REGENERATIVE_DAMPING_FACTOR: float = 87.2


def compute_tension_metric(
    gamma_klima: float,
    q_ki: float,
    v_ice: float,
    epsilon: float = 1e-6,
) -> float:
    """Berechnet die Tension-Metrik Tension(t) = Γ_Klima · Q_KI / (V_Eis + ε).

    Args:
        gamma_klima: CREP-Gamma aus ERA5-Klimafeldern.
        q_ki: KI-Energieverbrauch [GW].
        v_ice: Arktisches Eisvolumen [km³].
        epsilon: Regularisierungsterm.

    Returns:
        Tension-Wert (dimensionslos, > 0).
    """
    return gamma_klima * q_ki / (v_ice + epsilon)


def albedo_loss(
    albedo_factor: float,
    v_ice: float,
    epsilon: float = 1e-6,
) -> float:
    """Ice-Albedo-Feedback: Albedo-Verlust steigt stark wenn Eis → 0.

    Args:
        albedo_factor: Skalierungsfaktor für Albedo-Verlust.
        v_ice: Arktisches Eisvolumen [km³].
        epsilon: Regularisierungsterm.

    Returns:
        Albedo-Verlust (steigt gegen ∞ wenn v_ice → 0).
    """
    return albedo_factor / (v_ice + epsilon)


def regenerative_noise_damping(
    eta: float,
    regenerative: bool = False,
    damping_factor: float = REGENERATIVE_DAMPING_FACTOR,
) -> float:
    """Wendet 87.2× neuromorphisches Rauschen-Dämpfung an.

    Im regenerativen Modus wird die Rausch-Amplitude um den Faktor 87.2
    reduziert — analog zu unified-mandala CollapseDetectorConfig(regenerative=True).

    Args:
        eta: Ursprüngliche Rausch-Amplitude.
        regenerative: Ob regenerativer Modus aktiv ist.
        damping_factor: Dämpfungsfaktor (Default: α^{-1}/Φ² ≈ 87.2).

    Returns:
        Gedämpfte Rausch-Amplitude.
    """
    if regenerative:
        return eta / damping_factor
    return eta
