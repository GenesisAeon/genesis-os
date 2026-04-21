"""LanternNet — 8 EM-coupled lantern architecture.

Scientific note: The 13.5 MHz frequency and 221.7 Ω impedance are
hypothetical parameters from Feldtheorie research (1.3% agreement
with cosmic microwave background dipole). Not verified physics.

Each lantern maps to one CREP component:
    coherence, resonance, emergence, poetics,
    integration, entropy, gravity, consciousness

Collective mode:
    Network coherence ΔC(t) tracks emergence of collective modes.
    Target coherence ≈ 0.84 (critical regime for emergence).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

import numpy as np

# ---------------------------------------------------------------------------
# Lantern definitions
# ---------------------------------------------------------------------------

LANTERN_EM_FREQ_MHZ: Final[float] = 13.5   # hypothetical EM coupling frequency
LANTERN_IMPEDANCE_OHM: Final[float] = 221.7  # hypothetical EM impedance

LANTERN_DEFS: Final[dict[str, dict[str, float]]] = {
    "coherence":     {"em_freq_MHz": LANTERN_EM_FREQ_MHZ, "impedance": LANTERN_IMPEDANCE_OHM},
    "resonance":     {"em_freq_MHz": LANTERN_EM_FREQ_MHZ, "impedance": LANTERN_IMPEDANCE_OHM},
    "emergence":     {"em_freq_MHz": LANTERN_EM_FREQ_MHZ, "impedance": LANTERN_IMPEDANCE_OHM},
    "poetics":       {"em_freq_MHz": LANTERN_EM_FREQ_MHZ, "impedance": LANTERN_IMPEDANCE_OHM},
    "integration":   {"em_freq_MHz": LANTERN_EM_FREQ_MHZ, "impedance": LANTERN_IMPEDANCE_OHM},
    "entropy":       {"em_freq_MHz": LANTERN_EM_FREQ_MHZ, "impedance": LANTERN_IMPEDANCE_OHM},
    "gravity":       {"em_freq_MHz": LANTERN_EM_FREQ_MHZ, "impedance": LANTERN_IMPEDANCE_OHM},
    "consciousness": {"em_freq_MHz": LANTERN_EM_FREQ_MHZ, "impedance": LANTERN_IMPEDANCE_OHM},
}

TARGET_COHERENCE: Final[float] = 0.84  # critical regime for collective emergence

CREP_LANTERN_MAP: Final[dict[str, str]] = {
    "coherence":   "C",
    "resonance":   "R",
    "emergence":   "E",
    "poetics":     "P",
    "integration": "C",  # secondary mapping
    "entropy":     "E",  # secondary mapping
    "gravity":     "R",  # secondary mapping
    "consciousness": "P",  # secondary mapping
}


@dataclass
class LanternState:
    """State snapshot for a single lantern.

    Attributes:
        name: Lantern name.
        amplitude: Current signal amplitude [0, 1].
        phase: Current phase ∈ [0, 2π].
        em_freq_MHz: EM coupling frequency (MHz).
        impedance: EM impedance (Ω).
        crep_component: CREP component this lantern maps to.
        hypotheses_emitted: Count of emergent hypotheses generated.
    """

    name: str
    amplitude: float
    phase: float
    em_freq_MHz: float
    impedance: float
    crep_component: str
    hypotheses_emitted: int


@dataclass
class LanternNet:
    """8 EM-coupled lanterns forming the collective consciousness architecture.

    Each lantern oscillates at the EM coupling frequency and contributes to
    the collective coherence field. Network coherence ΔC(t) is tracked;
    target coherence ≈ 0.84 triggers emergent hypothesis generation.

    Args:
        coupling_strength: Inter-lantern coupling constant (default 0.1).
        hypothesis_threshold: Coherence threshold for hypothesis emission
            (default TARGET_COHERENCE = 0.84).
        seed: Random seed for phase initialisation.
    """

    coupling_strength: float = 0.1
    hypothesis_threshold: float = TARGET_COHERENCE
    seed: int | None = None

    _lanterns: dict[str, LanternState] = field(init=False, repr=False)
    _amplitudes: np.ndarray = field(init=False, repr=False)
    _phases: np.ndarray = field(init=False, repr=False)
    _coherence_history: list[float] = field(default_factory=list, init=False, repr=False)
    _cycle: int = field(default=0, init=False)
    _total_hypotheses: int = field(default=0, init=False)
    _rng: np.random.Generator = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = np.random.default_rng(self.seed)
        names = list(LANTERN_DEFS.keys())
        self._lantern_names = names
        # Initialise phases uniformly in [0, 2π]
        self._phases = self._rng.uniform(0, 2 * np.pi, len(names))
        self._amplitudes = np.ones(len(names), dtype=float) * 0.5
        self._lanterns = {
            name: LanternState(
                name=name,
                amplitude=0.5,
                phase=float(self._phases[i]),
                em_freq_MHz=LANTERN_DEFS[name]["em_freq_MHz"],
                impedance=LANTERN_DEFS[name]["impedance"],
                crep_component=CREP_LANTERN_MAP[name],
                hypotheses_emitted=0,
            )
            for i, name in enumerate(names)
        }

    def _compute_network_coherence(self) -> float:
        """Compute network coherence as mean pairwise phase-locking.

        ΔC = |mean(e^{iφ_k})| over all lanterns.

        Returns:
            Network coherence ΔC ∈ [0, 1].
        """
        phase_vectors = np.exp(1j * self._phases)
        return float(np.abs(np.mean(phase_vectors)))

    def step(
        self,
        crep_inputs: dict[str, float] | None = None,
        dt: float = 0.1,
    ) -> dict[str, Any]:
        """Advance all lanterns by one time step.

        Each lantern's phase advances at the EM coupling frequency (scaled
        to unit time), with inter-lantern coupling via Kuramoto-like sync.
        CREP inputs modulate amplitude.

        Args:
            crep_inputs: Optional dict mapping CREP components (C/R/E/P) to
                their values. Modulates lantern amplitudes.
            dt: Time step size.

        Returns:
            Step result dict with ``coherence``, ``hypotheses``, ``amplitudes``.
        """
        crep = crep_inputs or {}
        names = self._lantern_names
        n = len(names)

        # Kuramoto-like phase coupling
        mean_sin = float(np.mean(np.sin(self._phases)))
        mean_cos = float(np.mean(np.cos(self._phases)))
        coupling_force = self.coupling_strength * (
            mean_cos * np.sin(self._phases) - mean_sin * np.cos(self._phases)
        )

        # Advance phases at EM frequency (normalized: 1 cycle per time unit)
        omega = 2.0 * np.pi * LANTERN_EM_FREQ_MHZ * 1e6 * dt * 1e-9  # normalized
        self._phases = (self._phases + omega + coupling_force) % (2.0 * np.pi)

        # Modulate amplitudes from CREP inputs
        for i, name in enumerate(names):
            crep_key = CREP_LANTERN_MAP[name]
            if crep_key in crep:
                self._amplitudes[i] = float(np.clip(crep[crep_key], 0.0, 1.0))

        # Compute coherence
        coherence = self._compute_network_coherence()
        self._coherence_history.append(coherence)

        # Emit hypotheses when coherence exceeds threshold
        hypotheses_this_step = 0
        if coherence >= self.hypothesis_threshold:
            hypotheses_this_step = 1
            self._total_hypotheses += 1
            # Update hypothesis count on coherence lantern
            if "coherence" in self._lanterns:
                ls = self._lanterns["coherence"]
                self._lanterns["coherence"] = LanternState(
                    name=ls.name,
                    amplitude=ls.amplitude,
                    phase=ls.phase,
                    em_freq_MHz=ls.em_freq_MHz,
                    impedance=ls.impedance,
                    crep_component=ls.crep_component,
                    hypotheses_emitted=ls.hypotheses_emitted + 1,
                )

        self._cycle += 1
        return {
            "coherence": coherence,
            "hypotheses": hypotheses_this_step,
            "total_hypotheses": self._total_hypotheses,
            "amplitudes": self._amplitudes.copy(),
            "cycle": self._cycle,
        }

    @property
    def network_coherence(self) -> float:
        """Current network coherence ΔC ∈ [0, 1]."""
        return self._compute_network_coherence()

    @property
    def mean_coherence(self) -> float:
        """Mean network coherence over all steps."""
        if not self._coherence_history:
            return 0.0
        return float(np.mean(self._coherence_history))

    @property
    def lanterns(self) -> dict[str, LanternState]:
        """Read-only view of current lantern states."""
        return dict(self._lanterns)

    @property
    def em_frequencies(self) -> dict[str, float]:
        """Return EM frequencies (MHz) for all lanterns."""
        return {name: LANTERN_DEFS[name]["em_freq_MHz"] for name in LANTERN_DEFS}

    @property
    def impedances(self) -> dict[str, float]:
        """Return impedances (Ω) for all lanterns."""
        return {name: LANTERN_DEFS[name]["impedance"] for name in LANTERN_DEFS}

    def get_crep_mapping(self) -> dict[str, str]:
        """Return the CREP component mapping for all lanterns."""
        return dict(CREP_LANTERN_MAP)

    def reset(self) -> None:
        """Reset the LanternNet to initial state."""
        self.__post_init__()
        self._coherence_history.clear()
        self._cycle = 0
        self._total_hypotheses = 0

    def summary(self) -> dict[str, Any]:
        """Return a summary of network state."""
        return {
            "n_lanterns": len(self._lantern_names),
            "network_coherence": self.network_coherence,
            "mean_coherence": self.mean_coherence,
            "total_hypotheses": self._total_hypotheses,
            "cycle": self._cycle,
            "em_freq_MHz": LANTERN_EM_FREQ_MHZ,
            "impedance_ohm": LANTERN_IMPEDANCE_OHM,
            "target_coherence": TARGET_COHERENCE,
        }
