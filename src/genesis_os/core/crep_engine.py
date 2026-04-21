"""Enhanced CREP Engine with empirically grounded component metrics.

Extends the base CREP framework (crep.py) with scientifically validated
computation methods for each CREP component, ported from Feldtheorie.

C (Coherence):  1 - CV_T  (coefficient of variation of inter-event intervals)
                Pikovsky & Kurths (1997) coherence resonance metric.

R (Resonance):  exp(-(f - f_res)^2 / (2·Δf^2))
                Gaussian proximity to noise-optimal resonance peak.

E (Emergence):  Approximated synergy via partial-information-decomposition proxy.
                Tönjes et al. (2021, Nat. Commun. 12, 72) approximation.

P (Poetics):    Normalized permutation entropy H_perm / log(order!)
                Ordinal pattern diversity without external template.

Γ (CREP tensor): (C·R·E·P)^(1/4)  — geometric mean

Type-VI safety governance thresholds (from Feldtheorie):
    Γ < 0.6  → log only
    Γ < 0.7  → monitor
    Γ < 0.8  → escalation required
    Γ ≥ 0.9  → halt + review
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import permutations
from typing import Final

import numpy as np

from genesis_os.core.crep import CREPScore

# ---------------------------------------------------------------------------
# Governance thresholds (Type-VI safety)
# ---------------------------------------------------------------------------

CREP_THRESHOLDS: Final[dict[str, float]] = {
    "informational": 0.6,
    "warning": 0.7,
    "reviewer": 0.8,
    "critical": 0.9,
}

GovernanceLevel = str


# ---------------------------------------------------------------------------
# Individual component functions
# ---------------------------------------------------------------------------


def compute_coherence(time_series: np.ndarray, _window: int = 50) -> float:
    """Compute coherence C from an inter-event interval time series.

    C = 1 - CV_T  where  CV_T = σ_T / μ_T
    (coefficient of variation of inter-event intervals)

    Follows Pikovsky & Kurths (1997) coherence resonance metric.
    Range: [0, 1], higher = more coherent.

    Args:
        time_series: 1-D array of values (e.g. spike train, threshold crossings).
        window: Maximum window for interval analysis (default 50).

    Returns:
        C ∈ [0, 1].
    """
    arr = np.asarray(time_series, dtype=float)
    if len(arr) < 2:
        return 0.5

    # Extract inter-event intervals: indices where sign changes or threshold cross
    # For general signals, use zero-crossing intervals as proxy
    crossings = np.where(np.diff(np.sign(arr - np.mean(arr))))[0]
    if len(crossings) < 2:
        # No oscillation detected — assume moderate coherence
        return 0.5

    intervals = np.diff(crossings.astype(float))
    if len(intervals) == 0:
        return 0.5

    mu_t = float(np.mean(intervals))
    sigma_t = float(np.std(intervals))

    if mu_t < 1e-12:
        return 0.5

    cv_t = sigma_t / mu_t
    return float(np.clip(1.0 - cv_t, 0.0, 1.0))


def compute_resonance(
    time_series: np.ndarray,
    f_res: float | None = None,
    delta_f: float | None = None,
) -> float:
    """Compute resonance R as Gaussian proximity to spectral peak.

    R = exp(-(f - f_res)^2 / (2·Δf^2))

    If f_res is None, the spectral peak frequency is used as the resonance
    target (i.e., the system is at its own peak → R = 1).

    Args:
        time_series: 1-D signal array.
        f_res: Target resonance frequency (normalised, in [0, 0.5]).
            If None, uses spectral peak → returns value near 1.0.
        delta_f: Frequency bandwidth Δf. Defaults to 1/len(time_series).

    Returns:
        R ∈ [0, 1].
    """
    arr = np.asarray(time_series, dtype=float)
    n = len(arr)
    if n < 4:
        return 0.5

    freqs = np.fft.rfftfreq(n)
    power = np.abs(np.fft.rfft(arr - np.mean(arr))) ** 2

    if len(power) == 0:
        return 0.5

    peak_idx = int(np.argmax(power[1:]) + 1) if len(power) > 1 else 0
    f_peak = float(freqs[peak_idx])

    if f_res is None:
        # At spectral peak → R = 1 by definition
        return 1.0

    df = delta_f if delta_f is not None else max(1.0 / n, 1e-6)
    exponent = -((f_peak - f_res) ** 2) / (2.0 * df**2)
    return float(np.clip(math.exp(exponent), 0.0, 1.0))


def compute_emergence(
    component_states: np.ndarray,
    system_output: np.ndarray,
) -> float:
    """Compute emergence E as synergy proxy via partial information decomposition.

    Approximation following Tönjes et al. (2021, Nat. Commun. 12, 72):
        E = max(0, I(output; all_components) - Σ I(output; component_i))

    Uses mutual information estimated from correlation coefficients as proxy.
    Range: [0, 1].

    Args:
        component_states: 2-D array shape (n_components, T) or (T, n_components).
            Each row/column is one component's time series.
        system_output: 1-D array of length T (collective output signal).

    Returns:
        E ∈ [0, 1].
    """
    comps = np.atleast_2d(np.asarray(component_states, dtype=float))
    out = np.asarray(system_output, dtype=float)

    # Standardise shape to (n_components, T)
    if (comps.shape[0] > comps.shape[1] and comps.shape[1] == len(out)) or (
        comps.shape[1] != len(out) and comps.shape[0] == len(out)
    ):
        comps = comps.T

    n_comps = comps.shape[0]
    T = comps.shape[1]
    if T < 2 or len(out) != T:
        return 0.5

    out_std = float(np.std(out))
    if out_std < 1e-12:
        return 0.0

    out_norm = (out - np.mean(out)) / out_std

    # I(output; all_components) proxy: |corr(output, mean_components)|
    mean_comp = np.mean(comps, axis=0)
    std_mean = float(np.std(mean_comp))
    if std_mean < 1e-12:
        i_total = 0.0
    else:
        mean_norm = (mean_comp - np.mean(mean_comp)) / std_mean
        i_total = float(abs(np.corrcoef(out_norm, mean_norm)[0, 1]))

    # Σ I(output; component_i) proxy
    i_sum = 0.0
    for i in range(n_comps):
        comp_i = comps[i]
        std_i = float(np.std(comp_i))
        if std_i < 1e-12:
            continue
        comp_norm = (comp_i - np.mean(comp_i)) / std_i
        corr = float(abs(np.corrcoef(out_norm, comp_norm)[0, 1]))
        i_sum += corr

    i_sum_norm = i_sum / n_comps if n_comps > 0 else 0.0

    synergy = max(0.0, i_total - i_sum_norm)
    return float(np.clip(synergy, 0.0, 1.0))


def compute_poetics(time_series: np.ndarray, order: int = 3) -> float:
    """Compute poetics P as normalized permutation entropy.

    P = H_perm / log(order!)

    Ordinal pattern diversity without external template.
    Range: [0, 1].

    Bandt & Pompe (2002) permutation entropy.

    Args:
        time_series: 1-D signal array.
        order: Pattern order (default 3). Must be ≥ 2.

    Returns:
        P ∈ [0, 1].
    """
    arr = np.asarray(time_series, dtype=float)
    n = len(arr)
    order = max(2, order)

    if n < order + 1:
        return 0.5

    # Build all permutation patterns of the given order
    all_perms = list(permutations(range(order)))
    perm_to_idx = {p: i for i, p in enumerate(all_perms)}
    n_patterns = len(all_perms)

    counts = np.zeros(n_patterns, dtype=float)
    for i in range(n - order + 1):
        window = arr[i : i + order]
        pattern = tuple(int(x) for x in np.argsort(window))
        idx = perm_to_idx.get(pattern)
        if idx is not None:
            counts[idx] += 1.0

    total = counts.sum()
    if total == 0:
        return 0.0

    probs = counts[counts > 0] / total
    h_perm = float(-np.sum(probs * np.log(probs + 1e-15)))
    h_max = math.log(math.factorial(order))

    if h_max < 1e-12:
        return 0.0

    return float(np.clip(h_perm / h_max, 0.0, 1.0))


def compute_gamma(C: float, R: float, E: float, P: float) -> float:
    """Compute CREP coupling tensor Γ as geometric mean.

    Γ = (C·R·E·P)^(1/4)   with all components ∈ [0, 1]

    Args:
        C: Coherence ∈ [0, 1].
        R: Resonance ∈ [0, 1].
        E: Emergence ∈ [0, 1].
        P: Poetics ∈ [0, 1].

    Returns:
        Γ ∈ [0, 1].
    """
    c_c = float(np.clip(C, 0.0, 1.0))
    c_r = float(np.clip(R, 0.0, 1.0))
    c_e = float(np.clip(E, 0.0, 1.0))
    c_p = float(np.clip(P, 0.0, 1.0))
    return float((c_c * c_r * c_e * c_p) ** 0.25)


def governance_level(gamma: float) -> GovernanceLevel:
    """Return the Type-VI governance level for a given Γ value.

    Args:
        gamma: CREP coupling value Γ.

    Returns:
        One of: ``"informational"``, ``"warning"``, ``"reviewer"``,
        ``"critical"``, or ``"safe"``.
    """
    if gamma >= CREP_THRESHOLDS["critical"]:
        return "critical"
    if gamma >= CREP_THRESHOLDS["reviewer"]:
        return "reviewer"
    if gamma >= CREP_THRESHOLDS["warning"]:
        return "warning"
    if gamma >= CREP_THRESHOLDS["informational"]:
        return "informational"
    return "safe"


# ---------------------------------------------------------------------------
# EmpiricalCREPEvaluator
# ---------------------------------------------------------------------------


@dataclass
class EmpiricalCREPEvaluator:
    """Evaluates CREP scores from raw time-series data using empirical metrics.

    Uses compute_coherence / compute_resonance / compute_emergence /
    compute_poetics to produce CREPScore objects from actual signal arrays.

    Args:
        coherence_window: Window for zero-crossing interval analysis (default 50).
        permutation_order: Order for permutation entropy (default 3).
        f_res: Optional target resonance frequency for R computation.
    """

    coherence_window: int = 50
    permutation_order: int = 3
    f_res: float | None = None

    def evaluate_from_signals(
        self,
        signal: np.ndarray,
        components: np.ndarray | None = None,
        timestamp: int = 0,
    ) -> CREPScore:
        """Build a CREPScore from a raw signal array.

        Args:
            signal: Primary 1-D time series.
            components: Optional (n_components, T) array for emergence calc.
                If None, uses a single-element array → E=0.5.
            timestamp: Cycle index for the CREPScore.

        Returns:
            CREPScore with empirically computed C, R, E, P.
        """
        sig = np.asarray(signal, dtype=float)

        C = compute_coherence(sig, self.coherence_window)
        R = compute_resonance(sig, f_res=self.f_res)
        P = compute_poetics(sig, order=self.permutation_order)

        E = compute_emergence(components, sig) if components is not None else 0.5

        return CREPScore(
            coherence=C,
            resonance=R,
            emergence=E,
            poetics=P,
            timestamp=timestamp,
        )

    def compute_gamma_from_signal(self, signal: np.ndarray) -> float:
        """Compute Γ directly from a signal using geometric-mean formula.

        Args:
            signal: 1-D time series.

        Returns:
            Γ ∈ [0, 1].
        """
        score = self.evaluate_from_signals(signal)
        return compute_gamma(score.coherence, score.resonance, score.emergence, score.poetics)

    def assess_governance(self, gamma: float) -> dict[str, object]:
        """Return governance assessment dict for a given Γ value.

        Args:
            gamma: CREP coupling value Γ.

        Returns:
            Dict with ``level``, ``gamma``, ``action`` keys.
        """
        level = governance_level(gamma)
        actions = {
            "safe": "no action required",
            "informational": "log event",
            "warning": "monitor closely",
            "reviewer": "escalate for human review",
            "critical": "halt operation and review",
        }
        return {
            "level": level,
            "gamma": gamma,
            "action": actions.get(level, "unknown"),
        }
