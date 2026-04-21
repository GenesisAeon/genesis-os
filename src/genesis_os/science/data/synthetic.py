"""Synthetic benchmark datasets for pipeline testing.

Generates synthetic systems with known β values drawn from the empirically
validated domain β-clusters. Used for testing without the full Feldtheorie
data directory.
"""

from __future__ import annotations

import numpy as np

from genesis_os.core.utac_bridge import DOMAIN_BETA


def generate_synthetic_datasets(
    n_per_domain: int = 5,
    n_points: int = 30,
    noise_std: float = 0.05,
    seed: int = 42,
) -> list[dict]:
    """Generate synthetic UTAC logistic datasets for each domain.

    Each dataset has known β drawn from the domain's empirical distribution,
    with additive Gaussian noise.

    Args:
        n_per_domain: Systems to generate per domain (default 5).
        n_points: Data points per system (default 30).
        noise_std: Gaussian noise standard deviation (default 0.05).
        seed: Random seed (default 42).

    Returns:
        List of dicts with keys: ``id``, ``domain``, ``R``, ``response``,
        ``beta_true``, ``theta_true``.
    """
    rng = np.random.default_rng(seed)
    datasets = []
    system_counter = 0

    for domain, params in DOMAIN_BETA.items():
        beta_mean = params["beta_mean"]
        beta_std = params["beta_std"]

        for i in range(n_per_domain):
            beta_true = float(rng.normal(beta_mean, beta_std))
            beta_true = max(0.5, beta_true)
            theta_true = float(rng.uniform(0.3, 0.7))

            R = np.linspace(0.0, 1.0, n_points)
            exponent = np.clip(-beta_true * (R - theta_true), -500.0, 500.0)
            response_clean = 1.0 / (1.0 + np.exp(exponent))
            noise = rng.normal(0, noise_std, n_points)
            response = np.clip(response_clean + noise, 0.0, 1.0)

            datasets.append({
                "id": f"{domain}_{i:02d}",
                "domain": domain,
                "R": R,
                "response": response,
                "beta_true": beta_true,
                "theta_true": theta_true,
                "n_points": n_points,
            })
            system_counter += 1

    return datasets
