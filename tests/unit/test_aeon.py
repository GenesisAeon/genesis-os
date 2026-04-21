"""Tests for genesis_os.aeon — Nullkern, AeonShell, SemanticAgent, LanternNet."""

from __future__ import annotations

import numpy as np
import pytest

from genesis_os.aeon import AeonShell, LanternNet, Nullkern, SemanticAgent
from genesis_os.aeon.agents import AgentCollective, AgentState, CollectiveField
from genesis_os.aeon.lantern_net import (
    CREP_LANTERN_MAP,
    LANTERN_DEFS,
    LANTERN_EM_FREQ_MHZ,
    LANTERN_IMPEDANCE_OHM,
    TARGET_COHERENCE,
)
from genesis_os.aeon.nullkern import BardoPhase, NullkernState, _BARDO_SEQUENCE
from genesis_os.aeon.shell import MAX_RECURSION_DEPTH, COHERENCE_EXTENSION_THRESHOLD


# ---------------------------------------------------------------------------
# Nullkern tests
# ---------------------------------------------------------------------------


class TestNullkern:
    def setup_method(self) -> None:
        self.kern = Nullkern(beta_utac=37.6, theta=0.5, humility_h=0.1)

    def test_activate_returns_state(self) -> None:
        state = self.kern.activate(0.6)
        assert isinstance(state, NullkernState)

    def test_activation_range(self) -> None:
        for R in [0.0, 0.3, 0.5, 0.7, 1.0]:
            state = self.kern.activate(R)
            assert 0.0 < state.activation < 1.0

    def test_humility_protocol_reduces_overconfidence(self) -> None:
        # Activation > 0.5 should be pulled toward 0.5
        state = self.kern.activate(0.9)  # high R → high activation
        if state.activation > 0.5:
            assert state.humility_adjusted < state.activation
        elif state.activation < 0.5:
            assert state.humility_adjusted > state.activation

    def test_humility_protocol_formula(self) -> None:
        a = 0.8
        h = 0.1
        expected = a + h * (0.5 - a)
        result = Nullkern.apply_humility(a, h)
        assert result == pytest.approx(expected)

    def test_humility_at_half_unchanged(self) -> None:
        result = Nullkern.apply_humility(0.5, h=0.1)
        assert result == pytest.approx(0.5)

    def test_cycle_increments(self) -> None:
        self.kern.activate(0.5)
        self.kern.activate(0.6)
        assert self.kern.cycle == 2

    def test_bardo_phase_initial(self) -> None:
        assert self.kern.bardo_phase == BardoPhase.GROUND

    def test_advance_bardo_changes_phase(self) -> None:
        phase1 = self.kern.bardo_phase
        new_phase = self.kern.advance_bardo()
        assert new_phase != phase1

    def test_bardo_wraps_around(self) -> None:
        for _ in range(len(_BARDO_SEQUENCE)):
            self.kern.advance_bardo()
        assert self.kern.bardo_phase == BardoPhase.GROUND

    def test_history_length(self) -> None:
        for i in range(5):
            self.kern.activate(float(i) / 5)
        assert len(self.kern.history) == 5

    def test_inject_state_metadata(self) -> None:
        self.kern.inject_state({"mirror_signal": 0.7, "phase": "active"})
        mirror_state = self.kern.get_state_for_mirror()
        assert mirror_state["mirror_signal"] == pytest.approx(0.7)

    def test_get_state_for_mirror_empty_history(self) -> None:
        state = self.kern.get_state_for_mirror()
        assert state["activation"] == pytest.approx(0.5)

    def test_get_state_for_mirror_with_history(self) -> None:
        self.kern.activate(0.7)
        state = self.kern.get_state_for_mirror()
        assert "bardo_phase" in state
        assert "cycle" in state

    def test_reset_clears_state(self) -> None:
        self.kern.activate(0.5)
        self.kern.advance_bardo()
        self.kern.reset()
        assert self.kern.cycle == 0
        assert self.kern.bardo_phase == BardoPhase.GROUND
        assert len(self.kern.history) == 0

    def test_clipped_R_above_one(self) -> None:
        state = self.kern.activate(1.5)
        assert state.R == pytest.approx(1.0)

    def test_clipped_R_below_zero(self) -> None:
        state = self.kern.activate(-0.3)
        assert state.R == pytest.approx(0.0)

    def test_bardo_sequence_has_all_phases(self) -> None:
        assert len(_BARDO_SEQUENCE) == len(BardoPhase)


# ---------------------------------------------------------------------------
# AeonShell tests
# ---------------------------------------------------------------------------


