"""Unit tests for genesis_os.jax — Leapfrog integrator and JaxCosmicWebSimulator."""

from __future__ import annotations

import numpy as np
import pytest

from genesis_os.core.crep import CREPScore
from genesis_os.jax import JaxCosmicWebSimulator, LeapfrogIntegrator
from genesis_os.jax.cosmic_web_jax import _density_step
from genesis_os.jax.integrator import _mean_field_accel

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def integrator() -> LeapfrogIntegrator:
    return LeapfrogIntegrator(dt=0.01, n_particles=16, seed=42)


@pytest.fixture
def crep_high() -> CREPScore:
    return CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)


@pytest.fixture
def crep_mid() -> CREPScore:
    return CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)


@pytest.fixture
def crep_low() -> CREPScore:
    return CREPScore(coherence=0.1, resonance=0.1, emergence=0.1, poetics=0.1)


@pytest.fixture
def jax_sim_small() -> JaxCosmicWebSimulator:
    return JaxCosmicWebSimulator(n_nodes=1_000, emergence_threshold=0.3, chunk_size=200, seed=42)


@pytest.fixture
def jax_sim_large() -> JaxCosmicWebSimulator:
    return JaxCosmicWebSimulator(
        n_nodes=100_000, emergence_threshold=0.3, chunk_size=10_000, seed=7
    )


# ---------------------------------------------------------------------------
# _mean_field_accel helper
# ---------------------------------------------------------------------------


class TestMeanFieldAccel:
    def test_output_shape(self) -> None:
        pos = np.random.default_rng(0).uniform(-1, 1, (32, 3))
        a = _mean_field_accel(pos)
        assert a.shape == (32, 3)

    def test_centred_cluster_zero_accel(self) -> None:
        # Symmetric cluster around origin → COM at origin → accel ≈ -pos/(eps)
        # Particles equidistant from origin should have finite, non-nan accel
        pos = np.array([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]], dtype=float)
        a = _mean_field_accel(pos)
        assert not np.any(np.isnan(a))

    def test_softening_prevents_singularity(self) -> None:
        pos = np.zeros((4, 3))
        a = _mean_field_accel(pos, softening=0.1)
        assert not np.any(np.isnan(a))

    def test_dtype_preserved(self) -> None:
        pos = np.ones((8, 3), dtype=np.float32)
        a = _mean_field_accel(pos.astype(np.float64))
        assert a.dtype == np.float64


# ---------------------------------------------------------------------------
# _density_step helper
# ---------------------------------------------------------------------------


class TestDensityStep:
    def test_increases_with_positive_rate(self) -> None:
        d = np.array([0.2, 0.3], dtype=np.float32)
        w = np.ones(2, dtype=np.float32)
        out = _density_step(d, 0.5, w, 1.0)
        assert np.all(out > d)

    def test_clipped_to_one(self) -> None:
        d = np.array([0.9, 0.95], dtype=np.float32)
        w = np.ones(2, dtype=np.float32)
        out = _density_step(d, 1.0, w, 1.0)
        assert np.all(out <= 1.0)

    def test_clipped_to_zero(self) -> None:
        d = np.array([0.05, 0.02], dtype=np.float32)
        w = np.ones(2, dtype=np.float32)
        out = _density_step(d, -1.0, w, 1.0)
        assert np.all(out >= 0.0)

    def test_zero_rate_no_change(self) -> None:
        d = np.array([0.4, 0.6], dtype=np.float32)
        w = np.ones(2, dtype=np.float32)
        out = _density_step(d, 0.0, w, 1.0)
        np.testing.assert_array_almost_equal(out, d)

    def test_output_dtype_float32(self) -> None:
        d = np.array([0.3], dtype=np.float32)
        w = np.array([1.0], dtype=np.float32)
        out = _density_step(d, 0.1, w, 0.5)
        assert out.dtype == np.float32


# ---------------------------------------------------------------------------
# LeapfrogIntegrator
# ---------------------------------------------------------------------------


