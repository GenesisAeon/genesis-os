"""Unit tests for genesis_os.core.phase."""

from __future__ import annotations

import pytest

from genesis_os.core.phase import Phase, PhaseMatrix, PhaseTransition

# ──────────────────────────────────────────────────────────────────────────────
# Phase enum
# ──────────────────────────────────────────────────────────────────────────────


class TestPhaseEnum:
    def test_all_phases_exist(self) -> None:
        phases = list(Phase)
        assert len(phases) == 4

    def test_crep_focus_initiation(self) -> None:
        assert Phase.INITIATION.crep_focus == "C"

    def test_crep_focus_activation(self) -> None:
        assert Phase.ACTIVATION.crep_focus == "R"

    def test_crep_focus_integration(self) -> None:
        assert Phase.INTEGRATION.crep_focus == "E"

    def test_crep_focus_reflection(self) -> None:
        assert Phase.REFLECTION.crep_focus == "P"

    def test_next_phase_initiation(self) -> None:
        assert Phase.INITIATION.next_phase == Phase.ACTIVATION

    def test_next_phase_activation(self) -> None:
        assert Phase.ACTIVATION.next_phase == Phase.INTEGRATION

    def test_next_phase_integration(self) -> None:
        assert Phase.INTEGRATION.next_phase == Phase.REFLECTION

    def test_next_phase_reflection_wraps(self) -> None:
        assert Phase.REFLECTION.next_phase == Phase.INITIATION

    def test_description_non_empty(self) -> None:
        for phase in Phase:
            assert len(phase.description) > 0

    def test_phase_value_is_string(self) -> None:
        for phase in Phase:
            assert isinstance(phase.value, str)

    def test_phase_from_string(self) -> None:
        p = Phase("Initiation")
        assert p == Phase.INITIATION


# ──────────────────────────────────────────────────────────────────────────────
# PhaseTransition
# ──────────────────────────────────────────────────────────────────────────────


class TestPhaseTransition:
    def test_is_full_cycle_true(self) -> None:
        t = PhaseTransition(
            from_phase=Phase.REFLECTION,
            to_phase=Phase.INITIATION,
            trigger_gamma=0.8,
            cycle=4,
        )
        assert t.is_full_cycle is True

    def test_is_full_cycle_false(self) -> None:
        t = PhaseTransition(
            from_phase=Phase.INITIATION,
            to_phase=Phase.ACTIVATION,
            trigger_gamma=0.7,
            cycle=1,
        )
        assert t.is_full_cycle is False

    def test_metadata_default_empty(self) -> None:
        t = PhaseTransition(
            from_phase=Phase.INITIATION,
            to_phase=Phase.ACTIVATION,
            trigger_gamma=0.7,
            cycle=1,
        )
        assert t.metadata == {}

    def test_metadata_stored(self) -> None:
        t = PhaseTransition(
            from_phase=Phase.INITIATION,
            to_phase=Phase.ACTIVATION,
            trigger_gamma=0.7,
            cycle=1,
            metadata={"key": "value"},
        )
        assert t.metadata["key"] == "value"


# ──────────────────────────────────────────────────────────────────────────────
# PhaseMatrix
# ──────────────────────────────────────────────────────────────────────────────


class TestPhaseMatrix:
    def test_initial_phase_default(self) -> None:
        pm = PhaseMatrix()
        assert pm.current_phase == Phase.INITIATION

    def test_initial_phase_custom(self) -> None:
        pm = PhaseMatrix(initial_phase=Phase.REFLECTION)
        assert pm.current_phase == Phase.REFLECTION

    def test_cycle_count_starts_at_zero(self) -> None:
        pm = PhaseMatrix()
        assert pm.cycle_count == 0

    def test_no_transition_below_threshold(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.8))
        result = pm.advance(0.5)
        assert result is None
        assert pm.current_phase == Phase.INITIATION

    def test_transition_above_threshold(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.5))
        result = pm.advance(0.7)
        assert result is not None
        assert pm.current_phase == Phase.ACTIVATION

    def test_transition_increments_cycle_count(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.0))
        pm.advance(0.1)
        assert pm.cycle_count == 1

    def test_four_transitions_complete_full_cycle(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.0))
        for _ in range(4):
            pm.advance(0.1)
        assert pm.current_phase == Phase.INITIATION
        assert pm.full_cycles == 1

    def test_full_cycles_counts_correctly(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.0))
        for _ in range(8):
            pm.advance(0.1)
        assert pm.full_cycles == 2

    def test_threshold_for_current_phase(self) -> None:
        pm = PhaseMatrix(thresholds={Phase.INITIATION: 0.55})
        assert pm.threshold_for() == pytest.approx(0.55)

    def test_threshold_for_specific_phase(self) -> None:
        pm = PhaseMatrix(thresholds={Phase.REFLECTION: 0.70})
        assert pm.threshold_for(Phase.REFLECTION) == pytest.approx(0.70)

    def test_should_transition_true(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.5))
        assert pm.should_transition(0.7) is True

    def test_should_transition_false(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.9))
        assert pm.should_transition(0.5) is False

    def test_transitions_list_grows(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.0))
        pm.advance(0.5)
        pm.advance(0.5)
        assert len(pm.transitions) == 2

    def test_transitions_returns_copy(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.0))
        pm.advance(0.5)
        t1 = pm.transitions
        t1.clear()
        assert len(pm.transitions) == 1

    def test_reset_clears_state(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.0))
        pm.advance(0.5)
        pm.reset()
        assert pm.cycle_count == 0
        assert pm.current_phase == Phase.INITIATION
        assert pm.transitions == []

    def test_advance_attaches_metadata(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.0))
        t = pm.advance(0.5, metadata={"test": True})
        assert t is not None
        assert t.metadata["test"] is True

    def test_advance_at_exact_threshold(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.7))
        result = pm.advance(0.7)
        assert result is not None

    def test_advance_just_below_threshold(self) -> None:
        pm = PhaseMatrix(thresholds=dict.fromkeys(Phase, 0.7))
        result = pm.advance(0.6999)
        assert result is None

    def test_default_threshold_fallback(self) -> None:
        pm = PhaseMatrix()
        # thresholds default dict – missing keys fall back to 0.6
        t = pm.threshold_for(Phase.INITIATION)
        assert isinstance(t, float)
