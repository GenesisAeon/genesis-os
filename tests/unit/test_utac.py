"""Unit tests for genesis_os.runtime.utac."""

from __future__ import annotations

import pytest

from genesis_os.runtime.utac import UTACLogistic


class TestUTACLogistic:
    def test_step_returns_float(self, utac: UTACLogistic) -> None:
        result = utac.step(0.5, 0.6)
        assert isinstance(result, float)

    def test_step_clamps_to_zero(self, utac: UTACLogistic) -> None:
        result = utac.step(0.0, -10.0)
        assert result >= 0.0

    def test_step_clamps_to_K(self, utac: UTACLogistic) -> None:
        result = utac.step(1.0, 100.0)
        assert result <= utac.K

    def test_step_positive_gamma_increases_entropy(self) -> None:
        u = UTACLogistic(r=1.0)
        h0 = 0.3
        h1 = u.step(h0, gamma=1.0)
        assert h1 > h0

    def test_step_negative_gamma_decreases_entropy(self) -> None:
        u = UTACLogistic(r=1.0)
        h0 = 0.7
        h1 = u.step(h0, gamma=-1.0)
        assert h1 < h0

    def test_step_zero_gamma_no_change(self) -> None:
        u = UTACLogistic(r=1.0)
        h0 = 0.5
        h1 = u.step(h0, gamma=0.0)
        assert h1 == pytest.approx(h0)

    def test_step_zero_entropy_stays_zero(self, utac: UTACLogistic) -> None:
        result = utac.step(0.0, 1.0)
        assert result == pytest.approx(0.0)

    def test_time_advances_each_step(self, utac: UTACLogistic) -> None:
        utac.step(0.5, 0.5)
        assert utac.t == pytest.approx(1.0)
        utac.step(0.5, 0.5)
        assert utac.t == pytest.approx(2.0)

    def test_reset_clears_time(self, utac: UTACLogistic) -> None:
        utac.step(0.5, 0.5)
        utac.reset()
        assert utac.t == pytest.approx(0.0)

    def test_equilibrium_positive_gamma(self, utac: UTACLogistic) -> None:
        eq = utac.equilibrium(1.0)
        assert eq == pytest.approx(utac.K)

    def test_equilibrium_negative_gamma(self, utac: UTACLogistic) -> None:
        eq = utac.equilibrium(-1.0)
        assert eq == pytest.approx(0.0)

    def test_equilibrium_zero_gamma(self, utac: UTACLogistic) -> None:
        eq = utac.equilibrium(0.0)
        assert eq == pytest.approx(utac.K / 2.0)

    def test_custom_K(self) -> None:
        u = UTACLogistic(K=2.0, r=0.5)
        result = u.step(1.0, 1.0)
        assert 0.0 <= result <= 2.0

    def test_multiple_steps_converge(self) -> None:
        u = UTACLogistic(r=0.5, K=1.0, sigma=3.0)
        h = 0.1
        for _ in range(50):
            h = u.step(h, gamma=1.0)
        assert h > 0.8  # should converge toward K=1.0

    def test_dt_affects_step_size(self) -> None:
        u1 = UTACLogistic(r=1.0, dt=0.1)
        u2 = UTACLogistic(r=1.0, dt=1.0)
        h = 0.5
        r1 = u1.step(h, 0.5)
        r2 = u2.step(h, 0.5)
        # smaller dt should give smaller change
        assert abs(r1 - h) < abs(r2 - h)
