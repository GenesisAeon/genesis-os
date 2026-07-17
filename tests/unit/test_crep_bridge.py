"""Tests für genesis_os.bridge.crep_ts_bridge — Phase B."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from genesis_os.bridge.crep_ts_bridge import CREPTypeScriptBridge
from genesis_os.core.crep import CREPScore


class TestCREPBridgeSchema:
    def test_crep_score_schema_exists(self) -> None:
        schema_path = Path(__file__).parents[2] / "schemas" / "crep_score.schema.json"
        assert schema_path.exists(), "schemas/crep_score.schema.json nicht gefunden"

    def test_crep_score_schema_valid_json(self) -> None:
        schema_path = Path(__file__).parents[2] / "schemas" / "crep_score.schema.json"
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
        required = {"C", "R", "E", "P", "gamma", "formula"}
        assert required.issubset(set(schema.get("required", [])))

    def test_crep_score_schema_fields(self) -> None:
        schema_path = Path(__file__).parents[2] / "schemas" / "crep_score.schema.json"
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
        props = schema.get("properties", {})
        for field in ("C", "R", "E", "P", "gamma", "formula"):
            assert field in props, f"Feld '{field}' fehlt im Schema"


class TestCREPBridgeLocalFallback:
    def _bridge(self) -> CREPTypeScriptBridge:
        return CREPTypeScriptBridge(base_url="http://localhost:9999")

    def test_is_available_returns_false_no_server(self) -> None:
        bridge = self._bridge()
        assert bridge.is_available() is False

    def test_evaluate_remote_fallback_no_server(self) -> None:
        bridge = self._bridge()
        crep = CREPScore(coherence=0.8, resonance=0.7, emergence=0.9, poetics=0.6)
        result = bridge.evaluate_remote(crep)
        assert "gamma" in result
        assert result["source"] == "local_fallback"

    def test_local_fallback_canonical_gamma(self) -> None:
        bridge = self._bridge()
        crep = CREPScore(coherence=0.8, resonance=0.7, emergence=0.9, poetics=0.6)
        result = bridge.evaluate_remote(crep)
        expected = (0.8 * 0.7 * 0.9 * 0.6) ** 0.25
        assert float(result["gamma"]) == pytest.approx(expected, rel=1e-5)

    def test_trikaya_classification_dharmakaya(self) -> None:
        bridge = self._bridge()
        crep = CREPScore(coherence=0.3, resonance=0.3, emergence=0.3, poetics=0.3)
        result = bridge.evaluate_remote(crep)
        assert result["trikaya_phase"] == "dharmakaya"

    def test_trikaya_classification_nirmanakaya(self) -> None:
        bridge = self._bridge()
        crep = CREPScore(coherence=1.0, resonance=1.0, emergence=1.0, poetics=1.0)
        result = bridge.evaluate_remote(crep)
        assert result["trikaya_phase"] == "nirmanakaya"

    def test_trikaya_classify_static(self) -> None:
        assert CREPTypeScriptBridge._classify_trikaya(0.2) == "dharmakaya"
        assert CREPTypeScriptBridge._classify_trikaya(0.6) == "sambhogakaya"
        assert CREPTypeScriptBridge._classify_trikaya(0.9) == "nirmanakaya"

    def test_crep_bridge_schema_validation(self) -> None:
        bridge = self._bridge()
        crep = CREPScore(coherence=0.5, resonance=0.5, emergence=0.5, poetics=0.5)
        result = bridge.evaluate_remote(crep)
        assert isinstance(result["C"], float)
        assert isinstance(result["R"], float)
        assert isinstance(result["gamma"], float)
        assert 0.0 <= float(result["gamma"]) <= 1.0

    def test_close_does_not_raise(self) -> None:
        bridge = self._bridge()
        bridge.close()
