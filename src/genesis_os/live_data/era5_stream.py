"""ERA5 Arctic sea-ice data stream with Tension Metric (Milestone 3.2).

Streams historical ERA5 reanalysis data from CSV and computes the
*Tension Metric* τ(t) — a composite Early Warning Signal (EWS) that
combines rising variance and critical-slowing-down (AR(1)) to detect
impending phase transitions.

The Tension Metric is defined as:

.. math::

    \\tau(t) = \\frac{1}{2}\\left(
        \\frac{\\sigma^2_{\\text{window}}(t)}{\\sigma^2_{\\text{baseline}}}
        + |\\hat{\\phi}_1(t)|
    \\right)

where :math:`\\hat{\\phi}_1` is the lag-1 autocorrelation coefficient
estimated over the sliding window, and :math:`\\sigma^2_{\\text{baseline}}`
is the variance over the full historical record.

A CREP-coupled variant is also provided:

.. math::

    \\tau_{\\Gamma}(t) = \\tau(t) \\cdot (1 + \\Gamma(t))
"""

from __future__ import annotations

import csv
from collections.abc import Iterator
from dataclasses import dataclass, field
from importlib.resources import files as _pkg_files
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class TensionReading:
    """A single timestep reading from the ERA5 stream.

    Attributes:
        year: Calendar year.
        temp_anomaly: Arctic temperature anomaly (°C relative to baseline).
        ice_volume: Arctic sea-ice volume proxy (m / decade or similar unit).
        tension: Raw tension metric τ(t) ∈ [0, ∞).
        tension_crep: CREP-coupled tension τ_Γ(t) = τ · (1 + Γ).
        variance_ratio: Sliding-window variance / baseline variance.
        ar1: Lag-1 autocorrelation coefficient over the sliding window.
    """

    year: int
    temp_anomaly: float
    ice_volume: float
    tension: float
    tension_crep: float
    variance_ratio: float
    ar1: float


@dataclass
class ERA5Stream:
    """Streaming iterator over ERA5 Arctic sea-ice reanalysis data.

    Reads the bundled ``era5_kipppunkte.csv`` (or a custom path) and
    yields :class:`TensionReading` objects one year at a time, simulating
    a real-time data feed.

    Args:
        data_path: Path to the ERA5 CSV file.  Defaults to the bundled
            ``data/era5_kipppunkte.csv`` relative to this file's package.
        window: Sliding window length for variance and AR(1) estimation
            (default ``15`` years).
        gamma: CREP coupling Γ applied to compute τ_Γ (default ``0.0``).
    """

    data_path: Path | None = None
    window: int = 15
    gamma: float = 0.0

    _records: list[tuple[int, float, float]] = field(default_factory=list, init=False, repr=False)
    _baseline_var: float = field(default=1.0, init=False)

    def __post_init__(self) -> None:
        if self.data_path is None:
            self.data_path = self._default_data_path()
        self._load(self.data_path)

    @staticmethod
    def _default_data_path() -> Path:
        """Resolve the bundled CSV regardless of install vs development layout.

        Prefers the package-bundled copy (available in installed wheels) and
        falls back to the repository ``data/`` directory for editable installs.
        """
        try:
            ref = _pkg_files("genesis_os.live_data").joinpath("era5_kipppunkte.csv")
            candidate = Path(str(ref))
            if candidate.exists():
                return candidate  # pragma: no cover
        except (TypeError, ModuleNotFoundError):  # pragma: no cover
            pass  # pragma: no cover
        return Path(__file__).parent.parent.parent.parent / "data" / "era5_kipppunkte.csv"

    def _load(self, path: Path) -> None:
        """Parse the CSV and compute the baseline variance."""
        with path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                self._records.append(
                    (int(row["year"]), float(row["temp_anomaly"]), float(row["ice_volume"]))
                )
        if not self._records:
            msg = f"ERA5 data file is empty: {path}"
            raise ValueError(msg)
        ice = np.array([r[2] for r in self._records], dtype=float)
        var = float(np.var(ice, ddof=1)) if len(ice) > 1 else 1.0
        self._baseline_var = var if var > 0.0 else 1.0

    # ------------------------------------------------------------------
    # Tension Metric helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ar1(series: np.ndarray) -> float:
        """Estimate the lag-1 autocorrelation coefficient.

        Args:
            series: 1-D array of length ≥ 2.

        Returns:
            Pearson correlation between ``series[:-1]`` and ``series[1:]``,
            or ``0.0`` if the array is too short or has zero variance.
        """
        if len(series) < 2:
            return 0.0
        x, y = series[:-1], series[1:]
        std_x, std_y = np.std(x), np.std(y)
        if std_x < 1e-12 or std_y < 1e-12:
            return 0.0
        return float(np.mean((x - x.mean()) * (y - y.mean())) / (std_x * std_y))

    def _tension(self, window_ice: np.ndarray, gamma: float) -> tuple[float, float, float, float]:
        """Compute raw τ, CREP-coupled τ_Γ, variance_ratio, and AR(1).

        Args:
            window_ice: Ice-volume values over the current sliding window.
            gamma: CREP coupling Γ.

        Returns:
            Tuple ``(tau, tau_crep, variance_ratio, ar1)`` where ``tau`` is the
            uncoupled baseline metric and ``tau_crep = tau · (1 + Γ)``.
        """
        var_w = float(np.var(window_ice, ddof=1)) if len(window_ice) > 1 else 0.0
        var_ratio = var_w / self._baseline_var
        ar1 = self._ar1(window_ice)
        tau = 0.5 * (var_ratio + abs(ar1))
        tau_crep = tau * (1.0 + gamma)
        return tau, tau_crep, var_ratio, ar1

    # ------------------------------------------------------------------
    # Public streaming API
    # ------------------------------------------------------------------

    def stream(self, gamma: float | None = None) -> Iterator[TensionReading]:
        """Yield :class:`TensionReading` objects for every year in the record.

        Earlier years (before a full window is available) use all data
        from the start up to the current point.

        Args:
            gamma: Override the instance-level CREP coupling Γ.

        Yields:
            :class:`TensionReading` for each year.
        """
        effective_gamma = gamma if gamma is not None else self.gamma
        ice_all = np.array([r[2] for r in self._records], dtype=float)

        for i, (year, temp, ice) in enumerate(self._records):
            start = max(0, i + 1 - self.window)
            window_slice = ice_all[start : i + 1]
            tau, tau_crep, var_ratio, ar1 = self._tension(window_slice, effective_gamma)
            yield TensionReading(
                year=year,
                temp_anomaly=temp,
                ice_volume=ice,
                tension=tau,
                tension_crep=tau_crep,
                variance_ratio=var_ratio,
                ar1=ar1,
            )

    def latest(self, gamma: float | None = None) -> TensionReading:
        """Return the tension reading for the most recent year.

        Args:
            gamma: Override the instance-level CREP coupling Γ.

        Returns:
            :class:`TensionReading` for the last record in the dataset.
        """
        *_, last = self.stream(gamma=gamma)
        return last

    def readings(self, gamma: float | None = None) -> list[TensionReading]:
        """Return all tension readings as a list.

        Args:
            gamma: Override the instance-level CREP coupling Γ.

        Returns:
            List of :class:`TensionReading` for every year.
        """
        return list(self.stream(gamma=gamma))

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def years(self) -> list[int]:
        """Sorted list of years in the dataset."""
        return [r[0] for r in self._records]

    @property
    def n_records(self) -> int:
        """Total number of annual records."""
        return len(self._records)

    @property
    def baseline_variance(self) -> float:
        """Full-record baseline variance of ice-volume."""
        return self._baseline_var
