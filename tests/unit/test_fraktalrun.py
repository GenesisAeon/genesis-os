"""Tests für genesis_os.runtime.fraktalrun_engine + core.mandala_map — Phase G."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from genesis_os.core.mandala_map import MandalaEdge, MandalaMap
from genesis_os.runtime.fraktalrun_engine import (
    MAX_FRACTAL_DEPTH,
    SIGMA_PHI,
    FraktalNode,
    FraktalRunEngine,
    fractal_activation,
)


class TestFractalActivation:
    def test_activation_at_half(self) -> None:
        """H = 0.5·K, gamma=1.0 → activation ≈ 0.5 (Inflektionspunkt)."""
        activation = fractal_activation(gamma=1.0, H=0.5, K=1.0, theta=0.5)
        assert activation == pytest.approx(0.5, abs=0.01)

    def test_activation_above_threshold(self) -> None:
        """H > Θ·K → activation > 0.5."""
        activation = fractal_activation(gamma=2.0, H=0.8, K=1.0, theta=0.5)
        assert activation > 0.5

    def test_activation_below_threshold(self) -> None:
        """H < Θ·K → activation < 0.5."""
        activation = fractal_activation(gamma=2.0, H=0.2, K=1.0, theta=0.5)
        assert activation < 0.5

    def test_activation_range(self) -> None:
        for H in [0.0, 0.1, 0.5, 0.9, 1.0]:
            a = fractal_activation(gamma=1.0, H=H, K=1.0)
            assert 0.0 < a < 1.0

    def test_sigma_phi_constant(self) -> None:
        assert SIGMA_PHI == pytest.approx(1.0 / 16.0)

    def test_max_depth_is_16(self) -> None:
        assert MAX_FRACTAL_DEPTH == 16


class TestFraktalRunEngine:
    def _state(self, entropy: float = 0.8, gamma: float = 0.9) -> object:
        class FakeCREP:
            pass

        crep = FakeCREP()
        crep.gamma = gamma  # type: ignore[attr-defined]

        class FakeState:
            pass

        state = FakeState()
        state.entropy = entropy  # type: ignore[attr-defined]
        state.crep = crep  # type: ignore[attr-defined]
        return state

    def test_engine_creates_root(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        config = GenesisConfig(entropy=0.4, max_cycles=2, seed=0)
        genesis = GenesisOS(config=config)
        initial = genesis.run()
        engine = FraktalRunEngine(max_depth=2, activation_threshold=0.7)
        root = engine.run(genesis, initial)
        assert isinstance(root, FraktalNode)
        assert root.depth == 0

    def test_depth_limit_respected(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        config = GenesisConfig(entropy=0.8, max_cycles=1, seed=1)
        genesis = GenesisOS(config=config)
        initial = genesis.run()
        engine = FraktalRunEngine(max_depth=2, activation_threshold=0.01)
        engine.run(genesis, initial)
        assert engine.tree_depth <= 2

    def test_tree_depth_zero_if_no_run(self) -> None:
        engine = FraktalRunEngine()
        assert engine.tree_depth == 0

    def test_collect_states(self) -> None:
        from genesis_os.core.orchestrator import GenesisConfig, GenesisOS

        config = GenesisConfig(entropy=0.3, max_cycles=1, seed=2)
        genesis = GenesisOS(config=config)
        initial = genesis.run()
        engine = FraktalRunEngine(max_depth=1, activation_threshold=0.99)
        engine.run(genesis, initial)
        states = engine.collect_states()
        assert len(states) >= 1

    def test_max_depth_capped_at_16(self) -> None:
        engine = FraktalRunEngine(max_depth=100)
        assert engine.max_depth == 16


class TestMandalaMap:
    def test_from_dict(self) -> None:
        data = {
            "nodes": ["genesis-os", "unified-mandala", "crep-bridge"],
            "edges": [
                {"source": "genesis-os", "target": "crep-bridge", "gamma": 0.7},
                {"source": "crep-bridge", "target": "unified-mandala", "gamma": 0.5},
            ],
        }
        mm = MandalaMap.from_dict(data)
        assert len(mm.nodes) == 3
        assert len(mm.edges) == 2

    def test_update_existing_edge(self) -> None:
        data = {
            "nodes": ["A", "B"],
            "edges": [{"source": "A", "target": "B", "gamma": 0.3}],
        }
        mm = MandalaMap.from_dict(data)
        mm.update_edge_weight("A", "B", 0.8)
        edge = mm.get_edge("A", "B")
        assert edge is not None
        assert edge.gamma == pytest.approx(0.8)

    def test_add_new_edge(self) -> None:
        mm = MandalaMap(nodes=["A", "B"])
        mm.update_edge_weight("A", "B", 0.6)
        assert len(mm.edges) == 1
        assert mm.edges[0].gamma == pytest.approx(0.6)

    def test_mean_gamma_empty(self) -> None:
        mm = MandalaMap()
        assert mm.mean_gamma() == pytest.approx(0.0)

    def test_mean_gamma_computed(self) -> None:
        mm = MandalaMap.from_dict(
            {
                "edges": [
                    {"source": "A", "target": "B", "gamma": 0.4},
                    {"source": "B", "target": "C", "gamma": 0.8},
                ]
            }
        )
        assert mm.mean_gamma() == pytest.approx(0.6)

    def test_load_from_yaml(self) -> None:
        yaml_content = """
nodes:
  - genesis-os
  - unified-mandala
edges:
  - source: genesis-os
    target: unified-mandala
    gamma: 0.72
    flow_type: nats
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            tmp = Path(f.name)

        mm = MandalaMap.load(tmp)
        tmp.unlink()

        assert "genesis-os" in mm.nodes
        assert len(mm.edges) == 1
        assert mm.edges[0].gamma == pytest.approx(0.72)
        assert mm.edges[0].flow_type == "nats"

    def test_adjacency_dict(self) -> None:
        mm = MandalaMap.from_dict(
            {
                "edges": [
                    {"source": "A", "target": "B"},
                    {"source": "A", "target": "C"},
                ]
            }
        )
        adj = mm.to_adjacency_dict()
        assert set(adj["A"]) == {"B", "C"}

    def test_get_edge_not_found(self) -> None:
        mm = MandalaMap(nodes=["A", "B"])
        assert mm.get_edge("A", "B") is None
