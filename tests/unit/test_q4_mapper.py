"""Tests für Q4-Mapper: CREP float → Q4State (kritische Schnittstelle)."""

from __future__ import annotations

import pytest

from genesis_os.core.crep import CREPScore
from genesis_os.core.gray_code import (
    all_gray_pairs_valid,
    encode,
    hamming_distance,
    suggest_gray_path,
    validate_gray_sequence,
)
from genesis_os.core.q4_mapper import (
    DEFAULT_Q4_THRESHOLDS,
    Q4Mapper,
    ThresholdCrossingDetector,
    validate_q4_transition,
)
from genesis_os.core.q4_state import (
    GRAY_ORDER,
    Q4_ENTROPY_BITS,
    Q4_STATE_COUNT,
    TESSERACT_EDGES,
    InvalidQ4StateError,
    InvalidTransitionError,
    Q4State,
)


# ─── Q4State Tests ────────────────────────────────────────────────────────────

class TestQ4State:
    def test_id_calculation(self) -> None:
        assert Q4State(1, 0, 1, 1).id == 11   # 8+0+2+1
        assert Q4State(0, 0, 0, 0).id == 0
        assert Q4State(1, 1, 1, 1).id == 15
        assert Q4State(1, 0, 0, 0).id == 8

    def test_binary_representation(self) -> None:
        assert Q4State(1, 0, 1, 1).binary == "1011"
        assert Q4State(0, 0, 0, 0).binary == "0000"
        assert Q4State(1, 1, 1, 1).binary == "1111"

    def test_entropy_bits(self) -> None:
        # 16 Zustände = 4 Bit (NICHT 16 Bit!)
        assert Q4State(0, 0, 0, 0).entropy_bits == pytest.approx(4.0, abs=0.01)

    def test_state_count(self) -> None:
        assert Q4_STATE_COUNT == 16

    def test_entropy_constant(self) -> None:
        assert Q4_ENTROPY_BITS == pytest.approx(4.0, abs=0.01)

    def test_from_id_roundtrip(self) -> None:
        for i in range(16):
            state = Q4State.from_id(i)
            assert state.id == i

    def test_from_binary_roundtrip(self) -> None:
        for i in range(16):
            state = Q4State.from_id(i)
            assert Q4State.from_binary(state.binary) == state

    def test_invalid_flag_raises(self) -> None:
        with pytest.raises(InvalidQ4StateError):
            Q4State(2, 0, 0, 0)
        with pytest.raises(InvalidQ4StateError):
            Q4State(0, -1, 0, 0)

    def test_invalid_id_raises(self) -> None:
        with pytest.raises(InvalidQ4StateError):
            Q4State.from_id(16)
        with pytest.raises(InvalidQ4StateError):
            Q4State.from_id(-1)

    def test_frozen_immutable(self) -> None:
        state = Q4State(1, 0, 1, 1)
        with pytest.raises(Exception):
            state.C = 0  # type: ignore[misc]

    def test_neighbors_hamming_one(self) -> None:
        for state_id in range(16):
            state = Q4State.from_id(state_id)
            for neighbor in state.neighbors():
                assert hamming_distance(state.id, neighbor.id) == 1

    def test_each_state_has_four_neighbors(self) -> None:
        for state_id in range(16):
            assert len(Q4State.from_id(state_id).neighbors()) == 4

    def test_to_dict(self) -> None:
        state = Q4State(1, 0, 1, 1)
        d = state.to_dict()
        assert d["C"] == 1
        assert d["binary"] == "1011"
        assert d["id"] == 11


# ─── Gray-Code Tests ──────────────────────────────────────────────────────────

