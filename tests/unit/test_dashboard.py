"""Unit tests for genesis_os.dashboard."""

from __future__ import annotations

import pytest

from genesis_os.core.crep import CREPScore
from genesis_os.core.phase import Phase
from genesis_os.dashboard.mandala import MandalaDashboard
from genesis_os.dashboard.sonification import SonificationFrame, Sonifier

# ──────────────────────────────────────────────────────────────────────────────
# MandalaDashboard
# ──────────────────────────────────────────────────────────────────────────────


class TestMandalaDashboard:
    @pytest.fixture
    def dashboard(self) -> MandalaDashboard:
        return MandalaDashboard(use_plugin=False)

    @pytest.fixture
    def crep(self) -> CREPScore:
        return CREPScore(coherence=0.7, resonance=0.6, emergence=0.5, poetics=0.8)

    def test_render_ascii_returns_string(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        result = dashboard.render_ascii(crep)
        assert isinstance(result, str)

    def test_render_ascii_non_empty(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        result = dashboard.render_ascii(crep)
        assert len(result) > 0

    def test_render_ascii_contains_phase(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        result = dashboard.render_ascii(crep, phase=Phase.ACTIVATION)
        assert "Activation" in result

    def test_render_ascii_contains_cycle(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        result = dashboard.render_ascii(crep, cycle=7)
        assert "7" in result

    def test_render_ascii_contains_all_axes(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        result = dashboard.render_ascii(crep)
        for axis in ["C", "R", "E", "P"]:
            assert axis in result

    def test_render_ascii_appends_frame(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        dashboard.render_ascii(crep)
        assert len(dashboard.frames) == 1

    def test_frames_returns_copy(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        dashboard.render_ascii(crep)
        frames = dashboard.frames
        frames.clear()
        assert len(dashboard.frames) == 1

    def test_frame_has_crep(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        dashboard.render_ascii(crep)
        frame = dashboard.frames[0]
        assert frame.crep is crep

    def test_frame_has_phase(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        dashboard.render_ascii(crep, phase=Phase.INTEGRATION)
        frame = dashboard.frames[0]
        assert frame.phase == Phase.INTEGRATION

    def test_render_polar_returns_list(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        result = dashboard.render_polar(crep)
        assert isinstance(result, list)

    def test_render_polar_has_four_entries(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        result = dashboard.render_polar(crep)
        assert len(result) == 4

    def test_render_polar_labels(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        result = dashboard.render_polar(crep)
        labels = [r[2] for r in result]
        assert set(labels) == {"C", "R", "E", "P"}

    def test_render_polar_radii_in_unit(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        result = dashboard.render_polar(crep)
        for r, theta, _ in result:
            assert 0.0 <= r <= 1.0

    def test_plugin_render_fallback(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        result = dashboard.plugin_render(crep)
        assert isinstance(result, str)

    def test_multiple_renders_accumulate_frames(self, dashboard: MandalaDashboard, crep: CREPScore) -> None:
        dashboard.render_ascii(crep)
        dashboard.render_ascii(crep)
        assert len(dashboard.frames) == 2


# ──────────────────────────────────────────────────────────────────────────────
# Sonifier
# ──────────────────────────────────────────────────────────────────────────────


class TestSonifier:
    @pytest.fixture
    def sonifier(self) -> Sonifier:
        return Sonifier(use_plugin=False)

    @pytest.fixture
    def crep(self) -> CREPScore:
        return CREPScore(coherence=0.7, resonance=0.6, emergence=0.5, poetics=0.8)

    def test_crep_to_frequencies_returns_frame(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        assert isinstance(frame, SonificationFrame)

    def test_frame_has_four_frequencies(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        assert set(frame.frequencies.keys()) == {"C", "R", "E", "P"}

    def test_frame_has_four_amplitudes(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        assert set(frame.amplitudes.keys()) == {"C", "R", "E", "P"}

    def test_frequencies_are_positive(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        for f in frame.frequencies.values():
            assert f > 0.0

    def test_amplitudes_in_unit(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        for a in frame.amplitudes.values():
            assert 0.0 <= a <= 1.0

    def test_coherence_frequency_in_band(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        assert sonifier.base_hz <= frame.frequencies["C"] <= sonifier.base_hz * 2

    def test_resonance_frequency_in_band(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        assert sonifier.base_hz * 2 <= frame.frequencies["R"] <= sonifier.base_hz * 4

    def test_emergence_frequency_in_band(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        assert sonifier.base_hz / 2 <= frame.frequencies["E"] <= sonifier.base_hz

    def test_poetics_frequency_in_band(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        assert sonifier.base_hz * 4 <= frame.frequencies["P"] <= sonifier.base_hz * 8

    def test_frames_accumulate(self, sonifier: Sonifier, crep: CREPScore) -> None:
        sonifier.crep_to_frequencies(crep)
        sonifier.crep_to_frequencies(crep)
        assert len(sonifier.frames) == 2

    def test_sequence_length(self, sonifier: Sonifier, crep: CREPScore) -> None:
        scores = [crep] * 5
        frames = sonifier.sequence(scores)
        assert len(frames) == 5

    def test_sequence_cycle_index(self, sonifier: Sonifier, crep: CREPScore) -> None:
        scores = [crep] * 3
        frames = sonifier.sequence(scores)
        assert frames[0].cycle == 0
        assert frames[2].cycle == 2

    def test_play_returns_false_without_plugin(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        result = sonifier.play(frame)
        assert result is False

    def test_duration_stored_in_frame(self, sonifier: Sonifier, crep: CREPScore) -> None:
        frame = sonifier.crep_to_frequencies(crep)
        assert frame.duration_ms == pytest.approx(sonifier.duration_ms)

    def test_log_scale_monotone(self, sonifier: Sonifier) -> None:
        f0 = sonifier._log_scale(0.0, 100.0, 1000.0)
        f1 = sonifier._log_scale(0.5, 100.0, 1000.0)
        f2 = sonifier._log_scale(1.0, 100.0, 1000.0)
        assert f0 < f1 < f2
