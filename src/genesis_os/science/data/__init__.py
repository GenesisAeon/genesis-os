"""Empirical datasets placeholder.

The 78 empirical datasets from Feldtheorie are available in the
Feldtheorie repository at science/data/. This package provides
synthetic benchmark data for testing the pipeline locally.
"""
from genesis_os.science.data.synthetic import generate_synthetic_datasets

__all__ = ["generate_synthetic_datasets"]