class TestGrayCode:
    def test_hamming_invariant_all_pairs(self) -> None:
        """KERN-INVARIANTE: Gray(n) und Gray(n+1) haben immer Hamming-Distanz = 1."""
        assert all_gray_pairs_valid(), (
            "Gray-Code Hamming-Invariante verletzt! "
            "encode(n) und encode(n+1) müssen Hamming-Distanz = 1 haben."
        )

    def test_encode_decode_roundtrip(self) -> None:
        from genesis_os.core.gray_code import decode
        for n in range(16):
            assert decode(encode(n)) == n

    def test_gray_order_adjacency(self) -> None:
        """Alle Nachbarn in GRAY_ORDER unterscheiden sich um 1 Bit."""
        assert validate_gray_sequence(GRAY_ORDER)

    def test_gray_order_length(self) -> None:
        assert len(GRAY_ORDER) == 16

    def test_gray_order_covers_all_states(self) -> None:
        assert set(GRAY_ORDER) == set(range(16))

    def test_hamming_zero_for_equal(self) -> None:
        assert hamming_distance(7, 7) == 0

    def test_hamming_counts_bits(self) -> None:
        assert hamming_distance(0b1010, 0b0101) == 4
        assert hamming_distance(0b1111, 0b1110) == 1

    def test_tesseract_edge_count(self) -> None:
        """Tesserakt hat exakt 32 Kanten (= 16 Ecken × 4 Kanten / 2)."""
        assert TESSERACT_EDGES == 32
        edges = set()
        for i in range(16):
            for neighbor in Q4State.from_id(i).neighbors():
                edge = tuple(sorted([i, neighbor.id]))
                edges.add(edge)
        assert len(edges) == TESSERACT_EDGES


# ─── Q4Mapper Tests ───────────────────────────────────────────────────────────

class TestQ4Mapper:
    def test_map_all_above_threshold(self) -> None:
        mapper = Q4Mapper()
        score = CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)
        state = mapper.map(score)
        assert state == Q4State(1, 1, 1, 1)
        assert state.id == 15

    def test_map_all_below_threshold(self) -> None:
        mapper = Q4Mapper()
        score = CREPScore(coherence=0.1, resonance=0.1, emergence=0.1, poetics=0.1)
        state = mapper.map(score)
        assert state == Q4State(0, 0, 0, 0)
        assert state.id == 0

    def test_map_mixed_known_values(self) -> None:
        # C=0.82≥0.5→1, R=0.44<0.6→0, E=0.91≥0.7→1, P=0.87≥0.8→1
        mapper = Q4Mapper()
        score = CREPScore(coherence=0.82, resonance=0.44, emergence=0.91, poetics=0.87)
        state = mapper.map(score)
        assert state == Q4State(C=1, R=0, E=1, P=1)
        assert state.id == 11
        assert state.binary == "1011"

    def test_map_at_exact_threshold(self) -> None:
        mapper = Q4Mapper()
        # Exakt auf Schwellenwert = über (>=)
        score = CREPScore(coherence=0.5, resonance=0.6, emergence=0.7, poetics=0.8)
        state = mapper.map(score)
        assert state == Q4State(1, 1, 1, 1)

    def test_map_just_below_threshold(self) -> None:
        mapper = Q4Mapper()
        score = CREPScore(coherence=0.499, resonance=0.599, emergence=0.699, poetics=0.799)
        state = mapper.map(score)
        assert state == Q4State(0, 0, 0, 0)

    def test_custom_thresholds(self) -> None:
        mapper = Q4Mapper(thresholds={"C": 0.9, "R": 0.9, "E": 0.9, "P": 0.9})
        score = CREPScore(coherence=0.8, resonance=0.8, emergence=0.8, poetics=0.8)
        assert mapper.map(score) == Q4State(0, 0, 0, 0)

    def test_deterministic(self) -> None:
        mapper = Q4Mapper()
        score = CREPScore(coherence=0.7, resonance=0.7, emergence=0.7, poetics=0.7)
        assert mapper.map(score) == mapper.map(score)

    def test_invalid_threshold_raises(self) -> None:
        with pytest.raises(ValueError):
            Q4Mapper(thresholds={"C": 1.5, "R": 0.6, "E": 0.7, "P": 0.8})

    def test_missing_threshold_raises(self) -> None:
        with pytest.raises(ValueError):
            Q4Mapper(thresholds={"C": 0.5, "R": 0.6})

    def test_map_with_timestamp(self) -> None:
        mapper = Q4Mapper()
        score = CREPScore(coherence=0.8, resonance=0.8, emergence=0.8, poetics=0.8)
        state, t = mapper.map_with_timestamp(score, 42.0)
        assert isinstance(state, Q4State)
        assert t == 42.0

    def test_calibration(self) -> None:
        mapper = Q4Mapper()
        history = [
            CREPScore(coherence=0.3, resonance=0.4, emergence=0.5, poetics=0.6),
            CREPScore(coherence=0.7, resonance=0.8, emergence=0.9, poetics=1.0),
            CREPScore(coherence=0.5, resonance=0.6, emergence=0.7, poetics=0.8),
        ]
        new_thresholds = mapper.calibrate(history)
        assert set(new_thresholds.keys()) == {"C", "R", "E", "P"}
        for val in new_thresholds.values():
            assert 0.0 <= val <= 1.0
        # Thresholds wurden aktualisiert
        assert mapper.thresholds == new_thresholds

    def test_calibration_empty_history(self) -> None:
        mapper = Q4Mapper()
        original = dict(mapper.thresholds)
        result = mapper.calibrate([])
        assert result == original


