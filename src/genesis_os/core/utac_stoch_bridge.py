"""UTACStochBridge — Mathematische Brücke zwischen UTAC-ODE und SDE-Collapse.

Das UTAC-Logistic-ODE (genesis-os) ist der Erwartungswert des vollständigen
stochastischen Differentialgleichungssystems (SDE) aus unified-mandala:

Deterministisch (genesis-os):
    dH/dt = r · H · (1 - H/K) · tanh(σ · Γ)

Stochastisch (unified-mandala CollapseDetector):
    dX = r · X · (1 - X/K) · tanh(σ · Γ) · dt + η · √X · dW_t

Verbindung (Itô-Kalkül):
    E[dX_t] = dH/dt · dt   (ODE = Erwartungswert des SDE)
    Var[dX_t] = η² · X · dt

Physikalische Interpretation:
    η = Rausch-Amplitude  ↔  σ_Φ = 1/16  (Frame Principle Stabilitätskonstante)
    η_optimal = √(σ_Φ) ≈ 0.25  für metastabile Selbst-Referenz
"""

from __future__ import annotations

import numpy as np

SIGMA_PHI: float = 1.0 / 16.0


def compute_noise_amplitude(sigma_phi: float = SIGMA_PHI) -> float:
    """Optimale Rausch-Amplitude η = √(σ_Φ) aus dem Frame Principle."""
    return float(np.sqrt(sigma_phi))


def sde_drift(x: float, r: float, K: float, sigma: float, gamma: float) -> float:
    """Drift-Term f(X) des UTAC-SDE — identisch mit dem UTAC-ODE."""
    return r * x * (1.0 - x / K) * float(np.tanh(sigma * gamma))


def sde_diffusion(x: float, eta: float | None = None) -> float:
    """Diffusions-Term g(X) = η · √X des UTAC-SDE."""
    if eta is None:
        eta = compute_noise_amplitude()
    return eta * float(np.sqrt(max(x, 0.0)))


def euler_maruyama_step(
    x: float,
    r: float,
    K: float,
    sigma: float,
    gamma: float,
    dt: float = 0.01,
    eta: float | None = None,
    rng: np.random.Generator | None = None,
) -> float:
    """Einzelner Euler-Maruyama Schritt des UTAC-SDE.

    X_{t+dt} = X_t + f(X_t)·dt + g(X_t)·dW   mit  dW ~ N(0, √dt)

    Args:
        x: Aktueller Zustand X_t.
        r: Wachstumsrate.
        K: Kapazitätsgrenze.
        sigma: Kopplungsstärke.
        gamma: CREP-Γ.
        dt: Integrationsschritt.
        eta: Rausch-Amplitude (Default: √σ_Φ).
        rng: NumPy Random Generator für Reproduzierbarkeit.

    Returns:
        Neuer Zustand X_{t+dt} ≥ 0.
    """
    if eta is None:
        eta = compute_noise_amplitude()
    _rng = rng if rng is not None else np.random.default_rng()
    drift = sde_drift(x, r, K, sigma, gamma)
    diffusion = sde_diffusion(x, eta)
    dW = float(_rng.normal(0.0, np.sqrt(dt)))
    return max(x + drift * dt + diffusion * dW, 0.0)


def simulate_sde_trajectory(
    x0: float,
    r: float,
    K: float,
    sigma: float,
    gamma: float,
    n_steps: int = 100,
    dt: float = 0.01,
    eta: float | None = None,
    seed: int | None = None,
) -> list[float]:
    """Simuliert eine vollständige SDE-Trajektorie via Euler-Maruyama.

    Args:
        x0: Anfangszustand.
        n_steps: Anzahl Zeitschritte.
        seed: Random seed für Reproduzierbarkeit.

    Returns:
        Liste der Zustandswerte [X_0, X_1, ..., X_n].
    """
    rng = np.random.default_rng(seed)
    trajectory = [x0]
    x = x0
    for _ in range(n_steps):
        x = euler_maruyama_step(x, r, K, sigma, gamma, dt=dt, eta=eta, rng=rng)
        trajectory.append(x)
    return trajectory


def ode_trajectory(
    x0: float,
    r: float,
    K: float,
    sigma: float,
    gamma: float,
    n_steps: int = 100,
    dt: float = 0.01,
) -> list[float]:
    """Deterministisches UTAC-ODE — Referenztrajektorie für SDE-Erwartungswert-Test.

    dH/dt = r · H · (1 - H/K) · tanh(σ · Γ)  via Euler-Methode.
    """
    trajectory = [x0]
    x = x0
    for _ in range(n_steps):
        x = max(x + sde_drift(x, r, K, sigma, gamma) * dt, 0.0)
        trajectory.append(x)
    return trajectory
