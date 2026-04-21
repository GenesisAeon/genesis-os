"""genesis-os API — FastAPI endpoints for UTAC, CREP, v_RIG, and telemetry.

Key endpoints (from Feldtheorie api/server.py port):
    POST /utac/fit          — Fit σ(β(R-Θ)) to a submitted time series
    GET  /utac/domain/{id}  — Get domain β-cluster classification
    POST /crep/compute      — Compute CREP tensor for a time series
    GET  /vrig/velocity     — Get v_RIG velocity for a parameter set
    POST /mirror/update     — Update Mirror-Machine state
    GET  /genesis/cycle     — Full GenesisAeon cycle status
"""

from genesis_os.api.router import GenesisRouter

__all__ = ["GenesisRouter"]
