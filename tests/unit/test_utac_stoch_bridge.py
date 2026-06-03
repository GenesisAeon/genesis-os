"""Tests für genesis_os.core.utac_stoch_bridge — Phase A."""

from __future__ import annotations

import math

import numpy as np
import pytest

from genesis_os.core.crep import CREPEvaluator, CREPScore
from genesis_os.core.utac_stoch_bridge import (
    SIGMA_PHI,
    compute_noise_amplitude,
    euler_maruyama_step,
    ode_trajectory,
    sde_diffusion,
    sde_drift,
    simulate_sde_trajectory,
)


class TestSigmaPhi:
    def test_sigma_phi_value(self) -> None:
        assert SIGMA_PHI == pytest.approx(1.0 / 16.0)

    def test_noise_amplitude(self) -> None:
        eta = compute_noise_amplitude()
        assert eta == pytest.approx(math.sqrt(1.0 / 16.0), rel=1e-6)
        assert eta == pytest.approx(0.25, rel=1e-6)

    def test_noise_amplitude_custom(self) -> None:
        eta = compute_noise_amplitude(sigma_phi=0.04)
        assert eta == pytest.approx(0.2, rel=1e-6)


class TestCREPCanonicalMode:
    def test_canonical_crep_geometric_mean(self) -> None:
        score = CREPScore(coherence=0.8, resonance=0.7, emergence=0.9, poetics=0.6)
        expected = (0.8 * 0.7 * 0.9 * 0.6) ** 0.25
        assert score.gamma == pytest.approx(expected, rel=1e-6)
        # (0.3024)^0.25 ≈ 0.7416
        assert score.gamma == pytest.approx(0.7416, abs=1e-3)

    def test_canonical_vs_legacy_differ(self) -> None:
        score = CREPScore(coherence=0.8, resonance=0.7, emergence=0.9, poetics=0.6)
        assert score.gamma != pytest.approx(score.gamma_legacy, rel=1e-3)

    def test_canonical_all_ones(self) -> None:
        score = CREPScore(coherence=1.0, resonance=1.0, emergence=1.0, poetics=1.0)
        assert score.gamma == pytest.approx(1.0)

    def test_canonical_all_zeros(self) -> None:
        score = CREPScore(coherence=0.0, resonance=0.0, emergence=0.0, poetics=0.0)
        assert score.gamma == pytest.approx(0.0)

    def test_evaluator_mode_canonical(self) -> None:
        evaluator = CREPEvaluator()
        state = {"coherence": 0.8, "resonance": 0.7, "emergence": 0.9, "poetics": 0.6}
        score = evaluator.evaluate(state, mode="canonical")
        assert score.gamma == pytest.approx(0.7416, abs=1e-3)
        assert evaluator.last_mode == "canonical"

    def test_evaluator_mode_legacy_default(self) -> None:
        evaluator = CREPEvaluator()
        state = {"coherence": 0.8, "resonance": 0.7, "emergence": 0.9, "poetics": 0.6}
        score = evaluator.evaluate(state)
        assert evaluator.last_mode == "legacy"
        assert score.gamma > 0.0

    def test_legacy_crep_backward_compat(self) -> None:
        score = CREPScore(coherence=0.8, resonance=0.7, emergence=0.9, poetics=0.6)
        sigma_c = 0.3
        expected = (
            (0.8 * 0.7 + 0.9 * 0.6) / 2.0
        ) * math.exp(-((1.0 - 0.8) ** 2) / (2.0 * sigma_c**2))
        assert score.gamma_legacy == pytest.approx(expected, rel=1e-6)


class TestSDEDrift:
    def test_drift_positive(self) -> None:
        d = sde_drift(0.5, r=0.12, K=1.0, sigma=2.2, gamma=0.7)
        assert d > 0.0

    def test_drift_at_capacity(self) -> None:
        d = sde_drift(1.0, r=0.12, K=1.0, sigma=2.2, gamma=0.7)
        assert d == pytest.approx(0.0, abs=1e-10)

    def test_drift_zero_gamma(self) -> None:
        d = sde_drift(0.5, r=0.12, K=1.0, sigma=2.2, gamma=0.0)
        assert d == pytest.approx(0.0, abs=1e-10)

    def test_diffusion_positive(self) -> None:
        g = sde_diffusion(0.5, eta=0.25)
        assert g > 0.0

    def test_diffusion_zero_state(self) -> None:
        g = sde_diffusion(0.0, eta=0.25)
        assert g == pytest.approx(0.0)


class TestEulerMaruyama:
    def test_step_returns_nonnegative(self) -> None:
        for _ in range(50):
            x = euler_maruyama_step(0.1, r=0.12, K=1.0, sigma=2.2, gamma=0.7)
            assert x >= 0.0

    def test_euler_maruyama_convergence(self) -> None:
        """10.000 Euler-Maruyama Pfade konvergieren zur ODE-Trajektorie im Mittel."""
        x0, r, K, sigma, gamma = 0.3, 0.12, 1.0, 2.2, 0.7
        n_steps, dt, n_paths = 100, 0.01, 10_000

        ode_traj = ode_trajectory(x0, r, K, sigma, gamma, n_steps=n_steps, dt=dt)

        rng = np.random.default_rng(42)
        sde_finals = []
        for _ in range(n_paths):
            x = x0
            for _ in range(n_steps):
                x = euler_maruyama_step(x, r, K, sigma, gamma, dt=dt, rng=rng)
            sde_finals.append(x)

        sde_mean = float(np.mean(sde_finals))
        ode_final = ode_traj[-1]

        rel_error = abs(sde_mean - ode_final) / max(abs(ode_final), 1e-12)
        assert rel_error < 0.05, f"SDE mean {sde_mean:.4f} vs ODE {ode_final:.4f}, rel_err={rel_error:.3f}"

    def test_simulate_trajectory_length(self) -> None:
        traj = simulate_sde_trajectory(0.3, r=0.12, K=1.0, sigma=2.2, gamma=0.7, n_steps=50, seed=0)
        assert len(traj) == 51  # x0 + 50 steps

    def test_simulate_trajectory_reproducible(self) -> None:
        kw = dict(x0=0.3, r=0.12, K=1.0, sigma=2.2, gamma=0.7, n_steps=10, seed=99)
        traj1 = simulate_sde_trajectory(**kw)
        traj2 = simulate_sde_trajectory(**kw)
        assert traj1 == traj2