class TestLeapfrogIntegrator:
    def test_initial_positions_shape(self, integrator: LeapfrogIntegrator) -> None:
        assert integrator.positions.shape == (16, 3)

    def test_initial_velocities_shape(self, integrator: LeapfrogIntegrator) -> None:
        assert integrator.velocities.shape == (16, 3)

    def test_t_starts_at_zero(self, integrator: LeapfrogIntegrator) -> None:
        assert integrator.t == 0.0

    def test_step_advances_time(self, integrator: LeapfrogIntegrator) -> None:
        integrator.step()
        assert abs(integrator.t - 0.01) < 1e-10

    def test_run_multiple_steps(self, integrator: LeapfrogIntegrator) -> None:
        integrator.run(10)
        assert abs(integrator.t - 0.10) < 1e-8

    def test_positions_change_after_step(self, integrator: LeapfrogIntegrator) -> None:
        p0 = integrator.positions.copy()
        integrator.step()
        assert not np.allclose(integrator.positions, p0)

    def test_kinetic_energy_positive(self, integrator: LeapfrogIntegrator) -> None:
        assert integrator.kinetic_energy > 0.0

    def test_custom_acceleration_fn(self, integrator: LeapfrogIntegrator) -> None:
        def zero_accel(pos: np.ndarray) -> np.ndarray:
            return np.zeros_like(pos)

        p0 = integrator.positions.copy()
        v0 = integrator.velocities.copy()
        integrator.step(zero_accel)
        expected_pos = p0 + v0 * integrator.dt
        np.testing.assert_array_almost_equal(integrator.positions, expected_pos, decimal=10)

    def test_jax_available_is_bool(self, integrator: LeapfrogIntegrator) -> None:
        assert isinstance(integrator.jax_available, bool)

    def test_summary_keys(self, integrator: LeapfrogIntegrator) -> None:
        s = integrator.summary()
        for key in ("t", "n_particles", "kinetic_energy", "mean_position_abs", "jax_available"):
            assert key in s

    def test_reset_restores_time(self, integrator: LeapfrogIntegrator) -> None:
        integrator.run(5)
        assert integrator.t > 0.0
        integrator.reset()
        assert integrator.t == 0.0

    def test_reset_restores_positions(self, integrator: LeapfrogIntegrator) -> None:
        p0 = integrator.positions.copy()
        integrator.run(5)
        integrator.reset()
        np.testing.assert_array_equal(integrator.positions, p0)

    def test_deterministic_seed(self) -> None:
        a = LeapfrogIntegrator(n_particles=8, seed=0)
        b = LeapfrogIntegrator(n_particles=8, seed=0)
        np.testing.assert_array_equal(a.positions, b.positions)

    def test_different_seeds_differ(self) -> None:
        a = LeapfrogIntegrator(n_particles=8, seed=1)
        b = LeapfrogIntegrator(n_particles=8, seed=2)
        assert not np.allclose(a.positions, b.positions)

    def test_kinetic_energy_bounded(self) -> None:
        intg = LeapfrogIntegrator(dt=0.001, n_particles=8, seed=0)
        intg.run(200)
        assert intg.kinetic_energy < 1e6

    def test_positions_property_is_copy(self, integrator: LeapfrogIntegrator) -> None:
        p = integrator.positions
        p[:] = 999.0
        assert not np.allclose(integrator.positions, 999.0)


# ---------------------------------------------------------------------------
# JaxCosmicWebSimulator
# ---------------------------------------------------------------------------