class TestAeonShell:
    def setup_method(self) -> None:
        self.shell = AeonShell(zeta=1.0, spectral_mask_fraction=0.5, max_depth=8)

    def test_zeta_normalize_preserves_length(self) -> None:
        ts = np.random.default_rng(42).normal(0, 1, 50)
        result = self.shell.zeta_normalize(ts)
        assert len(result) == len(ts)

    def test_zeta_normalize_single_element(self) -> None:
        ts = np.array([5.0])
        result = self.shell.zeta_normalize(ts)
        assert result[0] == pytest.approx(5.0)

    def test_zeta_normalize_lipschitz_bound(self) -> None:
        ts = np.array([0.0, 10.0, 20.0, 30.0])
        result = self.shell.zeta_normalize(ts)
        grads = np.diff(result)
        assert np.all(np.abs(grads) <= self.shell.zeta + 1e-9)

    def test_zeta_normalize_zero_gradient(self) -> None:
        ts = np.ones(10)
        result = self.shell.zeta_normalize(ts)
        np.testing.assert_array_almost_equal(result, np.ones(10))

    def test_extract_interference_shape(self) -> None:
        ts = np.random.default_rng(0).normal(0, 1, 64)
        result = self.shell.extract_interference(ts)
        assert result.shape == ts.shape

    def test_extract_interference_short_signal(self) -> None:
        ts = np.array([1.0, 2.0])
        result = self.shell.extract_interference(ts)
        np.testing.assert_array_almost_equal(result, np.zeros(2))

    def test_measure_coherence_range(self) -> None:
        rng = np.random.default_rng(42)
        s = rng.normal(0, 1, 50)
        c = rng.normal(0, 1, 50)
        coh = self.shell.measure_coherence(s, c)
        assert 0.0 <= coh <= 1.0

    def test_measure_coherence_identical_signals(self) -> None:
        s = np.array([1.0, 2.0, 3.0, 4.0])
        coh = self.shell.measure_coherence(s, s)
        assert coh == pytest.approx(1.0, abs=1e-6)

    def test_measure_coherence_different_length(self) -> None:
        s = np.ones(5)
        c = np.ones(3)
        coh = self.shell.measure_coherence(s, c)
        assert coh == pytest.approx(0.0)

    def test_measure_coherence_zero_signal(self) -> None:
        coh = self.shell.measure_coherence(np.zeros(5), np.ones(5))
        assert coh == pytest.approx(0.0)

    def test_project_returns_projection(self) -> None:
        ts = np.random.default_rng(1).normal(0, 1, 64)
        result = self.shell.project(ts)
        assert result.depth >= 1
        assert result.depth <= MAX_RECURSION_DEPTH
        assert len(result.signal_normalized) == len(ts)
        assert 0.0 <= result.coherence <= 1.0

    def test_project_depth_limit(self) -> None:
        ts = np.random.default_rng(1).normal(0, 1, 64)
        for _ in range(20):
            result = self.shell.project(ts)
        assert result.depth <= MAX_RECURSION_DEPTH

    def test_project_with_correction(self) -> None:
        rng = np.random.default_rng(7)
        ts = rng.normal(0, 1, 64)
        corr = rng.normal(0, 1, 64)
        result = self.shell.project(ts, correction=corr)
        assert isinstance(result.extended, bool)

    def test_mean_depth_tracked(self) -> None:
        ts = np.random.default_rng(0).normal(0, 1, 64)
        self.shell.project(ts)
        self.shell.project(ts)
        assert self.shell.mean_depth >= 1.0

    def test_reset_clears_history(self) -> None:
        ts = np.random.default_rng(0).normal(0, 1, 64)
        self.shell.project(ts)
        self.shell.reset()
        assert self.shell.mean_depth == pytest.approx(0.0)

    def test_constants(self) -> None:
        assert MAX_RECURSION_DEPTH == 8
        assert COHERENCE_EXTENSION_THRESHOLD == pytest.approx(0.92)


# ---------------------------------------------------------------------------
# SemanticAgent tests
# ---------------------------------------------------------------------------


class TestSemanticAgent:
    def setup_method(self) -> None:
        self.agent = SemanticAgent(agent_id="test_agent", kappa=0.5, beta=4.5)

    def test_step_returns_state(self) -> None:
        state = self.agent.step(R=0.6)
        assert isinstance(state, AgentState)

    def test_step_activation_range(self) -> None:
        state = self.agent.step(R=0.5)
        assert 0.0 < state.activation < 1.0

    def test_cycle_increments(self) -> None:
        self.agent.step(0.5)
        self.agent.step(0.7)
        assert len(self.agent.history) == 2

    def test_resonance_positive(self) -> None:
        state = self.agent.step(R=0.5)
        assert state.resonance_score >= 0.0

    def test_mean_resonance(self) -> None:
        for R in [0.3, 0.5, 0.7, 0.9]:
            self.agent.step(R)
        assert 0.0 <= self.agent.mean_resonance <= 1.0

    def test_v_angular_has_value(self) -> None:
        self.agent.step(0.6)
        assert isinstance(self.agent.v_angular, float)

    def test_reset_clears_state(self) -> None:
        self.agent.step(0.5)
        self.agent.reset()
        assert len(self.agent.history) == 0
        assert self.agent.mean_resonance == pytest.approx(0.0)

    def test_field_input_modulates_R(self) -> None:
        state_no_field = self.agent.step(R=0.4, field_input=0.0)
        self.agent.reset()
        state_with_field = self.agent.step(R=0.4, field_input=0.3)
        assert state_no_field.activation != state_with_field.activation


