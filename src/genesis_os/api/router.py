"""GenesisRouter — pure-Python request/response layer for genesis-os API.

Designed to be framework-agnostic: the router handles domain logic and
returns plain dicts, making it easy to wrap with FastAPI, Flask, or test
directly without an HTTP server.

FastAPI integration (optional — only imported if fastapi is installed):
    from genesis_os.api.server import create_app
    app = create_app()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from genesis_os.core.crep_engine import (
    EmpiricalCREPEvaluator,
    compute_gamma,
    governance_level,
)
from genesis_os.core.utac_bridge import DomainBetaRegistry, UTACBridge
from genesis_os.science.models.logistic_fit import fit_utac_logistic
from genesis_os.vrig.velocity import VRIGVelocity


@dataclass
class GenesisRouter:
    """Pure-Python domain-logic router for genesis-os API endpoints.

    All methods accept plain Python dicts/lists and return plain dicts,
    making them independently testable without any HTTP framework.

    Args:
        bridge: UTACBridge instance (created if None).
        registry: DomainBetaRegistry instance (created if None).
        vrig: VRIGVelocity instance (created if None).
        crep_evaluator: EmpiricalCREPEvaluator instance (created if None).
    """

    bridge: UTACBridge = field(default_factory=UTACBridge)
    registry: DomainBetaRegistry = field(default_factory=DomainBetaRegistry)
    vrig: VRIGVelocity = field(default_factory=VRIGVelocity)
    crep_evaluator: EmpiricalCREPEvaluator = field(
        default_factory=EmpiricalCREPEvaluator
    )
    _mirror_state: dict[str, Any] = field(default_factory=dict, init=False)
    _cycle_count: int = field(default=0, init=False)

    # ------------------------------------------------------------------
    # POST /utac/fit
    # ------------------------------------------------------------------

    def utac_fit(
        self,
        R: list[float],
        response: list[float],
        n_bootstrap: int = 100,
    ) -> dict[str, Any]:
        """Fit UTAC logistic σ(β(R-Θ)) to submitted data.

        Args:
            R: Resource/state variable array.
            response: Observed response array.
            n_bootstrap: Bootstrap iterations for CI (default 100).

        Returns:
            Dict with beta, theta, r_squared, delta_aic_linear,
            beta_ci_95, domain, and success flag.
        """
        R_arr = np.asarray(R, dtype=float)
        y_arr = np.asarray(response, dtype=float)
        result = fit_utac_logistic(R_arr, y_arr, n_bootstrap=n_bootstrap)
        domain = self.registry.classify_domain(result.beta)
        return {
            "beta": result.beta,
            "theta": result.theta,
            "r_squared": result.r_squared,
            "delta_aic_linear": result.delta_aic_linear,
            "delta_aic_power": result.delta_aic_power,
            "delta_aic_exp": result.delta_aic_exp,
            "beta_ci_95": list(result.beta_ci_95),
            "domain": domain,
            "n": result.n,
            "success": result.success,
        }

    # ------------------------------------------------------------------
    # GET /utac/domain/{domain_id}
    # ------------------------------------------------------------------

    def utac_domain(self, domain_id: str) -> dict[str, Any]:
        """Return β-cluster info for a named domain.

        Args:
            domain_id: Domain name (informational/biological/climate/etc.).

        Returns:
            Dict with beta_mean, beta_std, phi_attractor, domains list,
            or error dict if unknown.
        """
        try:
            data = self.registry.get(domain_id)
            data["domain"] = domain_id
            return data
        except KeyError:
            return {
                "error": f"Unknown domain: {domain_id!r}",
                "available": self.registry.all_domains,
            }

    # ------------------------------------------------------------------
    # POST /crep/compute
    # ------------------------------------------------------------------

    def crep_compute(self, signal: list[float]) -> dict[str, Any]:
        """Compute full CREP tensor C, R, E, P, Γ for a time series.

        Args:
            signal: 1-D time series values.

        Returns:
            Dict with C, R, E, P, gamma, governance_level.
        """
        arr = np.asarray(signal, dtype=float)
        score = self.crep_evaluator.evaluate_from_signals(arr)
        gamma = compute_gamma(
            score.coherence, score.resonance, score.emergence, score.poetics
        )
        gov = governance_level(gamma)
        return {
            "C": score.coherence,
            "R": score.resonance,
            "E": score.emergence,
            "P": score.poetics,
            "gamma": gamma,
            "governance_level": gov,
            "n_points": len(arr),
        }

    # ------------------------------------------------------------------
    # GET /vrig/velocity
    # ------------------------------------------------------------------

    def vrig_velocity(
        self,
        params_current: list[float],
        params_prev: list[float],
    ) -> dict[str, Any]:
        """Compute v_RIG for a parameter displacement.

        Args:
            params_current: Current [r, K, sigma] parameter vector.
            params_prev: Previous [r, K, sigma] parameter vector.

        Returns:
            Dict with velocity, regime_change, v_rig_constant_kms.
        """
        p_curr = np.asarray(params_current, dtype=float)
        p_prev = np.asarray(params_prev, dtype=float)
        fim = self.vrig.compute_fisher_information_matrix(
            p_curr, lambda p: float(-0.5 * np.sum(p**2))
        )
        v = self.vrig.compute_velocity(p_curr, p_prev, fim)
        history = self.vrig.velocity_history
        shifts = self.vrig.detect_regime_change(
            np.array(history), threshold_sigma=3.0
        ) if len(history) >= 3 else []
        return {
            "velocity": v,
            "regime_change": len(shifts) > 0,
            "v_rig_constant_kms": self.vrig.v_rig_constant_kms,
            "n_history": len(history),
        }

    # ------------------------------------------------------------------
    # POST /mirror/update
    # ------------------------------------------------------------------

    def mirror_update(self, state: dict[str, Any]) -> dict[str, Any]:
        """Update Mirror-Machine state.

        Args:
            state: Arbitrary state dict from the Mirror-Machine.

        Returns:
            Confirmation dict with updated_keys and cycle_count.
        """
        self._mirror_state.update(state)
        self._cycle_count += 1
        return {
            "status": "updated",
            "updated_keys": list(state.keys()),
            "cycle_count": self._cycle_count,
            "mirror_state_keys": list(self._mirror_state.keys()),
        }

    # ------------------------------------------------------------------
    # GET /genesis/cycle
    # ------------------------------------------------------------------

    def genesis_cycle_status(self) -> dict[str, Any]:
        """Return full GenesisAeon cycle status.

        Returns:
            Dict with cycle phases, counts, and module availability.
        """
        from genesis_os.api.cycle import CYCLE_PHASES
        return {
            "cycle_count": self._cycle_count,
            "phases": CYCLE_PHASES,
            "n_phases": len(CYCLE_PHASES),
            "mirror_state_size": len(self._mirror_state),
            "v_rig_history_len": len(self.vrig.velocity_history),
            "registry_domains": self.registry.all_domains,
        }
