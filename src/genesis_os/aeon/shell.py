"""AeonShell — symbolic projection and signal containment interface.

Implements:
    - ζ-Lipschitz normalisation on signals
    - Destructive interference extraction via FFT spectral masking
    - Coherence measurement: C = |cos(signal, correction)|
    - Depth extension when coherence C > 0.92
    - Hard limit: N = 8 recursive coupling iterations
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Final

import numpy as np

MAX_RECURSION_DEPTH: Final[int] = 8
COHERENCE_EXTENSION_THRESHOLD: Final[float] = 0.92


@dataclass
class ShellProjection:
    """Result of an AeonShell projection step.

    Attributes:
        signal_normalized: ζ-Lipschitz normalized output signal.
        interference: Extracted destructive interference component.
        coherence: C = |cos(signal, correction)|.
        depth: Number of recursive iterations applied.
        extended: True if depth extension was triggered (C > 0.92).
    """

    signal_normalized: np.ndarray
    interference: np.ndarray
    coherence: float
    depth: int
    extended: bool


@dataclass
class AeonShell:
    """Symbolic projection and containment interface.

    The AeonShell normalises input signals, extracts interference components
    via FFT spectral masking, measures coherence, and applies recursive
    depth extension when coherence exceeds the 0.92 threshold.

    Args:
        zeta: Lipschitz constant for normalisation (default 1.0).
        spectral_mask_fraction: Fraction of high-frequency components
            to zero out in interference extraction (default 0.5).
        max_depth: Hard limit on recursive iterations (default 8).
        coherence_threshold: Threshold above which depth is extended
            (default 0.92).
    """

    zeta: float = 1.0
    spectral_mask_fraction: float = 0.5
    max_depth: int = MAX_RECURSION_DEPTH
    coherence_threshold: float = COHERENCE_EXTENSION_THRESHOLD
    _depth_history: list[int] = field(default_factory=list, init=False, repr=False)

    def zeta_normalize(self, signal: np.ndarray) -> np.ndarray:
        """Apply ζ-Lipschitz normalisation to a signal.

        Clips the Lipschitz constant of the signal to ≤ ζ by normalising
        by max(|gradient|, ζ). Preserves the signal's mean.

        Args:
            signal: 1-D input signal.

        Returns:
            Lipschitz-normalised signal with same length.
        """
        arr = np.asarray(signal, dtype=float)
        if len(arr) < 2:
            return arr.copy()

        grad = np.diff(arr)
        max_grad = float(np.max(np.abs(grad)))
        if max_grad < 1e-12:
            return arr.copy()

        scale = min(1.0, self.zeta / max_grad)
        normalized = arr[0:1].copy()
        for g in grad * scale:
            normalized = np.append(normalized, normalized[-1] + g)
        # Preserve mean
        normalized = normalized - np.mean(normalized) + np.mean(arr)
        return normalized

    def extract_interference(self, signal: np.ndarray) -> np.ndarray:
        """Extract destructive interference via FFT spectral masking.

        Zeros out the high-frequency half of the spectrum (above the
        spectral_mask_fraction * Nyquist) and returns the inverse FFT.
        The interference is signal - filtered_signal.

        Args:
            signal: 1-D input signal.

        Returns:
            Interference component (same shape as signal).
        """
        arr = np.asarray(signal, dtype=float)
        if len(arr) < 4:
            return np.zeros_like(arr)

        spectrum = np.fft.rfft(arr)
        n_keep = max(1, int(len(spectrum) * (1.0 - self.spectral_mask_fraction)))
        masked = spectrum.copy()
        masked[n_keep:] = 0.0
        filtered = np.fft.irfft(masked, n=len(arr))
        return arr - filtered

    def measure_coherence(
        self, signal: np.ndarray, correction: np.ndarray
    ) -> float:
        """Measure coherence as cosine similarity between signal and correction.

        C = |cos(signal, correction)| = |signal · correction| / (|signal| · |correction|)

        Args:
            signal: Primary signal vector.
            correction: Correction / reference vector (same length).

        Returns:
            Coherence C ∈ [0, 1].
        """
        s = np.asarray(signal, dtype=float).ravel()
        c = np.asarray(correction, dtype=float).ravel()
        if len(s) != len(c) or len(s) == 0:
            return 0.0
        norm_s = float(np.linalg.norm(s))
        norm_c = float(np.linalg.norm(c))
        if norm_s < 1e-12 or norm_c < 1e-12:
            return 0.0
        cos_val = float(np.dot(s, c)) / (norm_s * norm_c)
        return float(np.clip(abs(cos_val), 0.0, 1.0))

    def project(
        self, signal: np.ndarray, correction: np.ndarray | None = None
    ) -> ShellProjection:
        """Apply the full projection pipeline with recursive depth extension.

        1. ζ-Lipschitz normalise the signal
        2. Extract interference via FFT masking
        3. Compute coherence between normalized signal and correction
        4. If C > coherence_threshold and depth < max_depth: extend recursion

        Args:
            signal: 1-D input signal.
            correction: Optional reference signal for coherence (defaults to
                interference component if None).

        Returns:
            ShellProjection result.
        """
        arr = np.asarray(signal, dtype=float)
        current = arr.copy()
        depth = 0
        extended = False

        while depth < self.max_depth:
            normalized = self.zeta_normalize(current)
            interference = self.extract_interference(normalized)

            corr = correction if correction is not None else interference
            coherence = self.measure_coherence(normalized, corr)

            depth += 1
            if coherence > self.coherence_threshold and depth < self.max_depth:
                # High coherence → extend: use normalized as next input
                current = normalized
                extended = True
                continue
            break

        self._depth_history.append(depth)
        return ShellProjection(
            signal_normalized=normalized,
            interference=interference,
            coherence=coherence,
            depth=depth,
            extended=extended,
        )

    @property
    def mean_depth(self) -> float:
        """Mean recursion depth across all projection calls."""
        if not self._depth_history:
            return 0.0
        return float(np.mean(self._depth_history))

    def reset(self) -> None:
        """Clear depth history."""
        self._depth_history.clear()