class TestAgentCollective:
    def setup_method(self) -> None:
        self.agents = [
            SemanticAgent(agent_id=f"a{i}", kappa=0.3 + i * 0.1, beta=4.5 + i)
            for i in range(4)
        ]
        self.collective = AgentCollective(self.agents)

    def test_kappa_field(self) -> None:
        kf = self.collective.compute_kappa_field()
        expected = float(np.mean([a.kappa for a in self.agents]))
        assert kf == pytest.approx(expected)

    def test_beta_sync_positive(self) -> None:
        sync = self.collective.compute_beta_sync()
        assert sync >= 0.0

    def test_v_collective_after_step(self) -> None:
        self.collective.step_all(R=0.5)
        v = self.collective.compute_v_collective()
        assert isinstance(v, float)

    def test_step_all_returns_collective_field(self) -> None:
        result = self.collective.step_all(R=0.6)
        assert isinstance(result, CollectiveField)
        assert result.n_agents == 4

    def test_summary_keys(self) -> None:
        summary = self.collective.summary()
        assert "n_agents" in summary
        assert "kappa_field" in summary
        assert "beta_sync" in summary
        assert "v_collective" in summary

    def test_empty_collective(self) -> None:
        empty = AgentCollective([])
        assert empty.compute_kappa_field() == pytest.approx(0.0)
        assert empty.compute_beta_sync() == pytest.approx(0.0)
        assert empty.compute_v_collective() == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# LanternNet tests
# ---------------------------------------------------------------------------


class TestLanternNet:
    def setup_method(self) -> None:
        self.net = LanternNet(seed=42)

    def test_has_8_lanterns(self) -> None:
        assert len(self.net.lanterns) == 8

    def test_lantern_names(self) -> None:
        expected = set(LANTERN_DEFS.keys())
        assert set(self.net.lanterns.keys()) == expected

    def test_em_frequencies_all_correct(self) -> None:
        freqs = self.net.em_frequencies
        for name, f in freqs.items():
            assert f == pytest.approx(LANTERN_EM_FREQ_MHZ)

    def test_impedances_all_correct(self) -> None:
        imps = self.net.impedances
        for name, z in imps.items():
            assert z == pytest.approx(LANTERN_IMPEDANCE_OHM)

    def test_crep_mapping_keys(self) -> None:
        mapping = self.net.get_crep_mapping()
        assert set(mapping.keys()) == set(LANTERN_DEFS.keys())
        for v in mapping.values():
            assert v in ("C", "R", "E", "P")

    def test_step_returns_dict(self) -> None:
        result = self.net.step()
        assert "coherence" in result
        assert "hypotheses" in result
        assert "total_hypotheses" in result
        assert "amplitudes" in result

    def test_coherence_in_unit_interval(self) -> None:
        for _ in range(10):
            result = self.net.step()
        assert 0.0 <= self.net.network_coherence <= 1.0

    def test_step_with_crep_inputs(self) -> None:
        crep = {"C": 0.8, "R": 0.7, "E": 0.6, "P": 0.9}
        result = self.net.step(crep_inputs=crep)
        assert "coherence" in result

    def test_mean_coherence_after_steps(self) -> None:
        for _ in range(5):
            self.net.step()
        assert 0.0 <= self.net.mean_coherence <= 1.0

    def test_summary_contains_key_fields(self) -> None:
        summary = self.net.summary()
        assert summary["n_lanterns"] == 8
        assert summary["em_freq_MHz"] == pytest.approx(LANTERN_EM_FREQ_MHZ)
        assert summary["impedance_ohm"] == pytest.approx(LANTERN_IMPEDANCE_OHM)
        assert summary["target_coherence"] == pytest.approx(TARGET_COHERENCE)

    def test_reset_resets_cycle(self) -> None:
        for _ in range(5):
            self.net.step()
        self.net.reset()
        assert self.net.summary()["cycle"] == 0

    def test_constants(self) -> None:
        assert LANTERN_EM_FREQ_MHZ == pytest.approx(13.5)
        assert LANTERN_IMPEDANCE_OHM == pytest.approx(221.7)
        assert TARGET_COHERENCE == pytest.approx(0.84)