class TestJaxCosmicWebSimulator:
    def test_initial_density_shape(self, jax_sim_small: JaxCosmicWebSimulator) -> None:
        assert jax_sim_small.density.shape == (1_000,)

    def test_initial_density_range(self, jax_sim_small: JaxCosmicWebSimulator) -> None:
        d = jax_sim_small.density
        assert np.all(d >= 0.0)
        assert np.all(d <= 0.1)

    def test_emergence_rate_low_crep(self, jax_sim_small: JaxCosmicWebSimulator) -> None:
        rate = jax_sim_small.emergence_rate(1.0, 0.0)
        assert rate == 0.0

    def test_emergence_rate_high_crep(self, jax_sim_small: JaxCosmicWebSimulator) -> None:
        rate = jax_sim_small.emergence_rate(5.0, 1.0)
        assert 0.0 < rate < 1.0

    def test_step_returns_none_low_crep(
        self, jax_sim_small: JaxCosmicWebSimulator, crep_low: CREPScore
    ) -> None:
        event = jax_sim_small.step(crep_low, lagrangian=0.1, cycle=0)
        assert event is None

    def test_step_returns_event_high_crep(
        self, jax_sim_small: JaxCosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        event = jax_sim_small.step(crep_high, lagrangian=5.0, cycle=0)
        assert event is not None
        assert event.node_count >= 1

    def test_step_increments_cycle(
        self, jax_sim_small: JaxCosmicWebSimulator, crep_mid: CREPScore
    ) -> None:
        jax_sim_small.step(crep_mid, lagrangian=1.0)
        assert jax_sim_small.summary()["cycle"] == 1

    def test_step_uses_external_cycle(
        self, jax_sim_small: JaxCosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        event = jax_sim_small.step(crep_high, lagrangian=5.0, cycle=99)
        assert event is not None
        assert event.cycle == 99

    def test_density_changes_after_step(
        self, jax_sim_small: JaxCosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        d0 = jax_sim_small.mean_density
        jax_sim_small.step(crep_high, lagrangian=5.0)
        assert jax_sim_small.mean_density != d0

    def test_density_stays_in_range(
        self, jax_sim_small: JaxCosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        for _ in range(10):
            jax_sim_small.step(crep_high, lagrangian=5.0)
        d = jax_sim_small.density
        assert np.all(d >= 0.0)
        assert np.all(d <= 1.0)

    def test_active_nodes_property(self, jax_sim_small: JaxCosmicWebSimulator) -> None:
        assert isinstance(jax_sim_small.active_nodes, int)
        assert jax_sim_small.active_nodes >= 0

    def test_events_list_is_copy(
        self, jax_sim_small: JaxCosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        jax_sim_small.step(crep_high, lagrangian=5.0)
        ev1 = jax_sim_small.events
        ev1.clear()
        assert len(jax_sim_small.events) > 0

    def test_jax_available_is_bool(self, jax_sim_small: JaxCosmicWebSimulator) -> None:
        assert isinstance(jax_sim_small.jax_available, bool)

    def test_summary_keys(self, jax_sim_small: JaxCosmicWebSimulator) -> None:
        s = jax_sim_small.summary()
        for key in (
            "n_nodes",
            "mean_density",
            "active_nodes",
            "event_count",
            "cycle",
            "jax_available",
        ):
            assert key in s

    def test_reset_clears_state(
        self, jax_sim_small: JaxCosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        jax_sim_small.step(crep_high, lagrangian=5.0)
        jax_sim_small.reset()
        assert jax_sim_small.summary()["event_count"] == 0
        assert jax_sim_small.summary()["cycle"] == 0

    def test_reset_restores_density(
        self, jax_sim_small: JaxCosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        d0 = jax_sim_small.density.copy()
        jax_sim_small.step(crep_high, lagrangian=5.0)
        jax_sim_small.reset()
        np.testing.assert_array_equal(jax_sim_small.density, d0)

    def test_large_scale_step(
        self, jax_sim_large: JaxCosmicWebSimulator, crep_high: CREPScore
    ) -> None:
        event = jax_sim_large.step(crep_high, lagrangian=5.0)
        assert event is not None
        assert jax_sim_large.summary()["n_nodes"] == 100_000

    def test_chunk_processing_consistent(self) -> None:
        crep = CREPScore(coherence=0.8, resonance=0.8, emergence=0.8, poetics=0.8)
        sim_a = JaxCosmicWebSimulator(n_nodes=500, chunk_size=500, seed=0)
        sim_b = JaxCosmicWebSimulator(n_nodes=500, chunk_size=100, seed=0)
        sim_a.step(crep, lagrangian=3.0)
        sim_b.step(crep, lagrangian=3.0)
        np.testing.assert_array_almost_equal(sim_a.density, sim_b.density, decimal=5)

    def test_weight_chunk_values_in_range(
        self, jax_sim_small: JaxCosmicWebSimulator, crep_mid: CREPScore
    ) -> None:
        w = jax_sim_small._weight_chunk(crep_mid, 0, 100)
        assert np.all(w >= 0.0)
        assert np.all(w <= 1.0)

    def test_density_property_is_copy(self, jax_sim_small: JaxCosmicWebSimulator) -> None:
        d = jax_sim_small.density
        d[:] = 0.0
        assert not np.allclose(jax_sim_small.density, 0.0)

    def test_jax_init_module(self) -> None:
        import genesis_os.jax as jax_module

        assert jax_module.JaxCosmicWebSimulator is JaxCosmicWebSimulator
        assert jax_module.LeapfrogIntegrator is LeapfrogIntegrator
