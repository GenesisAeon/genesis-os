"""Tests für genesis_os.afet.landauer_consistency + esposito_mapping — Phase C."""

from __future__ import annotations

import math
import warnings

import pytest

from genesis_os.afet.esposito_mapping import EspositoDecomposition, map_to_crep
from genesis_os.afet.landauer_consistency import (
    K_BOLTZMANN,
    ROOM_TEMP_K,
    landauer_minimum_entropy,
    validate_landauer_consistency,
)
from genesis_os.core.crep import CREPScore


class TestLandauerMinimum:
    def test_landauer_room_temp(self) -> None:
        minimum = landauer_minimum_entropy(ROOM_TEMP_K, dt=1.0, volume=1.0)
        expected = K_BOLTZMANN * ROOM_TEMP_K * math.log(2)
        assert minimum == pytest.approx(expected, rel=1e-6)
        # NIST: k_B ≈ 1.38e-23, T=300K → E_bit ≈ 2.87e-21 J
        assert minimum == pytest.approx(2.87e-21, rel=0.01)

    def test_landauer_scales_with_temperature(self) -> None:
        m1 = landauer_minimum_entropy(300.0)
        m2 = landauer_minimum_entropy(600.0)
        assert m2 == pytest.approx(2.0 * m1, rel=1e-6)

    def test_landauer_scales_with_n_bits(self) -> None:
        m1 = landauer_minimum_entropy(n_bits=1.0)
        m2 = landauer_minimum_entropy(n_bits=3.0)
        assert m2 == pytest.approx(3.0 * m1, rel=1e-6)

    def test_landauer_scales_inversely_with_dt(self) -> None:
        m1 = landauer_minimum_entropy(dt=1.0)
        m2 = landauer_minimum_entropy(dt=2.0)
        assert m1 == pytest.approx(2.0 * m2, rel=1e-6)


class TestLandauerConsistency:
    def test_consistency_valid(self) -> None:
        consistent, minimum = validate_landauer_consistency(1e-15, warn_only=True)
        assert consistent is True
        assert minimum > 0.0

    def test_consistency_invalid_warn(self) -> None:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            consistent, minimum = validate_landauer_consistency(1e-30, warn_only=True)
        assert consistent is False
        assert len(w) == 1
        assert "Landauer" in str(w[0].message)

    def test_consistency_invalid_raise(self) -> None:
        with pytest.raises(ValueError, match="Landauer"):
            validate_landauer_consistency(1e-30, warn_only=False)

    def test_consistency_exact_boundary(self) -> None:
        minimum = landauer_minimum_entropy(ROOM_TEMP_K)
        consistent, _ = validate_landauer_consistency(minimum, warn_only=True)
        assert consistent is True

    def test_returns_minimum_value(self) -> None:
        _, minimum = validate_landauer_consistency(1.0, warn_only=True)
        expected = landauer_minimum_entropy(ROOM_TEMP_K)
        assert minimum == pytest.approx(expected)


class TestEspositoDecomposition:
    def test_sigma_total(self) -> None:
        decomp = EspositoDecomposition(sigma_maint=3.0, sigma_reorg=1.0)
        assert decomp.sigma_total == pytest.approx(4.0)

    def test_normalization(self) -> None:
        decomp = EspositoDecomposition(sigma_maint=3.0, sigma_reorg=1.0)
        assert decomp.c_esposito + decomp.e_esposito == pytest.approx(1.0)

    def test_c_esposito_equals_maint_fraction(self) -> None:
        decomp = EspositoDecomposition(sigma_maint=0.75, sigma_reorg=0.25)
        assert decomp.c_esposito == pytest.approx(0.75)

    def test_e_esposito_equals_reorg_fraction(self) -> None:
        decomp = EspositoDecomposition(sigma_maint=0.25, sigma_reorg=0.75)
        assert decomp.e_esposito == pytest.approx(0.75)

    def test_zero_total_does_not_divide_by_zero(self) -> None:
        decomp = EspositoDecomposition(sigma_maint=0.0, sigma_reorg=0.0)
        assert decomp.c_esposito == pytest.approx(0.0, abs=1.0)


class TestEspositoToCREPMapping:
    def test_crep_blend_between_bounds(self) -> None:
        crep = CREPScore(coherence=0.8, resonance=0.5, emergence=0.2, poetics=0.5)
        decomp = EspositoDecomposition(sigma_maint=0.4, sigma_reorg=0.6)
        result = map_to_crep(decomp, crep)

        c_corr = result["C_corrected"]
        assert 0.0 <= c_corr <= 1.0
        assert min(crep.coherence, decomp.c_esposito) <= c_corr <= max(
            crep.coherence, decomp.c_esposito
        )

    def test_e_corrected_blend(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.9, poetics=0.5)
        decomp = EspositoDecomposition(sigma_maint=0.3, sigma_reorg=0.7)
        result = map_to_crep(decomp, crep, blend_weight=0.3)

        expected_e = 0.7 * 0.9 + 0.3 * decomp.e_esposito
        assert result["E_corrected"] == pytest.approx(expected_e, rel=1e-6)

    def test_result_contains_all_keys(self) -> None:
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        decomp = EspositoDecomposition(sigma_maint=0.5, sigma_reorg=0.5)
        result = map_to_crep(decomp, crep)
        for key in ("C_esposito", "E_esposito", "C_corrected", "E_corrected"):
            assert key in result
