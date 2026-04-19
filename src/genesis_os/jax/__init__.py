"""JAX-accelerated simulation modules for Cycle-3 GPU scaling (Milestone 3.1).

Falls back to NumPy when JAX is not installed.
"""

from genesis_os.jax.cosmic_web_jax import JaxCosmicWebSimulator
from genesis_os.jax.integrator import LeapfrogIntegrator

__all__ = ["JaxCosmicWebSimulator", "LeapfrogIntegrator"]