# ─── ThresholdCrossingDetector Tests ─────────────────────────────────────────

class TestThresholdCrossingDetector:
    def test_no_crossing_on_first_update(self) -> None:
        detector = ThresholdCrossingDetector()
        score = CREPScore(coherence=0.8, resonance=0.8, emergence=0.8, poetics=0.8)
        crossings = detector.update(score)
        assert crossings == []

    def test_crossing_detected(self) -> None:
        detector = ThresholdCrossingDetector()
        low = CREPScore(coherence=0.1, resonance=0.1, emergence=0.1, poetics=0.1)
        high = CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)
        detector.update(low)
        crossings = detector.update(high)
        assert set(crossings) == {"C", "R", "E", "P"}

    def test_single_crossing(self) -> None:
        detector = ThresholdCrossingDetector()
        score1 = CREPScore(coherence=0.1, resonance=0.9, emergence=0.9, poetics=0.9)
        score2 = CREPScore(coherence=0.9, resonance=0.9, emergence=0.9, poetics=0.9)
        detector.update(score1)
        crossings = detector.update(score2)
        assert crossings == ["C"]

    def test_no_crossing_when_state_unchanged(self) -> None:
        detector = ThresholdCrossingDetector()
        score = CREPScore(coherence=0.8, resonance=0.8, emergence=0.8, poetics=0.8)
        detector.update(score)
        crossings = detector.update(score)
        assert crossings == []

    def test_reset_clears_state(self) -> None:
        detector = ThresholdCrossingDetector()
        score = CREPScore(coherence=0.8, resonance=0.8, emergence=0.8, poetics=0.8)
        detector.update(score)
        detector.reset()
        assert detector.current_state() is None


# ─── Q4-Transition-Validator Tests ────────────────────────────────────────────

class TestValidateQ4Transition:
    def test_valid_hamming_one(self) -> None:
        validate_q4_transition(Q4State(0, 0, 0, 0), Q4State(1, 0, 0, 0))  # kein Fehler

    def test_invalid_hamming_two(self) -> None:
        with pytest.raises(InvalidTransitionError):
            validate_q4_transition(Q4State(0, 0, 0, 0), Q4State(1, 1, 0, 0))

    def test_invalid_hamming_four(self) -> None:
        with pytest.raises(InvalidTransitionError):
            validate_q4_transition(Q4State(0, 0, 0, 0), Q4State(1, 1, 1, 1))


# ─── Gray-Path Tests ──────────────────────────────────────────────────────────

class TestSuggestGrayPath:
    def test_path_from_zero_to_fifteen(self) -> None:
        path = suggest_gray_path(0, 15)
        assert path[0] == 0
        assert path[-1] == 15
        # Jeder Schritt im Pfad hat Hamming-Distanz = 1 (State-ID-Raum)
        for i in range(len(path) - 1):
            assert hamming_distance(path[i], path[i + 1]) == 1

    def test_path_is_sequential_hamming_one(self) -> None:
        for start in range(16):
            for end in range(16):
                path = suggest_gray_path(start, end)
                for i in range(len(path) - 1):
                    assert hamming_distance(path[i], path[i + 1]) == 1

    def test_same_state_path(self) -> None:
        path = suggest_gray_path(7, 7)
        assert path == [7]

    def test_adjacent_path_length_one(self) -> None:
        path = suggest_gray_path(0, 1)  # 0000 → 0001: direkt benachbart
        assert len(path) == 2
