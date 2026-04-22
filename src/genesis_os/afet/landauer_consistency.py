"""Landauer-Konsistenz-Check für AFET.

Stellt sicher, dass die AFET-Entropieproduktionsrate σ_0 physikalisch
konsistent mit der Landauer-Schranke aus unified-mandala ist.

Physikalische Herleitung:
    Landauer: E_bit = k_B · T · ln2      [Energie pro Bit-Löschung]
    AFET: σ_s = σ_0 · (1 + κ·Γ)         [Entropieproduktionsrate, J/(K·m³·s)]

    Konsistenz-Bedingung:
        σ_0 ≥ k_B · T · ln2 / (Δt · V_system)

    mit Δt = Integrationsschritt, V_system = Systemvolumen (normiert = 1 m³)
"""

from __future__ import annotations

import math
import warnings

K_BOLTZMANN: float = 1.380649e-23
ROOM_TEMP_K: float = 300.0


def landauer_minimum_entropy(
    temperature_K: float = ROOM_TEMP_K,
    n_bits: float = 1.0,
    dt: float = 1.0,
    volume: float = 1.0,
) -> float:
    """Minimale AFET σ_0 aus der Landauer-Schranke.

    Args:
        temperature_K: Temperatur in Kelvin.
        n_bits: Anzahl der gelöschten Bits pro Schritt.
        dt: Integrationsschritt (s).
        volume: Systemvolumen (m³).

    Returns:
        Minimale physikalisch erlaubte Entropieproduktionsrate [J/(K·m³·s)].
    """
    e_bit = K_BOLTZMANN * temperature_K * math.log(2)
    return (e_bit * n_bits) / (dt * volume)


def validate_landauer_consistency(
    sigma_0: float,
    temperature_K: float = ROOM_TEMP_K,
    dt: float = 1.0,
    volume: float = 1.0,
    warn_only: bool = True,
) -> tuple[bool, float]:
    """Prüft ob σ_0 ≥ Landauer-Minimum.

    Args:
        sigma_0: AFET Entropieproduktionsrate σ_0 [J/(K·m³·s)].
        temperature_K: Systemtemperatur (K).
        dt: Integrationsschritt (s).
        volume: Systemvolumen (m³).
        warn_only: Wenn True, wird nur eine Warnung ausgegeben statt Exception.

    Returns:
        Tuple (is_consistent, landauer_minimum).

    Raises:
        ValueError: Wenn nicht konsistent und ``warn_only=False``.
    """
    minimum = landauer_minimum_entropy(temperature_K, dt=dt, volume=volume)
    consistent = sigma_0 >= minimum
    if not consistent:
        msg = (
            f"AFET σ_0={sigma_0:.2e} < Landauer minimum {minimum:.2e}. "
            f"Physikalisch inkonsistent bei T={temperature_K}K."
        )
        if warn_only:
            warnings.warn(msg, stacklevel=2)
        else:
            raise ValueError(msg)
    return consistent, minimum
